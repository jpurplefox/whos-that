import type { HintType } from '../types/api';

export interface HintMetadata {
  label: string;
  icon: string;
  colorClass: string;
}

export const HINT_CONFIG: Record<HintType, HintMetadata> = {
  stat: {
    label: 'Random Stat',
    icon: '📊',
    colorClass: 'hintStat',
  },
  primary_type: {
    label: 'Primary Type',
    icon: '🏷️',
    colorClass: 'hintType',
  },
  secondary_type: {
    label: 'Secondary Type',
    icon: '🏷️',
    colorClass: 'hintType',
  },
  fully_evolved: {
    label: 'Evolution Status',
    icon: '⚡',
    colorClass: 'hintEvolution',
  },
  effectiveness: {
    label: 'Type Effectiveness',
    icon: '⚔️',
    colorClass: 'hintEffectiveness',
  },
};
