import { useState } from 'react';
import type { Difficulty } from '../types/api';
import styles from './Home.module.css';

interface HomeProps {
  onStartGame: (difficulty: Difficulty) => void;
}

export function Home({ onStartGame }: HomeProps) {
  const [selectedDifficulty, setSelectedDifficulty] = useState<Difficulty>('medium');

  const handleStart = () => {
    onStartGame(selectedDifficulty);
  };

  return (
    <div className={styles.home}>
      <h1 className={styles.title}>Who's That Pokémon?</h1>
      <p className={styles.subtitle}>
        Test your Pokémon knowledge! Guess the mystery Pokémon using hints and comparisons.
      </p>

      <div className={styles.difficultySection}>
        <h2>Choose Your Difficulty</h2>
        <div className={styles.difficultyButtons}>
          <button
            className={`${styles.difficultyButton} ${styles.easy} ${
              selectedDifficulty === 'easy' ? styles.selected : ''
            }`}
            onClick={() => setSelectedDifficulty('easy')}
          >
            Easy
          </button>
          <button
            className={`${styles.difficultyButton} ${styles.medium} ${
              selectedDifficulty === 'medium' ? styles.selected : ''
            }`}
            onClick={() => setSelectedDifficulty('medium')}
          >
            Medium
          </button>
          <button
            className={`${styles.difficultyButton} ${styles.hard} ${
              selectedDifficulty === 'hard' ? styles.selected : ''
            }`}
            onClick={() => setSelectedDifficulty('hard')}
          >
            Hard
          </button>
        </div>
      </div>

      <button className={styles.startButton} onClick={handleStart}>
        Start Game
      </button>
    </div>
  );
}
