import { describe, it, expect } from 'vitest';
import { HINT_CONFIG } from './hintConfig';
import type { HintType } from '../types/api';

describe('hintConfig', () => {
  const allHintTypes: HintType[] = ['stat', 'primary_type', 'secondary_type', 'fully_evolved', 'effectiveness', 'moves'];

  it('has entries for all HintType keys', () => {
    allHintTypes.forEach((hintType) => {
      expect(HINT_CONFIG[hintType]).toBeDefined();
    });
  });

  it('each entry has labelKey defined', () => {
    allHintTypes.forEach((hintType) => {
      expect(HINT_CONFIG[hintType].labelKey).toBeDefined();
      expect(typeof HINT_CONFIG[hintType].labelKey).toBe('string');
      expect(HINT_CONFIG[hintType].labelKey.length).toBeGreaterThan(0);
    });
  });

  it('each entry has icon defined', () => {
    allHintTypes.forEach((hintType) => {
      expect(HINT_CONFIG[hintType].icon).toBeDefined();
      expect(typeof HINT_CONFIG[hintType].icon).toBe('string');
      expect(HINT_CONFIG[hintType].icon.length).toBeGreaterThan(0);
    });
  });

  it('each entry has colorClass defined', () => {
    allHintTypes.forEach((hintType) => {
      expect(HINT_CONFIG[hintType].colorClass).toBeDefined();
      expect(typeof HINT_CONFIG[hintType].colorClass).toBe('string');
      expect(HINT_CONFIG[hintType].colorClass.length).toBeGreaterThan(0);
    });
  });

  it('has correct metadata for stat hint', () => {
    expect(HINT_CONFIG.stat).toEqual({
      labelKey: 'hint.randomStat',
      icon: '📊',
      colorClass: 'hintStat',
    });
  });

  it('has correct metadata for primary_type hint', () => {
    expect(HINT_CONFIG.primary_type).toEqual({
      labelKey: 'hint.primaryType',
      icon: '🏷️',
      colorClass: 'hintType',
    });
  });

  it('has correct metadata for secondary_type hint', () => {
    expect(HINT_CONFIG.secondary_type).toEqual({
      labelKey: 'hint.secondaryType',
      icon: '🏷️',
      colorClass: 'hintType',
    });
  });

  it('has correct metadata for fully_evolved hint', () => {
    expect(HINT_CONFIG.fully_evolved).toEqual({
      labelKey: 'hint.evolutionStatus',
      icon: '⚡',
      colorClass: 'hintEvolution',
    });
  });

  it('has correct metadata for effectiveness hint', () => {
    expect(HINT_CONFIG.effectiveness).toEqual({
      labelKey: 'hint.typeEffectiveness',
      icon: '⚔️',
      colorClass: 'hintEffectiveness',
    });
  });

  it('has correct metadata for moves hint', () => {
    expect(HINT_CONFIG.moves).toEqual({
      labelKey: 'hint.pokemonMoves',
      icon: '💥',
      colorClass: 'hintMoves',
    });
  });
});
