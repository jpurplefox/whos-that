import { useState } from 'react';
import type { FormEvent } from 'react';
import type { GameResponse, HintType } from '../types/api';
import { api } from '../services/api';
import { HintCard } from './HintCard';
import styles from './Game.module.css';

interface GameProps {
  initialGame: GameResponse;
  onGameOver: (game: GameResponse) => void;
}

export function Game({ initialGame, onGameOver }: GameProps) {
  const [game, setGame] = useState<GameResponse>(initialGame);
  const [guessInput, setGuessInput] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleGuess = async (e: FormEvent) => {
    e.preventDefault();
    if (!guessInput.trim() || isLoading) return;

    setIsLoading(true);
    setError(null);

    try {
      const updatedGame = await api.makeGuess(game.id!, {
        pokemon_name: guessInput.trim().toLowerCase(),
      });
      setGame(updatedGame);
      setGuessInput('');

      if (updatedGame.is_over) {
        setTimeout(() => onGameOver(updatedGame), 500);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to make guess');
    } finally {
      setIsLoading(false);
    }
  };

  const handleConsultHint = async (hintType: HintType) => {
    if (isLoading) return;

    setIsLoading(true);
    setError(null);

    try {
      const updatedGame = await api.consultHint(game.id!, {
        hint_type: hintType,
      });
      setGame(updatedGame);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to consult hint');
    } finally {
      setIsLoading(false);
    }
  };

  const batteryPercentage = (game.battery / game.max_battery) * 100;
  const isLowBattery = batteryPercentage < 30;

  const getHintTypeLabel = (type: HintType): string => {
    const labels: Record<HintType, string> = {
      stat: 'Random Stat',
      primary_type: 'Primary Type',
      secondary_type: 'Secondary Type',
      fully_evolved: 'Evolution Status',
      effectiveness: 'Type Effectiveness',
    };
    return labels[type];
  };

  return (
    <div className={styles.game}>
      <div className={styles.header}>
        <h1>Who's That Pokémon?</h1>
      </div>

      <div className={styles.statusBar}>
        <div className={styles.batteryContainer}>
          <div className={styles.batteryLabel}>Battery</div>
          <div className={styles.batteryBar}>
            <div
              className={`${styles.batteryFill} ${isLowBattery ? styles.low : ''}`}
              style={{ width: `${batteryPercentage}%` }}
            />
            <div className={styles.batteryText}>
              {game.battery} / {game.max_battery}
            </div>
          </div>
        </div>

        <div className={styles.attemptsRemaining}>
          Attempts: <strong>{game.attempts_remaining}</strong>
        </div>
      </div>

      <div className={styles.mysterySilhouette}>
        <div className={styles.silhouetteImage}>❓</div>
        <p>Mystery Pokémon</p>
      </div>

      {game.hints.length > 0 && (
        <div className={styles.hintsSection}>
          <h3>Hints</h3>
          <div className={styles.hintsGrid}>
            {game.hints.map((hint, index) => (
              <HintCard key={index} hint={hint} />
            ))}
          </div>
        </div>
      )}

      <div className={styles.hintShopSection}>
        <h3>Pokedex Consultation ({game.battery} battery)</h3>
        <div className={styles.hintShop}>
          {game.available_hints
            .filter((h) => h.cost !== null)
            .map((availableHint) => (
              <button
                key={availableHint.type}
                className={styles.hintButton}
                onClick={() => handleConsultHint(availableHint.type)}
                disabled={!availableHint.available || game.battery < (availableHint.cost || 0) || isLoading}
              >
                <span>{getHintTypeLabel(availableHint.type)}</span>
                <span className={styles.hintCost}>Cost: {availableHint.cost} battery</span>
              </button>
            ))}
        </div>
      </div>

      <div className={styles.guessSection}>
        <h3>Make Your Guess</h3>
        <form onSubmit={handleGuess} className={styles.guessForm}>
          <input
            type="text"
            className={styles.guessInput}
            value={guessInput}
            onChange={(e) => setGuessInput(e.target.value)}
            placeholder="Enter Pokémon name..."
            disabled={isLoading}
          />
          <button type="submit" className={styles.guessButton} disabled={!guessInput.trim() || isLoading}>
            {isLoading ? 'Guessing...' : 'Guess'}
          </button>
        </form>

        {error && <div className="error">{error}</div>}
      </div>

      {game.attempts.length > 0 && (
        <div>
          <h3>Previous Guesses</h3>
          <p style={{ textAlign: 'center', color: 'var(--color-text-secondary)' }}>
            {game.attempts.map((attempt) => attempt).join(', ')}
          </p>
        </div>
      )}
    </div>
  );
}
