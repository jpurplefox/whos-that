import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { HintCard } from './HintCard';
import type { StatHint, PrimaryTypeHint, SecondaryTypeHint, FullyEvolvedHint, EffectivenessHint, Pokemon } from '../types/api';
import styles from './HintCard.module.css';

// Mock pokemonCache
vi.mock('../services/pokemonCache', () => ({
  findPokemonByName: vi.fn(),
}));

describe('HintCard', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  describe('StatHint', () => {
    it('renders stat hint with stat name and value', () => {
      const hint: StatHint = {
        type: 'stat',
        stat: 'hp',
        value: 100,
      };

      render(<HintCard hint={hint} />);

      expect(screen.getByText('hp')).toBeInTheDocument();
      expect(screen.getByText('100')).toBeInTheDocument();
    });

    it('renders stat hint with underscored stat name', () => {
      const hint: StatHint = {
        type: 'stat',
        stat: 'sp_attack',
        value: 90,
      };

      render(<HintCard hint={hint} />);

      expect(screen.getByText('sp attack')).toBeInTheDocument();
      expect(screen.getByText('90')).toBeInTheDocument();
    });
  });

  describe('ComparisonHint', () => {
    it('renders comparison hint with pokemon name and comparison icons', async () => {
      const { findPokemonByName } = await import('../services/pokemonCache');
      const mockPokemon: Pokemon = {
        id: 25,
        name: 'Pikachu',
        image_url: 'https://example.com/pikachu.png',
      };

      vi.mocked(findPokemonByName).mockReturnValue(mockPokemon);

      const hint = {
        type: 'comparison' as const,
        pokemon: 'Pikachu',
        comparisons: {
          hp: 'higher' as const,
          attack: 'lower' as const,
          defense: 'equal' as const,
          sp_attack: 'higher' as const,
          sp_defense: 'lower' as const,
          speed: 'higher' as const,
        },
      };

      render(<HintCard hint={hint} />);

      expect(screen.getByText('Pikachu')).toBeInTheDocument();
      expect(screen.getByAltText('Pikachu')).toHaveAttribute('src', 'https://example.com/pikachu.png');

      // Check for comparison icons (↑, ↓, =)
      const higherIcon = '\u2191';
      const lowerIcon = '\u2193';
      const equalIcon = '=';

      expect(screen.getAllByText(higherIcon)).toHaveLength(3); // hp, sp_attack, speed
      expect(screen.getAllByText(lowerIcon)).toHaveLength(2); // attack, sp_defense
      expect(screen.getByText(equalIcon)).toBeInTheDocument(); // defense
    });
  });

  describe('PrimaryTypeHint', () => {
    it('renders primary_type hint with type label', () => {
      const hint: PrimaryTypeHint = {
        type: 'primary_type',
        primary_type: 'Electric',
      };

      render(<HintCard hint={hint} />);

      expect(screen.getByText('Primary Type')).toBeInTheDocument();
      expect(screen.getByText('Electric')).toBeInTheDocument();
    });
  });

  describe('SecondaryTypeHint', () => {
    it('renders secondary_type hint with type value', () => {
      const hint: SecondaryTypeHint = {
        type: 'secondary_type',
        secondary_type: 'Flying',
      };

      render(<HintCard hint={hint} />);

      expect(screen.getByText('Secondary Type')).toBeInTheDocument();
      expect(screen.getByText('Flying')).toBeInTheDocument();
    });

    it('renders secondary_type hint showing "None" when null', () => {
      const hint: SecondaryTypeHint = {
        type: 'secondary_type',
        secondary_type: null,
      };

      render(<HintCard hint={hint} />);

      expect(screen.getByText('Secondary Type')).toBeInTheDocument();
      expect(screen.getByText('None')).toBeInTheDocument();
    });
  });

  describe('FullyEvolvedHint', () => {
    it('renders fully_evolved hint when true', () => {
      const hint: FullyEvolvedHint = {
        type: 'fully_evolved',
        is_fully_evolved: true,
      };

      render(<HintCard hint={hint} />);

      expect(screen.getByText('Fully Evolved')).toBeInTheDocument();
    });

    it('renders fully_evolved hint when false', () => {
      const hint: FullyEvolvedHint = {
        type: 'fully_evolved',
        is_fully_evolved: false,
      };

      render(<HintCard hint={hint} />);

      expect(screen.getByText('Not Fully Evolved')).toBeInTheDocument();
    });
  });

  describe('EffectivenessHint', () => {
    it('renders effectiveness hint with relation and element', () => {
      const hint: EffectivenessHint = {
        type: 'effectiveness',
        relation: 'strong against',
        element: 'Water',
        multiplier: 2.0,
      };

      render(<HintCard hint={hint} />);

      expect(screen.getByText('strong against')).toBeInTheDocument();
      expect(screen.getByText('Water')).toBeInTheDocument();
      expect(screen.getByText('×2')).toBeInTheDocument();
    });

    it('renders effectiveness completion hint', () => {
      const hint: EffectivenessHint = {
        type: 'effectiveness',
        relation: 'completion',
        element: null,
        multiplier: null,
      };

      render(<HintCard hint={hint} />);

      expect(screen.getByText('All type attributes revealed!')).toBeInTheDocument();
    });
  });

  describe('isNew prop', () => {
    it('applies newCard class when isNew is true', () => {
      const hint: StatHint = {
        type: 'stat',
        stat: 'attack',
        value: 80,
      };

      const { container } = render(<HintCard hint={hint} isNew={true} />);

      const hintCard = container.querySelector(`.${styles.newCard}`);
      expect(hintCard).toBeInTheDocument();
    });

    it('does not apply newCard class when isNew is false', () => {
      const hint: StatHint = {
        type: 'stat',
        stat: 'attack',
        value: 80,
      };

      const { container } = render(<HintCard hint={hint} isNew={false} />);

      const hintCard = container.querySelector(`.${styles.newCard}`);
      expect(hintCard).not.toBeInTheDocument();
    });

    it('does not apply newCard class when isNew is undefined', () => {
      const hint: StatHint = {
        type: 'stat',
        stat: 'attack',
        value: 80,
      };

      const { container } = render(<HintCard hint={hint} />);

      const hintCard = container.querySelector(`.${styles.newCard}`);
      expect(hintCard).not.toBeInTheDocument();
    });
  });
});
