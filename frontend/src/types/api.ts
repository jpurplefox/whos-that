export type Difficulty = 'easy' | 'medium' | 'hard';

export type HintType = 'stat' | 'primary_type' | 'secondary_type' | 'fully_evolved' | 'effectiveness' | 'moves';

export type Comparison = 'higher' | 'lower' | 'equal';

export type Stat = 'hp' | 'attack' | 'defense' | 'sp_attack' | 'sp_defense' | 'speed';

export interface Pokemon {
  id: number;
  name: string;
  image_url: string;
}

export interface AvailableHint {
  type: HintType;
  cost: number | null;
  available: boolean;
}

export interface StatHint {
  type: 'stat';
  stat: Stat;
  value: number;
}

export interface ComparisonHint {
  type: 'comparison';
  pokemon: string;
  comparisons: Record<Stat, Comparison>;
}

export interface PrimaryTypeHint {
  type: 'primary_type';
  primary_type: string;
}

export interface SecondaryTypeHint {
  type: 'secondary_type';
  secondary_type: string | null;
}

export interface FullyEvolvedHint {
  type: 'fully_evolved';
  is_fully_evolved: boolean;
}

export interface EffectivenessHint {
  type: 'effectiveness';
  relation: string;
  element: string | null;
  multiplier: number | null;
}

export interface MoveHint {
  type: 'moves';
  move: string | null;
}

export type Hint = StatHint | ComparisonHint | PrimaryTypeHint | SecondaryTypeHint | FullyEvolvedHint | EffectivenessHint | MoveHint;

export interface GameResponse {
  id: string | null;
  created_at: string | null;
  is_won: boolean;
  is_over: boolean;
  attempts_remaining: number;
  attempts: string[];
  hints: Hint[];
  available_hints: AvailableHint[];
  battery: number;
  max_battery: number;
  battery_recovery: number;
  score: number | null;
  pokemon: Pokemon | null;
}

export interface CreateGameRequest {
  difficulty: Difficulty;
}

export interface GuessRequest {
  pokemon_name: string;
}

export interface ConsultRequest {
  hint_type: HintType;
}
