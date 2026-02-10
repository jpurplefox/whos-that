import * as amplitude from '@amplitude/analytics-browser';
import type {
  AppOpenedProperties,
  GameStartedProperties,
  GuessSubmittedProperties,
  HintPurchasedProperties,
  GameEndedProperties,
  PlayAgainClickedProperties,
} from '../types/analytics';

const DEVICE_ID_KEY = 'whos_that_device_id';

let initialized = false;
let returningUser = false;

export function initAnalytics(): void {
  const apiKey = import.meta.env.VITE_AMPLITUDE_API_KEY as string | undefined;
  if (!apiKey) return;

  returningUser = localStorage.getItem(DEVICE_ID_KEY) !== null;

  let deviceId = localStorage.getItem(DEVICE_ID_KEY);
  if (!deviceId) {
    deviceId = crypto.randomUUID();
    localStorage.setItem(DEVICE_ID_KEY, deviceId);
  }

  amplitude.init(apiKey, {
    deviceId,
    defaultTracking: false,
  });

  initialized = true;
}

export function isReturningUser(): boolean {
  return returningUser;
}

export function trackAppOpened(properties: AppOpenedProperties): void {
  if (!initialized) return;
  amplitude.track('App Opened', properties);
}

export function trackGameStarted(properties: GameStartedProperties): void {
  if (!initialized) return;
  amplitude.track('Game Started', properties);
}

export function trackGuessSubmitted(properties: GuessSubmittedProperties): void {
  if (!initialized) return;
  amplitude.track('Guess Submitted', properties);
}

export function trackHintPurchased(properties: HintPurchasedProperties): void {
  if (!initialized) return;
  amplitude.track('Hint Purchased', properties);
}

export function trackGameEnded(properties: GameEndedProperties): void {
  if (!initialized) return;
  amplitude.track('Game Ended', properties);
}

export function trackPlayAgainClicked(properties: PlayAgainClickedProperties): void {
  if (!initialized) return;
  amplitude.track('Play Again Clicked', properties);
}
