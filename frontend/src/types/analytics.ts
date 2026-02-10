import type { Difficulty, HintType } from './api';

export interface AppOpenedProperties {
  language: string;
  referrer: string;
  is_returning_user: boolean;
}

export interface GameStartedProperties {
  difficulty: Difficulty;
  game_id: string;
  initial_battery: number;
  max_attempts: number;
  session_game_number: number;
}

export interface GuessSubmittedProperties {
  game_id: string;
  difficulty: Difficulty;
  guessed_pokemon: string;
  is_correct: boolean;
  attempt_number: number;
  battery_remaining: number;
  hints_used_count: number;
  time_since_game_start: number;
}

export interface HintPurchasedProperties {
  game_id: string;
  difficulty: Difficulty;
  hint_type: HintType;
  hint_cost: number;
  battery_before: number;
  battery_after: number;
  attempt_number: number;
  hints_already_purchased: number;
}

export interface GameEndedProperties {
  game_id: string;
  difficulty: Difficulty;
  result: 'won' | 'lost';
  score: number;
  total_attempts_used: number;
  battery_remaining: number;
  hints_purchased_count: number;
  hint_types_purchased: HintType[];
  game_duration_seconds: number;
  target_pokemon_name: string;
}

export interface PlayAgainClickedProperties {
  previous_game_id: string;
  previous_result: 'won' | 'lost';
  previous_score: number;
  previous_difficulty: Difficulty;
  games_played_this_session: number;
}
