import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { Difficulty } from '../types/api';
import styles from './Home.module.css';

interface HomeProps {
  onStartGame: (difficulty: Difficulty) => void;
}

export function Home({ onStartGame }: HomeProps) {
  const { t } = useTranslation();
  const [selected, setSelected] = useState<Difficulty | null>(null);

  const handleSelect = (difficulty: Difficulty) => {
    if (selected) return;
    setSelected(difficulty);
    setTimeout(() => onStartGame(difficulty), 150);
  };

  return (
    <div className={styles.home}>
      <div className={styles.deviceIndicators}>
        <div className={styles.blueLens}></div>
        <div className={styles.ledIndicators}>
          <span className={styles.ledRed}></span>
          <span className={styles.ledYellow}></span>
          <span className={styles.ledGreen}></span>
        </div>
      </div>

      <div className={styles.screenBorder}>
        <div className={styles.screen}>
          <h1 className={styles.title}>{t('home.title')}</h1>
          <p className={styles.subtitle}>
            {t('home.subtitle')}
          </p>

          <div className={styles.difficultySection}>
            <h2>{t('home.chooseDifficulty')}</h2>
            <div className={styles.difficultyButtons}>
              <button
                className={`${styles.difficultyButton} ${styles.easy} ${selected === 'easy' ? styles.selected : ''}`}
                onClick={() => handleSelect('easy')}
                disabled={selected !== null}
              >
                {t('home.easy')}
              </button>
              <button
                className={`${styles.difficultyButton} ${styles.medium} ${selected === 'medium' ? styles.selected : ''}`}
                onClick={() => handleSelect('medium')}
                disabled={selected !== null}
              >
                {t('home.medium')}
              </button>
              <button
                className={`${styles.difficultyButton} ${styles.hard} ${selected === 'hard' ? styles.selected : ''}`}
                onClick={() => handleSelect('hard')}
                disabled={selected !== null}
              >
                {t('home.hard')}
              </button>
            </div>
          </div>

          <a href="https://instagram.com/collado.jesica" target="_blank" rel="noopener noreferrer" className={styles.contactLink} aria-label="@collado.jesica on Instagram (opens in new tab)">
            @collado.jesica
          </a>
          <p className={styles.disclaimer}>{t('home.disclaimer')}</p>
        </div>
      </div>
    </div>
  );
}
