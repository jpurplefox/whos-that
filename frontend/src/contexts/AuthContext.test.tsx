import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider, useAuth } from './AuthContext';

vi.mock('../services/auth', () => ({
  getStoredSession: vi.fn(() => null),
  loginWithGoogle: vi.fn(),
  clearSession: vi.fn(),
}));

import { getStoredSession, loginWithGoogle, clearSession } from '../services/auth';
import { setUserId, resetUserId, trackLoginCompleted, trackLogout } from '../services/analytics';

const mockUser = {
  user_id: 'u-1',
  email: 'ash@pokemon.com',
  display_name: 'Ash',
  avatar_url: null,
};

function TestConsumer() {
  const { user, isLoggingIn, loginError, login, logout } = useAuth();
  return (
    <div>
      <span data-testid="user">{user ? user.display_name : 'none'}</span>
      <span data-testid="logging-in">{String(isLoggingIn)}</span>
      <span data-testid="error">{loginError ?? 'none'}</span>
      <button onClick={login}>login</button>
      <button onClick={logout}>logout</button>
    </div>
  );
}

describe('AuthContext', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.mocked(getStoredSession).mockReturnValue(null);
  });

  it('initializes user from stored session', () => {
    vi.mocked(getStoredSession).mockReturnValue({ token: 'tok', user: mockUser });

    render(
      <AuthProvider><TestConsumer /></AuthProvider>
    );

    expect(screen.getByTestId('user')).toHaveTextContent('Ash');
  });

  it('initializes with null user when no session', () => {
    render(
      <AuthProvider><TestConsumer /></AuthProvider>
    );

    expect(screen.getByTestId('user')).toHaveTextContent('none');
  });

  it('calls setUserId on mount when user exists', () => {
    vi.mocked(getStoredSession).mockReturnValue({ token: 'tok', user: mockUser });

    render(
      <AuthProvider><TestConsumer /></AuthProvider>
    );

    expect(setUserId).toHaveBeenCalledWith('u-1');
  });

  it('does not call setUserId on mount when no user', () => {
    render(
      <AuthProvider><TestConsumer /></AuthProvider>
    );

    expect(setUserId).not.toHaveBeenCalled();
  });

  describe('login', () => {
    it('sets isLoggingIn during login and updates user on success', async () => {
      const session = { token: 'tok', user: mockUser };
      let resolveLogin!: (val: typeof session) => void;
      vi.mocked(loginWithGoogle).mockImplementation(
        () => new Promise((r) => { resolveLogin = r; })
      );

      const user = userEvent.setup();
      render(
        <AuthProvider><TestConsumer /></AuthProvider>
      );

      await user.click(screen.getByText('login'));
      expect(screen.getByTestId('logging-in')).toHaveTextContent('true');

      await act(async () => resolveLogin(session));

      expect(screen.getByTestId('logging-in')).toHaveTextContent('false');
      expect(screen.getByTestId('user')).toHaveTextContent('Ash');
    });

    it('tracks analytics on successful login', async () => {
      const session = { token: 'tok', user: mockUser };
      vi.mocked(loginWithGoogle).mockResolvedValue(session);

      const user = userEvent.setup();
      render(
        <AuthProvider><TestConsumer /></AuthProvider>
      );

      await user.click(screen.getByText('login'));

      expect(setUserId).toHaveBeenCalledWith('u-1');
      expect(trackLoginCompleted).toHaveBeenCalledWith({ provider: 'google', user_id: 'u-1' });
    });

    it('sets loginError on failure (not login_cancelled)', async () => {
      vi.mocked(loginWithGoogle).mockRejectedValue(new Error('popup_blocked'));

      const user = userEvent.setup();
      render(
        <AuthProvider><TestConsumer /></AuthProvider>
      );

      await user.click(screen.getByText('login'));

      expect(screen.getByTestId('error')).toHaveTextContent('popup_blocked');
      expect(screen.getByTestId('logging-in')).toHaveTextContent('false');
    });

    it('does not set loginError for login_cancelled', async () => {
      vi.mocked(loginWithGoogle).mockRejectedValue(new Error('login_cancelled'));

      const user = userEvent.setup();
      render(
        <AuthProvider><TestConsumer /></AuthProvider>
      );

      await user.click(screen.getByText('login'));

      expect(screen.getByTestId('error')).toHaveTextContent('none');
    });
  });

  describe('logout', () => {
    it('clears user and session on logout', async () => {
      vi.mocked(getStoredSession).mockReturnValue({ token: 'tok', user: mockUser });

      const user = userEvent.setup();
      render(
        <AuthProvider><TestConsumer /></AuthProvider>
      );

      expect(screen.getByTestId('user')).toHaveTextContent('Ash');

      await user.click(screen.getByText('logout'));

      expect(screen.getByTestId('user')).toHaveTextContent('none');
      expect(clearSession).toHaveBeenCalled();
    });

    it('tracks analytics on logout', async () => {
      vi.mocked(getStoredSession).mockReturnValue({ token: 'tok', user: mockUser });

      const user = userEvent.setup();
      render(
        <AuthProvider><TestConsumer /></AuthProvider>
      );

      await user.click(screen.getByText('logout'));

      expect(trackLogout).toHaveBeenCalledWith({ user_id: 'u-1' });
      expect(resetUserId).toHaveBeenCalled();
    });
  });

  describe('session expired event', () => {
    it('resets user when auth:session_expired fires', async () => {
      vi.mocked(getStoredSession).mockReturnValue({ token: 'tok', user: mockUser });

      render(
        <AuthProvider><TestConsumer /></AuthProvider>
      );

      expect(screen.getByTestId('user')).toHaveTextContent('Ash');

      act(() => {
        window.dispatchEvent(new CustomEvent('auth:session_expired'));
      });

      expect(screen.getByTestId('user')).toHaveTextContent('none');
      expect(resetUserId).toHaveBeenCalled();
    });
  });

  describe('useAuth outside provider', () => {
    it('throws when used outside AuthProvider', () => {
      const spy = vi.spyOn(console, 'error').mockImplementation(() => {});

      expect(() => render(<TestConsumer />)).toThrow(
        'useAuth must be used within an AuthProvider'
      );

      spy.mockRestore();
    });
  });
});
