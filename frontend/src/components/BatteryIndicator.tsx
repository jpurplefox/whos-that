import { useTranslation } from 'react-i18next';
import styles from './Game.module.css';

interface BatteryIndicatorProps {
  battery: number;
  maxBattery: number;
  hoveredHintCost: number | null;
}

export function BatteryIndicator({ battery, maxBattery, hoveredHintCost }: BatteryIndicatorProps) {
  const { t } = useTranslation();
  const batteryPercentage = (battery / maxBattery) * 100;
  const isLowBattery = batteryPercentage < 30;

  const getBatteryColorClass = (): string => {
    if (batteryPercentage >= 75) return styles.batteryFull;
    if (batteryPercentage >= 50) return styles.batteryGood;
    if (batteryPercentage >= 30) return styles.batteryWarning;
    return styles.batteryCritical;
  };

  return (
    <div className={styles.batteryDisplay}>
      <div className={styles.batteryHeader}>
        <span className={styles.batteryIcon}>⚡</span>
        <span className={styles.batteryLabel}>{t('indicator.pwr')}</span>
      </div>
      <div className={styles.batteryBarOuter}>
        {Array.from({ length: maxBattery }).map((_, index) => {
          const isFilled = index < battery;
          const isPreviewedForRemoval = hoveredHintCost !== null &&
                                         isFilled &&
                                         index >= (battery - hoveredHintCost);
          return (
            <div
              key={`${index}-${hoveredHintCost ?? 'none'}`}
              className={`${styles.batterySegment} ${
                isFilled ? getBatteryColorClass() : styles.batterySegmentEmpty
              } ${isPreviewedForRemoval ? styles.batterySegmentPreview : ''}`}
            />
          );
        })}
        <div className={styles.batteryTerminal} />
      </div>
      <div className={`${styles.batteryValue} ${isLowBattery ? styles.warning : ''}`}>
        {battery}/{maxBattery}
      </div>
    </div>
  );
}
