import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { Difficulty } from '../types/api';
import styles from './Home.module.css';

interface HomeProps {
  onStartGame: (difficulty: Difficulty) => void;
}

export function Home({ onStartGame }: HomeProps) {
  const { t } = useTranslation();
  const [selectedDifficulty, setSelectedDifficulty] = useState<Difficulty>('medium');

  const handleStart = () => {
    onStartGame(selectedDifficulty);
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
                className={`${styles.difficultyButton} ${styles.easy} ${
                  selectedDifficulty === 'easy' ? styles.selected : ''
                }`}
                onClick={() => setSelectedDifficulty('easy')}
              >
                {t('home.easy')}
              </button>
              <button
                className={`${styles.difficultyButton} ${styles.medium} ${
                  selectedDifficulty === 'medium' ? styles.selected : ''
                }`}
                onClick={() => setSelectedDifficulty('medium')}
              >
                {t('home.medium')}
              </button>
              <button
                className={`${styles.difficultyButton} ${styles.hard} ${
                  selectedDifficulty === 'hard' ? styles.selected : ''
                }`}
                onClick={() => setSelectedDifficulty('hard')}
              >
                {t('home.hard')}
              </button>
            </div>
          </div>

          <button className={styles.startButton} onClick={handleStart}>
            {t('home.startGame')}
          </button>
        </div>
      </div>
    </div>
  );
}
