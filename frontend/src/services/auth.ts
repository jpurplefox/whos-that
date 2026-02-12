const AUTH_STORAGE_KEY = 'whos_that_auth';
const API_BASE = '/api';

export interface AuthUser {
  user_id: string;
  email: string;
  display_name: string | null;
  avatar_url: string | null;
}

export interface AuthSession {
  token: string;
  user: AuthUser;
}

function decodeJwtPayload(token: string): { exp?: number } {
  try {
    const base64Url = token.split('.')[1];
    if (!base64Url) return {};
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), '=');
    const binary = atob(padded);
    const bytes = Uint8Array.from(binary, (c) => c.charCodeAt(0));
    return JSON.parse(new TextDecoder().decode(bytes));
  } catch {
    return {};
  }
}

function isTokenExpired(token: string): boolean {
  const { exp } = decodeJwtPayload(token);
  if (!exp) return true;
  return Date.now() / 1000 > exp;
}

export function getStoredSession(): AuthSession | null {
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY);
    if (!raw) return null;
    const session: AuthSession = JSON.parse(raw);
    if (isTokenExpired(session.token)) {
      clearSession();
      return null;
    }
    return session;
  } catch {
    clearSession();
    return null;
  }
}

export function storeSession(session: AuthSession): void {
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(session));
}

export function clearSession(): void {
  localStorage.removeItem(AUTH_STORAGE_KEY);
}

export function getToken(): string | null {
  return getStoredSession()?.token ?? null;
}

export async function loginWithGoogle(): Promise<AuthSession> {
  const urlResponse = await fetch(`${API_BASE}/auth/google/url`);
  if (!urlResponse.ok) {
    throw new Error('login_failed');
  }
  const { url } = await urlResponse.json();

  const width = 500;
  const height = 600;
  const left = window.screenX + (window.outerWidth - width) / 2;
  const top = window.screenY + (window.outerHeight - height) / 2;
  const features = `width=${width},height=${height},left=${left},top=${top},toolbar=no,menubar=no`;

  const popup = window.open(url, 'google-login', features);
  if (!popup) {
    throw new Error('popup_blocked');
  }

  return new Promise<AuthSession>((resolve, reject) => {
    const TIMEOUT_MS = 5 * 60 * 1000;

    const pollInterval = setInterval(() => {
      if (popup.closed) {
        cleanup();
        reject(new Error('login_cancelled'));
      }
    }, 500);

    const timeoutId = setTimeout(() => {
      popup.close();
      cleanup();
      reject(new Error('login_timeout'));
    }, TIMEOUT_MS);

    function handleMessage(event: MessageEvent) {
      if (event.origin !== window.location.origin) return;
      if (event.data?.type !== 'oauth_callback') return;

      const { code, state } = event.data;
      cleanup();

      fetch(`${API_BASE}/auth/google/callback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, state }),
      })
        .then((res) => {
          if (!res.ok) throw new Error('login_failed');
          return res.json();
        })
        .then((data) => {
          const session: AuthSession = {
            token: data.token,
            user: {
              user_id: data.user_id,
              email: data.email,
              display_name: data.display_name,
              avatar_url: data.avatar_url,
            },
          };
          storeSession(session);
          resolve(session);
        })
        .catch(() => reject(new Error('login_failed')));
    }

    function cleanup() {
      clearInterval(pollInterval);
      clearTimeout(timeoutId);
      window.removeEventListener('message', handleMessage);
    }

    window.addEventListener('message', handleMessage);
  });
}
