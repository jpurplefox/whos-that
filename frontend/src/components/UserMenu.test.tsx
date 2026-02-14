import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UserMenu } from './UserMenu';

const mockLogin = vi.fn();
const mockLogout = vi.fn();

vi.mock('../contexts/AuthContext', () => ({
  useAuth: vi.fn(),
}));

import { useAuth } from '../contexts/AuthContext';

const authenticatedUser = {
  user_id: 'u-1',
  email: 'ash@pokemon.com',
  display_name: 'Ash Ketchum',
  avatar_url: 'https://example.com/ash.png',
};

function mockAuthState(overrides: Partial<ReturnType<typeof useAuth>> = {}) {
  vi.mocked(useAuth).mockReturnValue({
    user: null,
    isLoggingIn: false,
    loginError: null,
    login: mockLogin,
    logout: mockLogout,
    ...overrides,
  });
}

describe('UserMenu', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.useFakeTimers({ shouldAdvanceTime: true });
  });

  describe('unauthenticated state', () => {
    it('renders sign in button', () => {
      mockAuthState();
      render(<UserMenu />);

      expect(screen.getByText('Sign in')).toBeInTheDocument();
    });

    it('calls login on sign in click', async () => {
      mockAuthState();
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      render(<UserMenu />);

      await user.click(screen.getByText('Sign in'));

      expect(mockLogin).toHaveBeenCalledOnce();
    });
  });

  describe('loading state', () => {
    it('renders loading text when logging in', () => {
      mockAuthState({ isLoggingIn: true });
      render(<UserMenu />);

      expect(screen.getByText('Linking...')).toBeInTheDocument();
      expect(screen.queryByText('Sign in')).not.toBeInTheDocument();
    });
  });

  describe('authenticated state', () => {
    it('renders user display name', () => {
      mockAuthState({ user: authenticatedUser });
      render(<UserMenu />);

      expect(screen.getByText('Ash Ketchum')).toBeInTheDocument();
    });

    it('renders avatar image', () => {
      mockAuthState({ user: authenticatedUser });
      const { container } = render(<UserMenu />);

      const img = container.querySelector('img');
      expect(img).toHaveAttribute('src', 'https://example.com/ash.png');
    });

    it('shows fallback initial when no avatar_url', () => {
      mockAuthState({ user: { ...authenticatedUser, avatar_url: null } });
      render(<UserMenu />);

      expect(screen.getByText('A')).toBeInTheDocument();
    });

    it('shows email initial when no display_name', () => {
      mockAuthState({ user: { ...authenticatedUser, display_name: null, avatar_url: null } });
      render(<UserMenu />);

      expect(screen.getByText('A')).toBeInTheDocument(); // 'a' from ash@...
      expect(screen.getByText('ash@pokemon.com')).toBeInTheDocument();
    });

    it('opens dropdown on avatar click', async () => {
      mockAuthState({ user: authenticatedUser });
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      render(<UserMenu />);

      await user.click(screen.getByRole('button', { name: /Ash Ketchum/ }));

      expect(screen.getByText('Sign out')).toBeInTheDocument();
      expect(screen.getByText('ash@pokemon.com')).toBeInTheDocument();
    });

    it('calls logout on sign out click', async () => {
      mockAuthState({ user: authenticatedUser });
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      render(<UserMenu />);

      await user.click(screen.getByRole('button', { name: /Ash Ketchum/ }));
      await user.click(screen.getByText('Sign out'));

      expect(mockLogout).toHaveBeenCalledOnce();
    });

    it('shows fallback initial when image fails to load', () => {
      mockAuthState({ user: authenticatedUser });
      const { container } = render(<UserMenu />);

      const img = container.querySelector('img')!;
      act(() => { img.dispatchEvent(new Event('error', { bubbles: true })); });

      expect(screen.getByText('A')).toBeInTheDocument();
    });
  });

  describe('error messages', () => {
    it('shows popup blocked message', () => {
      mockAuthState({ loginError: 'popup_blocked' });
      render(<UserMenu />);

      expect(screen.getByText('Please allow popups for this site')).toBeInTheDocument();
    });

    it('shows generic error for other failures', () => {
      mockAuthState({ loginError: 'login_failed' });
      render(<UserMenu />);

      expect(screen.getByText('Login failed. Please try again.')).toBeInTheDocument();
    });

    it('auto-hides error after 5 seconds', () => {
      mockAuthState({ loginError: 'login_failed' });
      render(<UserMenu />);

      expect(screen.getByText('Login failed. Please try again.')).toBeInTheDocument();

      act(() => { vi.advanceTimersByTime(5000); });

      expect(screen.queryByText('Login failed. Please try again.')).not.toBeInTheDocument();
    });
  });
});
