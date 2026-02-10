import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.unmock('./analytics');

vi.mock('@amplitude/analytics-browser', () => ({
  init: vi.fn(),
  track: vi.fn(),
}));

const mockLocalStorage = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] ?? null),
    setItem: vi.fn((key: string, value: string) => { store[key] = value; }),
    removeItem: vi.fn((key: string) => { delete store[key]; }),
    clear: vi.fn(() => { store = {}; }),
  };
})();

Object.defineProperty(globalThis, 'localStorage', { value: mockLocalStorage });

async function freshModules() {
  vi.resetModules();
  const amplitude = await import('@amplitude/analytics-browser');
  const analytics = await import('./analytics');
  return { amplitude, analytics };
}

describe('analytics', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockLocalStorage.clear();
  });

  describe('initAnalytics', () => {
    it('does nothing without API key', async () => {
      vi.stubEnv('VITE_AMPLITUDE_API_KEY', '');
      const { amplitude, analytics } = await freshModules();

      analytics.initAnalytics();

      expect(amplitude.init).not.toHaveBeenCalled();
    });

    it('initializes amplitude with API key and new device ID', async () => {
      vi.stubEnv('VITE_AMPLITUDE_API_KEY', 'test-key');
      const { amplitude, analytics } = await freshModules();

      analytics.initAnalytics();

      expect(amplitude.init).toHaveBeenCalledWith('test-key', {
        deviceId: expect.any(String),
        defaultTracking: false,
      });
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'whos_that_device_id',
        expect.any(String),
      );
    });

    it('reuses existing device ID from localStorage', async () => {
      vi.stubEnv('VITE_AMPLITUDE_API_KEY', 'test-key');
      mockLocalStorage.setItem('whos_that_device_id', 'existing-id');
      vi.mocked(mockLocalStorage.getItem).mockImplementation((key: string) =>
        key === 'whos_that_device_id' ? 'existing-id' : null,
      );

      const { amplitude, analytics } = await freshModules();
      analytics.initAnalytics();

      expect(amplitude.init).toHaveBeenCalledWith('test-key', {
        deviceId: 'existing-id',
        defaultTracking: false,
      });
    });

    it('detects returning user when device ID exists', async () => {
      vi.stubEnv('VITE_AMPLITUDE_API_KEY', 'test-key');
      vi.mocked(mockLocalStorage.getItem).mockImplementation((key: string) =>
        key === 'whos_that_device_id' ? 'existing-id' : null,
      );

      const { analytics } = await freshModules();
      analytics.initAnalytics();

      expect(analytics.isReturningUser()).toBe(true);
    });

    it('detects new user when no device ID exists', async () => {
      vi.stubEnv('VITE_AMPLITUDE_API_KEY', 'test-key');
      vi.mocked(mockLocalStorage.getItem).mockReturnValue(null);

      const { analytics } = await freshModules();
      analytics.initAnalytics();

      expect(analytics.isReturningUser()).toBe(false);
    });
  });

  describe('track functions no-op without init', () => {
    it('trackAppOpened does nothing', async () => {
      const { amplitude, analytics } = await freshModules();
      analytics.trackAppOpened({ language: 'en', referrer: '', is_returning_user: false });
      expect(amplitude.track).not.toHaveBeenCalled();
    });

    it('trackGameStarted does nothing', async () => {
      const { amplitude, analytics } = await freshModules();
      analytics.trackGameStarted({
        difficulty: 'easy', game_id: '1', initial_battery: 100,
        max_attempts: 5, session_game_number: 1,
      });
      expect(amplitude.track).not.toHaveBeenCalled();
    });

    it('trackGuessSubmitted does nothing', async () => {
      const { amplitude, analytics } = await freshModules();
      analytics.trackGuessSubmitted({
        game_id: '1', difficulty: 'easy', guessed_pokemon: 'pikachu',
        is_correct: false, attempt_number: 1, battery_remaining: 90,
        hints_used_count: 0, time_since_game_start: 10,
      });
      expect(amplitude.track).not.toHaveBeenCalled();
    });

    it('trackHintPurchased does nothing', async () => {
      const { amplitude, analytics } = await freshModules();
      analytics.trackHintPurchased({
        game_id: '1', difficulty: 'easy', hint_type: 'stat',
        hint_cost: 10, battery_before: 100, battery_after: 90,
        attempt_number: 0, hints_already_purchased: 0,
      });
      expect(amplitude.track).not.toHaveBeenCalled();
    });

    it('trackGameEnded does nothing', async () => {
      const { amplitude, analytics } = await freshModules();
      analytics.trackGameEnded({
        game_id: '1', difficulty: 'easy', result: 'won', score: 100,
        total_attempts_used: 3, battery_remaining: 50,
        hints_purchased_count: 2, hint_types_purchased: ['stat', 'primary_type'],
        game_duration_seconds: 60, target_pokemon_name: 'pikachu',
      });
      expect(amplitude.track).not.toHaveBeenCalled();
    });

    it('trackPlayAgainClicked does nothing', async () => {
      const { amplitude, analytics } = await freshModules();
      analytics.trackPlayAgainClicked({
        previous_game_id: '1', previous_result: 'won',
        previous_score: 100, previous_difficulty: 'easy',
        games_played_this_session: 1,
      });
      expect(amplitude.track).not.toHaveBeenCalled();
    });
  });

  describe('track functions delegate to amplitude after init', () => {
    it('trackAppOpened sends correct event', async () => {
      vi.stubEnv('VITE_AMPLITUDE_API_KEY', 'test-key');
      const { amplitude, analytics } = await freshModules();
      analytics.initAnalytics();

      const props = { language: 'en', referrer: 'google.com', is_returning_user: true };
      analytics.trackAppOpened(props);

      expect(amplitude.track).toHaveBeenCalledWith('App Opened', props);
    });

    it('trackGameStarted sends correct event', async () => {
      vi.stubEnv('VITE_AMPLITUDE_API_KEY', 'test-key');
      const { amplitude, analytics } = await freshModules();
      analytics.initAnalytics();

      const props = {
        difficulty: 'hard' as const, game_id: 'g1', initial_battery: 100,
        max_attempts: 5, session_game_number: 2,
      };
      analytics.trackGameStarted(props);

      expect(amplitude.track).toHaveBeenCalledWith('Game Started', props);
    });

    it('trackGuessSubmitted sends correct event', async () => {
      vi.stubEnv('VITE_AMPLITUDE_API_KEY', 'test-key');
      const { amplitude, analytics } = await freshModules();
      analytics.initAnalytics();

      const props = {
        game_id: 'g1', difficulty: 'medium' as const, guessed_pokemon: 'bulbasaur',
        is_correct: true, attempt_number: 2, battery_remaining: 80,
        hints_used_count: 1, time_since_game_start: 30,
      };
      analytics.trackGuessSubmitted(props);

      expect(amplitude.track).toHaveBeenCalledWith('Guess Submitted', props);
    });

    it('trackHintPurchased sends correct event', async () => {
      vi.stubEnv('VITE_AMPLITUDE_API_KEY', 'test-key');
      const { amplitude, analytics } = await freshModules();
      analytics.initAnalytics();

      const props = {
        game_id: 'g1', difficulty: 'easy' as const, hint_type: 'primary_type' as const,
        hint_cost: 15, battery_before: 100, battery_after: 85,
        attempt_number: 1, hints_already_purchased: 0,
      };
      analytics.trackHintPurchased(props);

      expect(amplitude.track).toHaveBeenCalledWith('Hint Purchased', props);
    });

    it('trackGameEnded sends correct event', async () => {
      vi.stubEnv('VITE_AMPLITUDE_API_KEY', 'test-key');
      const { amplitude, analytics } = await freshModules();
      analytics.initAnalytics();

      const props = {
        game_id: 'g1', difficulty: 'hard' as const, result: 'lost' as const,
        score: 0, total_attempts_used: 5, battery_remaining: 10,
        hints_purchased_count: 3, hint_types_purchased: ['stat' as const, 'primary_type' as const],
        game_duration_seconds: 120, target_pokemon_name: 'mewtwo',
      };
      analytics.trackGameEnded(props);

      expect(amplitude.track).toHaveBeenCalledWith('Game Ended', props);
    });

    it('trackPlayAgainClicked sends correct event', async () => {
      vi.stubEnv('VITE_AMPLITUDE_API_KEY', 'test-key');
      const { amplitude, analytics } = await freshModules();
      analytics.initAnalytics();

      const props = {
        previous_game_id: 'g1', previous_result: 'won' as const,
        previous_score: 250, previous_difficulty: 'medium' as const,
        games_played_this_session: 3,
      };
      analytics.trackPlayAgainClicked(props);

      expect(amplitude.track).toHaveBeenCalledWith('Play Again Clicked', props);
    });
  });
});
