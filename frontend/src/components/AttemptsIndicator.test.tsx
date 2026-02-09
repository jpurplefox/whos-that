import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AttemptsIndicator } from './AttemptsIndicator';
import styles from './Game.module.css';

describe('AttemptsIndicator', () => {
  it('renders correct number of pokeball icons based on totalAttempts', () => {
    const { container } = render(
      <AttemptsIndicator attemptsRemaining={3} totalAttempts={5} />
    );

    const pokeballs = container.querySelectorAll(`.${styles.pokeball}`);
    expect(pokeballs).toHaveLength(5);
  });

  it('shows remaining vs used indicators', () => {
    render(<AttemptsIndicator attemptsRemaining={3} totalAttempts={5} />);

    // 3 remaining should show ●
    const remainingIndicators = screen.getAllByText('●');
    expect(remainingIndicators).toHaveLength(3);

    // 2 used should show ✕
    const usedIndicators = screen.getAllByText('✕');
    expect(usedIndicators).toHaveLength(2);
  });

  it('shows correct attempts value text', () => {
    render(<AttemptsIndicator attemptsRemaining={3} totalAttempts={5} />);

    expect(screen.getByText('3/5')).toBeInTheDocument();
  });

  it('shows different attempts values correctly', () => {
    const { rerender } = render(
      <AttemptsIndicator attemptsRemaining={2} totalAttempts={4} />
    );

    expect(screen.getByText('2/4')).toBeInTheDocument();

    rerender(<AttemptsIndicator attemptsRemaining={0} totalAttempts={4} />);

    expect(screen.getByText('0/4')).toBeInTheDocument();
  });

  it('renders TRIES label', () => {
    render(<AttemptsIndicator attemptsRemaining={3} totalAttempts={5} />);

    expect(screen.getByText('TRIES')).toBeInTheDocument();
  });

  it('handles edge case with zero attempts remaining', () => {
    render(<AttemptsIndicator attemptsRemaining={0} totalAttempts={5} />);

    expect(screen.getByText('0/5')).toBeInTheDocument();

    const usedIndicators = screen.getAllByText('✕');
    expect(usedIndicators).toHaveLength(5);

    const remainingIndicators = screen.queryAllByText('●');
    expect(remainingIndicators).toHaveLength(0);
  });

  it('handles edge case with all attempts remaining', () => {
    render(<AttemptsIndicator attemptsRemaining={5} totalAttempts={5} />);

    expect(screen.getByText('5/5')).toBeInTheDocument();

    const remainingIndicators = screen.getAllByText('●');
    expect(remainingIndicators).toHaveLength(5);

    const usedIndicators = screen.queryAllByText('✕');
    expect(usedIndicators).toHaveLength(0);
  });

  it('handles single attempt scenario', () => {
    render(<AttemptsIndicator attemptsRemaining={1} totalAttempts={1} />);

    expect(screen.getByText('1/1')).toBeInTheDocument();
    expect(screen.getByText('●')).toBeInTheDocument();
  });

  it('applies correct classes for remaining attempts', () => {
    const { container } = render(
      <AttemptsIndicator attemptsRemaining={2} totalAttempts={5} />
    );

    const pokeballs = container.querySelectorAll(`.${styles.pokeball}`);

    // First 2 should not have pokeballUsed class
    expect(pokeballs[0].className).not.toContain(styles.pokeballUsed);
    expect(pokeballs[1].className).not.toContain(styles.pokeballUsed);

    // Last 3 should have pokeballUsed class
    expect(pokeballs[2].className).toContain(styles.pokeballUsed);
    expect(pokeballs[3].className).toContain(styles.pokeballUsed);
    expect(pokeballs[4].className).toContain(styles.pokeballUsed);
  });
});
