import type { HintType, AvailableHint } from '../types/api';
import { HINT_CONFIG } from '../config/hintConfig';
import styles from './Game.module.css';

interface HintShopProps {
  availableHints: AvailableHint[];
  battery: number;
  isLoading: boolean;
  onConsultHint: (hintType: HintType) => void;
  onHoverCost: (cost: number | null) => void;
}

type DisabledReason = 'purchased' | 'low-battery' | null;

export function HintShop({ availableHints, battery, isLoading, onConsultHint, onHoverCost }: HintShopProps) {
  const getDisabledReason = (availableHint: AvailableHint): DisabledReason => {
    if (!availableHint.available) return 'purchased';
    if (battery < (availableHint.cost || 0)) return 'low-battery';
    return null;
  };

  return (
    <div className={styles.controlPanel}>
      <h3 className={styles.controlTitle}>POKEDEX CONSULTATION</h3>
      <div className={styles.hintShop}>
        {availableHints
          .filter((h) => h.cost !== null)
          .map((availableHint) => {
            const metadata = HINT_CONFIG[availableHint.type];
            const disabledReason = getDisabledReason(availableHint);
            const isDisabled = disabledReason !== null || isLoading;
            return (
              <button
                key={availableHint.type}
                className={`${styles.hintButton} ${styles[metadata.colorClass]} ${
                  disabledReason === 'purchased' ? styles.purchased :
                  disabledReason === 'low-battery' ? styles.lowBattery : ''
                }`}
                onClick={() => onConsultHint(availableHint.type)}
                disabled={isDisabled}
                onMouseEnter={() => !isDisabled && onHoverCost(availableHint.cost)}
                onMouseLeave={() => onHoverCost(null)}
              >
                <span className={styles.hintIcon}>{metadata.icon}</span>
                <span className={styles.hintLabel}>{metadata.label}</span>
                <div className={styles.hintCostWrapper}>
                  <span className={styles.hintCost}>{availableHint.cost}</span>
                  <span className={styles.powerUnit}>⚡</span>
                </div>
                {disabledReason === 'purchased' && (
                  <span className={styles.disabledLabel}>USED</span>
                )}
                {disabledReason === 'low-battery' && (
                  <span className={styles.disabledLabel}>LOW PWR</span>
                )}
              </button>
            );
          })}
      </div>
    </div>
  );
}
