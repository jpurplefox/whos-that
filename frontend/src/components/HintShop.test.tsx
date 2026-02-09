import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HintShop } from './HintShop';
import type { AvailableHint } from '../types/api';

describe('HintShop', () => {
  const mockOnConsultHint = vi.fn();
  const mockOnHoverCost = vi.fn();

  const defaultProps = {
    availableHints: [] as AvailableHint[],
    battery: 10,
    isLoading: false,
    onConsultHint: mockOnConsultHint,
    onHoverCost: mockOnHoverCost,
  };

  beforeEach(() => {
    mockOnConsultHint.mockReset();
    mockOnHoverCost.mockReset();
  });

  it('renders only hints with non-null cost', () => {
    const hints: AvailableHint[] = [
      { type: 'stat', cost: 2, available: true },
      { type: 'primary_type', cost: null, available: true },
      { type: 'secondary_type', cost: 3, available: true },
      { type: 'fully_evolved', cost: null, available: false },
    ];

    render(<HintShop {...defaultProps} availableHints={hints} />);

    // Should only render stat and secondary_type (those with non-null cost)
    expect(screen.getByText('Random Stat')).toBeInTheDocument();
    expect(screen.getByText('Secondary Type')).toBeInTheDocument();
    expect(screen.queryByText('Primary Type')).not.toBeInTheDocument();
    expect(screen.queryByText('Evolution Status')).not.toBeInTheDocument();
  });

  it('shows USED label for purchased hints', () => {
    const hints: AvailableHint[] = [
      { type: 'stat', cost: 2, available: false },
      { type: 'primary_type', cost: 3, available: true },
    ];

    render(<HintShop {...defaultProps} availableHints={hints} />);

    // Get all USED labels
    const usedLabels = screen.getAllByText('USED');
    expect(usedLabels).toHaveLength(1);

    // The button with USED should be disabled
    const statButton = screen.getByRole('button', { name: /Random Stat/i });
    expect(statButton).toBeDisabled();
  });

  it('shows LOW PWR label when battery is insufficient', () => {
    const hints: AvailableHint[] = [
      { type: 'stat', cost: 5, available: true },
      { type: 'primary_type', cost: 2, available: true },
    ];

    render(<HintShop {...defaultProps} availableHints={hints} battery={3} />);

    // Should show LOW PWR for stat hint (cost 5, battery 3)
    const lowPwrLabels = screen.getAllByText('LOW PWR');
    expect(lowPwrLabels).toHaveLength(1);

    // The stat button should be disabled
    const statButton = screen.getByRole('button', { name: /Random Stat/i });
    expect(statButton).toBeDisabled();

    // The primary_type button should not be disabled
    const primaryTypeButton = screen.getByRole('button', { name: /Primary Type/i });
    expect(primaryTypeButton).not.toBeDisabled();
  });

  it('calls onConsultHint when button clicked', async () => {
    const user = userEvent.setup();
    const hints: AvailableHint[] = [
      { type: 'stat', cost: 2, available: true },
      { type: 'primary_type', cost: 3, available: true },
    ];

    render(<HintShop {...defaultProps} availableHints={hints} />);

    const statButton = screen.getByRole('button', { name: /Random Stat/i });
    await user.click(statButton);

    expect(mockOnConsultHint).toHaveBeenCalledTimes(1);
    expect(mockOnConsultHint).toHaveBeenCalledWith('stat');
  });

  it('calls onHoverCost on mouse enter', async () => {
    const user = userEvent.setup();
    const hints: AvailableHint[] = [
      { type: 'stat', cost: 2, available: true },
    ];

    render(<HintShop {...defaultProps} availableHints={hints} />);

    const statButton = screen.getByRole('button', { name: /Random Stat/i });
    await user.hover(statButton);

    expect(mockOnHoverCost).toHaveBeenCalledWith(2);
  });

  it('calls onHoverCost with null on mouse leave', async () => {
    const user = userEvent.setup();
    const hints: AvailableHint[] = [
      { type: 'stat', cost: 2, available: true },
    ];

    render(<HintShop {...defaultProps} availableHints={hints} />);

    const statButton = screen.getByRole('button', { name: /Random Stat/i });
    await user.hover(statButton);
    await user.unhover(statButton);

    expect(mockOnHoverCost).toHaveBeenCalledWith(null);
  });

  it('does not call onHoverCost when hovering disabled button', async () => {
    const user = userEvent.setup();
    const hints: AvailableHint[] = [
      { type: 'stat', cost: 5, available: true },
    ];

    render(<HintShop {...defaultProps} availableHints={hints} battery={2} />);

    const statButton = screen.getByRole('button', { name: /Random Stat/i });
    await user.hover(statButton);

    expect(mockOnHoverCost).not.toHaveBeenCalled();
  });

  it('disables all buttons when isLoading is true', () => {
    const hints: AvailableHint[] = [
      { type: 'stat', cost: 2, available: true },
      { type: 'primary_type', cost: 3, available: true },
    ];

    render(<HintShop {...defaultProps} availableHints={hints} isLoading={true} />);

    const statButton = screen.getByRole('button', { name: /Random Stat/i });
    const primaryTypeButton = screen.getByRole('button', { name: /Primary Type/i });

    expect(statButton).toBeDisabled();
    expect(primaryTypeButton).toBeDisabled();
  });

  it('does not call onConsultHint when disabled button is clicked', async () => {
    const user = userEvent.setup();
    const hints: AvailableHint[] = [
      { type: 'stat', cost: 2, available: false },
    ];

    render(<HintShop {...defaultProps} availableHints={hints} />);

    const statButton = screen.getByRole('button', { name: /Random Stat/i });

    // Try to click disabled button (this won't trigger the click handler)
    await user.click(statButton);

    expect(mockOnConsultHint).not.toHaveBeenCalled();
  });

  it('renders hint cost with power unit icon', () => {
    const hints: AvailableHint[] = [
      { type: 'stat', cost: 2, available: true },
    ];

    render(<HintShop {...defaultProps} availableHints={hints} />);

    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getAllByText('⚡').length).toBeGreaterThan(0);
  });

  it('renders POKEDEX CONSULTATION title', () => {
    render(<HintShop {...defaultProps} availableHints={[]} />);

    expect(screen.getByText('POKEDEX CONSULTATION')).toBeInTheDocument();
  });

  it('handles multiple hints with various states', () => {
    const hints: AvailableHint[] = [
      { type: 'stat', cost: 2, available: true },
      { type: 'primary_type', cost: 3, available: false },
      { type: 'secondary_type', cost: 5, available: true },
      { type: 'fully_evolved', cost: 2, available: true },
    ];

    render(<HintShop {...defaultProps} availableHints={hints} battery={3} />);

    // stat: available, battery sufficient
    const statButton = screen.getByRole('button', { name: /Random Stat/i });
    expect(statButton).not.toBeDisabled();

    // primary_type: not available (purchased)
    const primaryTypeButton = screen.getByRole('button', { name: /Primary Type/i });
    expect(primaryTypeButton).toBeDisabled();
    expect(screen.getByText('USED')).toBeInTheDocument();

    // secondary_type: available, battery insufficient
    const secondaryTypeButton = screen.getByRole('button', { name: /Secondary Type/i });
    expect(secondaryTypeButton).toBeDisabled();
    expect(screen.getByText('LOW PWR')).toBeInTheDocument();

    // fully_evolved: available, battery sufficient
    const fullyEvolvedButton = screen.getByRole('button', { name: /Evolution Status/i });
    expect(fullyEvolvedButton).not.toBeDisabled();
  });
});
