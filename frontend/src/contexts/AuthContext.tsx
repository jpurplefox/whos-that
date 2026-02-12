import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { ReactNode } from 'react';
import type { AuthUser } from '../services/auth';
import { getStoredSession, loginWithGoogle, clearSession as clearAuthSession } from '../services/auth';
import { setUserId, resetUserId, trackLoginCompleted, trackLogout } from '../services/analytics';

interface AuthContextValue {
  user: AuthUser | null;
  isLoggingIn: boolean;
  loginError: string | null;
  login: () => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => {
    return getStoredSession()?.user ?? null;
  });
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [loginError, setLoginError] = useState<string | null>(null);

  useEffect(() => {
    const handleExpired = () => {
      resetUserId();
      setUser(null);
    };
    window.addEventListener('auth:session_expired', handleExpired);
    return () => window.removeEventListener('auth:session_expired', handleExpired);
  }, []);

  useEffect(() => {
    if (user) {
      setUserId(user.user_id);
    }
  }, []);

  const login = useCallback(async () => {
    setIsLoggingIn(true);
    setLoginError(null);
    try {
      const session = await loginWithGoogle();
      setUser(session.user);
      setUserId(session.user.user_id);
      trackLoginCompleted({ provider: 'google', user_id: session.user.user_id });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'login_failed';
      if (message !== 'login_cancelled') {
        setLoginError(message);
      }
    } finally {
      setIsLoggingIn(false);
    }
  }, []);

  const logout = useCallback(() => {
    if (user) {
      trackLogout({ user_id: user.user_id });
      resetUserId();
    }
    clearAuthSession();
    setUser(null);
    setLoginError(null);
  }, [user]);

  return (
    <AuthContext.Provider value={{ user, isLoggingIn, loginError, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
