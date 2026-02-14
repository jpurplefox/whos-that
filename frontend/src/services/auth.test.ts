import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { getStoredSession, storeSession, clearSession, getToken, loginWithGoogle } from './auth';
import type { AuthSession } from './auth';

function createJwt(payload: Record<string, unknown>): string {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const body = btoa(JSON.stringify(payload));
  return `${header}.${body}.fake-signature`;
}

const mockUser = {
  user_id: 'u-1',
  email: 'ash@pokemon.com',
  display_name: 'Ash',
  avatar_url: 'https://example.com/ash.png',
};

function validSession(overrides: Partial<{ exp: number }> = {}): AuthSession {
  const exp = overrides.exp ?? Math.floor(Date.now() / 1000) + 3600;
  return { token: createJwt({ exp }), user: mockUser };
}

describe('auth', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  describe('storeSession / clearSession', () => {
    it('stores session in localStorage', () => {
      const session = validSession();
      storeSession(session);

      const raw = localStorage.getItem('whos_that_auth');
      expect(raw).not.toBeNull();
      expect(JSON.parse(raw!)).toEqual(session);
    });

    it('clearSession removes from localStorage', () => {
      storeSession(validSession());
      clearSession();

      expect(localStorage.getItem('whos_that_auth')).toBeNull();
    });
  });

  describe('getStoredSession', () => {
    it('returns null when nothing is stored', () => {
      expect(getStoredSession()).toBeNull();
    });

    it('returns session when token is still valid', () => {
      const session = validSession();
      storeSession(session);

      expect(getStoredSession()).toEqual(session);
    });

    it('returns null and clears when token is expired', () => {
      const expired = validSession({ exp: Math.floor(Date.now() / 1000) - 60 });
      storeSession(expired);

      expect(getStoredSession()).toBeNull();
      expect(localStorage.getItem('whos_that_auth')).toBeNull();
    });

    it('returns null for token without exp claim', () => {
      const session: AuthSession = { token: createJwt({}), user: mockUser };
      storeSession(session);

      expect(getStoredSession()).toBeNull();
    });

    it('returns null for malformed token', () => {
      const session: AuthSession = { token: 'not-a-jwt', user: mockUser };
      storeSession(session);

      expect(getStoredSession()).toBeNull();
    });

    it('returns null and clears on corrupted localStorage value', () => {
      localStorage.setItem('whos_that_auth', '{invalid json');

      expect(getStoredSession()).toBeNull();
      expect(localStorage.getItem('whos_that_auth')).toBeNull();
    });
  });

  describe('getToken', () => {
    it('returns token from a valid stored session', () => {
      const session = validSession();
      storeSession(session);

      expect(getToken()).toBe(session.token);
    });

    it('returns null when no session', () => {
      expect(getToken()).toBeNull();
    });
  });

  describe('loginWithGoogle', () => {
    let fetchMock: ReturnType<typeof vi.fn>;

    beforeEach(() => {
      fetchMock = vi.fn();
      global.fetch = fetchMock;
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it('throws login_failed when /auth/google/url fails', async () => {
      fetchMock.mockResolvedValueOnce({ ok: false });

      await expect(loginWithGoogle()).rejects.toThrow('login_failed');
    });

    it('throws popup_blocked when window.open returns null', async () => {
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ url: 'https://accounts.google.com/auth' }),
      });
      vi.spyOn(window, 'open').mockReturnValue(null);

      await expect(loginWithGoogle()).rejects.toThrow('popup_blocked');
    });

    it('throws login_cancelled when popup is closed before callback', async () => {
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ url: 'https://accounts.google.com/auth' }),
      });

      const fakePopup = { closed: false, close: vi.fn() };
      vi.spyOn(window, 'open').mockReturnValue(fakePopup as unknown as Window);

      const promise = loginWithGoogle();
      // Attach rejection handler BEFORE advancing timers to avoid unhandled rejection
      const assertion = expect(promise).rejects.toThrow('login_cancelled');

      fakePopup.closed = true;
      await vi.advanceTimersByTimeAsync(500);

      await assertion;
    });

    it('resolves with session on successful OAuth callback', async () => {
      const callbackResponse = {
        token: createJwt({ exp: Math.floor(Date.now() / 1000) + 3600 }),
        ...mockUser,
      };

      fetchMock
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ url: 'https://accounts.google.com/auth' }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => callbackResponse,
        });

      const fakePopup = { closed: false, close: vi.fn() };
      vi.spyOn(window, 'open').mockReturnValue(fakePopup as unknown as Window);

      const promise = loginWithGoogle();

      // Flush microtasks so loginWithGoogle gets past the initial await fetch()
      // and sets up the message listener
      await vi.advanceTimersByTimeAsync(0);

      window.dispatchEvent(new MessageEvent('message', {
        origin: window.location.origin,
        data: { type: 'oauth_callback', code: 'auth-code', state: 'state-123' },
      }));

      // Flush the fetch .then chain from handleMessage
      await vi.advanceTimersByTimeAsync(0);

      const session = await promise;

      expect(session.token).toBe(callbackResponse.token);
      expect(session.user).toEqual(mockUser);
      expect(fetchMock).toHaveBeenCalledWith('/api/auth/google/callback', expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ code: 'auth-code', state: 'state-123' }),
      }));
    });

    it('throws login_failed when callback API returns non-ok', async () => {
      fetchMock
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ url: 'https://accounts.google.com/auth' }),
        })
        .mockResolvedValueOnce({ ok: false });

      const fakePopup = { closed: false, close: vi.fn() };
      vi.spyOn(window, 'open').mockReturnValue(fakePopup as unknown as Window);

      const promise = loginWithGoogle();
      const assertion = expect(promise).rejects.toThrow('login_failed');

      await vi.advanceTimersByTimeAsync(0);

      window.dispatchEvent(new MessageEvent('message', {
        origin: window.location.origin,
        data: { type: 'oauth_callback', code: 'code', state: 'state' },
      }));

      await vi.advanceTimersByTimeAsync(0);

      await assertion;
    });

    it('ignores messages from different origins', async () => {
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ url: 'https://accounts.google.com/auth' }),
      });

      const fakePopup = { closed: false, close: vi.fn() };
      vi.spyOn(window, 'open').mockReturnValue(fakePopup as unknown as Window);

      const promise = loginWithGoogle();
      const assertion = expect(promise).rejects.toThrow('login_cancelled');

      // Message from wrong origin — should be ignored
      window.dispatchEvent(new MessageEvent('message', {
        origin: 'https://evil.com',
        data: { type: 'oauth_callback', code: 'code', state: 'state' },
      }));

      // Close popup to resolve
      fakePopup.closed = true;
      await vi.advanceTimersByTimeAsync(500);

      await assertion;
    });

    it('ignores messages with wrong type', async () => {
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ url: 'https://accounts.google.com/auth' }),
      });

      const fakePopup = { closed: false, close: vi.fn() };
      vi.spyOn(window, 'open').mockReturnValue(fakePopup as unknown as Window);

      const promise = loginWithGoogle();
      const assertion = expect(promise).rejects.toThrow('login_cancelled');

      window.dispatchEvent(new MessageEvent('message', {
        origin: window.location.origin,
        data: { type: 'some_other_event' },
      }));

      fakePopup.closed = true;
      await vi.advanceTimersByTimeAsync(500);

      await assertion;
    });

    it('throws login_timeout after 5 minutes', async () => {
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ url: 'https://accounts.google.com/auth' }),
      });

      const fakePopup = { closed: false, close: vi.fn() };
      vi.spyOn(window, 'open').mockReturnValue(fakePopup as unknown as Window);

      const promise = loginWithGoogle();
      const assertion = expect(promise).rejects.toThrow('login_timeout');

      await vi.advanceTimersByTimeAsync(5 * 60 * 1000);

      await assertion;
      expect(fakePopup.close).toHaveBeenCalled();
    });
  });
});
