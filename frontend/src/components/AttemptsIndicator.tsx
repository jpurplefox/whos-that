import styles from './Game.module.css';

interface AttemptsIndicatorProps {
  attemptsRemaining: number;
  totalAttempts: number;
}

export function AttemptsIndicator({ attemptsRemaining, totalAttempts }: AttemptsIndicatorProps) {
  const getAttemptsColorClass = (): string => {
    if (attemptsRemaining >= 3) return styles.attemptsFull;
    if (attemptsRemaining === 2) return styles.attemptsWarning;
    if (attemptsRemaining === 1) return styles.attemptsCritical;
    return styles.attemptsEmpty;
  };

  return (
    <div className={styles.attemptsDisplay}>
      <div className={styles.attemptsLabel}>TRIES</div>
      <div className={styles.attemptsIcons}>
        {Array.from({ length: totalAttempts }).map((_, index) => (
          <div
            key={index}
            className={`${styles.pokeball} ${
              index < attemptsRemaining
                ? getAttemptsColorClass()
                : styles.pokeballUsed
            } ${
              attemptsRemaining === 1 && index === 0 ? styles.lastAttempt : ''
            }`}
          >
            {index < attemptsRemaining ? '●' : '✕'}
          </div>
        ))}
      </div>
      <div className={styles.attemptsValue}>
        {attemptsRemaining}/{totalAttempts}
      </div>
    </div>
  );
}
