import { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import styles from './UserMenu.module.css';

function GoogleIcon() {
  return (
    <svg className={styles.googleIcon} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"
        fill="#a1a1aa"
      />
      <path
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
        fill="#a1a1aa"
      />
      <path
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18A10.96 10.96 0 0 0 1 12c0 1.77.42 3.45 1.18 4.93l3.66-2.84z"
        fill="#a1a1aa"
      />
      <path
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
        fill="#a1a1aa"
      />
    </svg>
  );
}

export function UserMenu() {
  const { t } = useTranslation();
  const { user, isLoggingIn, loginError, login, logout } = useAuth();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const [imgError, setImgError] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const [visibleError, setVisibleError] = useState<string | null>(null);

  useEffect(() => {
    if (!loginError) {
      setVisibleError(null);
      return;
    }
    setVisibleError(loginError);
    const timer = setTimeout(() => setVisibleError(null), 5000);
    return () => clearTimeout(timer);
  }, [loginError]);

  const closeDropdown = () => {
    setIsClosing(true);
    setTimeout(() => {
      setIsDropdownOpen(false);
      setIsClosing(false);
    }, 150);
  };

  const toggleDropdown = () => {
    if (isDropdownOpen) {
      closeDropdown();
    } else {
      setIsDropdownOpen(true);
    }
  };

  const handleSignOut = () => {
    closeDropdown();
    logout();
  };

  // Loading state
  if (isLoggingIn) {
    return (
      <div className={styles.loadingControl}>
        <div className={styles.loadingAvatar} />
        <span className={styles.loadingText}>{t('auth.signingIn')}</span>
        <div className={styles.loadingScanBar} />
      </div>
    );
  }

  // Authenticated state
  if (user) {
    const initial = (user.display_name || user.email)?.[0]?.toUpperCase() || '?';

    return (
      <div className={styles.userControl} ref={dropdownRef}>
        {isDropdownOpen && (
          <div className={styles.backdrop} onClick={closeDropdown} />
        )}
        <button
          className={`${styles.avatarButton} ${isDropdownOpen ? styles.open : ''}`}
          onClick={toggleDropdown}
          aria-label={`${t('auth.signOut')} — ${user.display_name || user.email}`}
        >
          <div className={styles.avatarFrame}>
            {user.avatar_url && !imgError ? (
              <img
                className={styles.avatarImage}
                src={user.avatar_url}
                alt=""
                onError={() => setImgError(true)}
              />
            ) : (
              <div className={styles.avatarFallback}>{initial}</div>
            )}
            <div className={styles.connectedLed} />
          </div>
          <span className={styles.userName}>{user.display_name || user.email}</span>
          <div className={`${styles.chevron} ${isDropdownOpen ? styles.open : ''}`} />
        </button>

        {isDropdownOpen && (
          <div className={`${styles.dropdown} ${isClosing ? styles.closing : ''}`}>
            <div className={styles.dropdownUserInfo}>
              <div className={styles.dropdownName}>{user.display_name || user.email}</div>
              {user.display_name && (
                <div className={styles.dropdownEmail}>{user.email}</div>
              )}
            </div>
            <button className={styles.signOutButton} onClick={handleSignOut}>
              <span className={styles.signOutIcon} />
              {t('auth.signOut')}
            </button>
          </div>
        )}
      </div>
    );
  }

  // Unauthenticated state
  return (
    <div className={styles.userControl}>
      <button className={styles.signInButton} onClick={login}>
        <GoogleIcon />
        {t('auth.signIn')}
      </button>
      {visibleError && (
        <div className={styles.errorMessage}>
          {visibleError === 'popup_blocked' ? t('auth.popupBlocked') : t('auth.loginFailed')}
        </div>
      )}
    </div>
  );
}
