import type { HintType } from '../types/api';

export interface HintMetadata {
  labelKey: string;
  icon: string;
  colorClass: string;
}

export const HINT_CONFIG: Record<HintType, HintMetadata> = {
  stat: {
    labelKey: 'hint.randomStat',
    icon: '📊',
    colorClass: 'hintStat',
  },
  primary_type: {
    labelKey: 'hint.primaryType',
    icon: '🏷️',
    colorClass: 'hintType',
  },
  secondary_type: {
    labelKey: 'hint.secondaryType',
    icon: '🏷️',
    colorClass: 'hintType',
  },
  fully_evolved: {
    labelKey: 'hint.evolutionStatus',
    icon: '⚡',
    colorClass: 'hintEvolution',
  },
  effectiveness: {
    labelKey: 'hint.typeEffectiveness',
    icon: '⚔️',
    colorClass: 'hintEffectiveness',
  },
  moves: {
    labelKey: 'hint.pokemonMoves',
    icon: '💥',
    colorClass: 'hintMoves',
  },
};
