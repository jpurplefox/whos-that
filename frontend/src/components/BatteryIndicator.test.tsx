import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BatteryIndicator } from './BatteryIndicator';
import styles from './Game.module.css';

describe('BatteryIndicator', () => {
  it('renders correct number of segments based on maxBattery', () => {
    const { container } = render(
      <BatteryIndicator battery={5} maxBattery={10} hoveredHintCost={null} />
    );

    const segments = container.querySelectorAll(`.${styles.batterySegment}`);
    expect(segments).toHaveLength(10);
  });

  it('shows correct battery value text', () => {
    render(<BatteryIndicator battery={7} maxBattery={10} hoveredHintCost={null} />);

    expect(screen.getByText('7/10')).toBeInTheDocument();
  });

  it('shows different battery values correctly', () => {
    const { rerender } = render(
      <BatteryIndicator battery={3} maxBattery={5} hoveredHintCost={null} />
    );

    expect(screen.getByText('3/5')).toBeInTheDocument();

    rerender(<BatteryIndicator battery={0} maxBattery={5} hoveredHintCost={null} />);

    expect(screen.getByText('0/5')).toBeInTheDocument();
  });

  it('applies preview class to segments when hoveredHintCost is set', () => {
    const { container } = render(
      <BatteryIndicator battery={8} maxBattery={10} hoveredHintCost={3} />
    );

    const previewSegments = container.querySelectorAll(`.${styles.batterySegmentPreview}`);

    // Should preview removal of 3 segments from the current battery level
    // Battery is 8, cost is 3, so segments at indices 5, 6, 7 should be previewed
    expect(previewSegments).toHaveLength(3);
  });

  it('does not apply preview class when hoveredHintCost is null', () => {
    const { container } = render(
      <BatteryIndicator battery={8} maxBattery={10} hoveredHintCost={null} />
    );

    const previewSegments = container.querySelectorAll(`.${styles.batterySegmentPreview}`);
    expect(previewSegments).toHaveLength(0);
  });

  it('previews correct segments when hovering hint with cost', () => {
    const { container, rerender } = render(
      <BatteryIndicator battery={10} maxBattery={10} hoveredHintCost={null} />
    );

    // No preview initially
    let previewSegments = container.querySelectorAll(`.${styles.batterySegmentPreview}`);
    expect(previewSegments).toHaveLength(0);

    // Hovering hint with cost 2
    rerender(<BatteryIndicator battery={10} maxBattery={10} hoveredHintCost={2} />);

    previewSegments = container.querySelectorAll(`.${styles.batterySegmentPreview}`);
    expect(previewSegments).toHaveLength(2);
  });

  it('renders PWR label', () => {
    render(<BatteryIndicator battery={5} maxBattery={10} hoveredHintCost={null} />);

    expect(screen.getByText('PWR')).toBeInTheDocument();
  });

  it('renders lightning icon', () => {
    render(<BatteryIndicator battery={5} maxBattery={10} hoveredHintCost={null} />);

    expect(screen.getByText('⚡')).toBeInTheDocument();
  });

  it('handles edge case with zero battery', () => {
    const { container } = render(
      <BatteryIndicator battery={0} maxBattery={10} hoveredHintCost={null} />
    );

    expect(screen.getByText('0/10')).toBeInTheDocument();

    const emptySegments = container.querySelectorAll(`.${styles.batterySegmentEmpty}`);
    expect(emptySegments.length).toBeGreaterThan(0);
  });

  it('handles edge case with full battery', () => {
    render(<BatteryIndicator battery={10} maxBattery={10} hoveredHintCost={null} />);

    expect(screen.getByText('10/10')).toBeInTheDocument();
  });
});
