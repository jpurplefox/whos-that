import '@testing-library/jest-dom';
import './test-utils/i18n.ts';

vi.mock('./services/analytics', () => ({
  initAnalytics: vi.fn(),
  isReturningUser: vi.fn(() => false),
  trackAppOpened: vi.fn(),
  trackGameStarted: vi.fn(),
  trackGuessSubmitted: vi.fn(),
  trackHintPurchased: vi.fn(),
  trackGameEnded: vi.fn(),
  trackPlayAgainClicked: vi.fn(),
}));
