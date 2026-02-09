import { describe, it, expect } from 'vitest';
import { HINT_CONFIG } from './hintConfig';
import type { HintType } from '../types/api';

describe('hintConfig', () => {
  const allHintTypes: HintType[] = ['stat', 'primary_type', 'secondary_type', 'fully_evolved', 'effectiveness'];

  it('has entries for all HintType keys', () => {
    allHintTypes.forEach((hintType) => {
      expect(HINT_CONFIG[hintType]).toBeDefined();
    });
  });

  it('each entry has label defined', () => {
    allHintTypes.forEach((hintType) => {
      expect(HINT_CONFIG[hintType].label).toBeDefined();
      expect(typeof HINT_CONFIG[hintType].label).toBe('string');
      expect(HINT_CONFIG[hintType].label.length).toBeGreaterThan(0);
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
      label: 'Random Stat',
      icon: '📊',
      colorClass: 'hintStat',
    });
  });

  it('has correct metadata for primary_type hint', () => {
    expect(HINT_CONFIG.primary_type).toEqual({
      label: 'Primary Type',
      icon: '🏷️',
      colorClass: 'hintType',
    });
  });

  it('has correct metadata for secondary_type hint', () => {
    expect(HINT_CONFIG.secondary_type).toEqual({
      label: 'Secondary Type',
      icon: '🏷️',
      colorClass: 'hintType',
    });
  });

  it('has correct metadata for fully_evolved hint', () => {
    expect(HINT_CONFIG.fully_evolved).toEqual({
      label: 'Evolution Status',
      icon: '⚡',
      colorClass: 'hintEvolution',
    });
  });

  it('has correct metadata for effectiveness hint', () => {
    expect(HINT_CONFIG.effectiveness).toEqual({
      label: 'Type Effectiveness',
      icon: '⚔️',
      colorClass: 'hintEffectiveness',
    });
  });
});
