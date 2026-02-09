import type { GameResponse } from '../types/api';
import styles from './GameOver.module.css';

interface GameOverProps {
  game: GameResponse;
  onPlayAgain: () => void;
}

export function GameOver({ game, onPlayAgain }: GameOverProps) {
  const { is_won, pokemon, score } = game;

  if (!pokemon) {
    return null;
  }

  return (
    <div className={styles.gameOver}>
      <div className={styles.screenBorder}>
        <div className={styles.resultScreen}>
          <h1 className={`${styles.title} ${is_won ? styles.won : styles.lost}`}>
            {is_won ? 'SCAN COMPLETE' : 'SCAN FAILED'}
          </h1>

          <p className={styles.message}>
            {is_won
              ? 'POKÉMON SUCCESSFULLY IDENTIFIED'
              : 'IDENTIFICATION UNSUCCESSFUL'}
          </p>

          <div className={styles.pokemonReveal}>
            <img
              src={pokemon.image_url}
              alt={pokemon.name}
              className={styles.pokemonImage}
            />
            <div className={styles.pokemonName}>{pokemon.name.toUpperCase()}</div>
            <div className={styles.pokemonId}>#{pokemon.id.toString().padStart(3, '0')}</div>
          </div>

          <div className={styles.scoreReadout}>
            <div className={styles.scoreLabel}>FINAL SCORE</div>
            <div className={styles.scoreValue}>{score || 0}</div>
          </div>

          <div className={styles.actions}>
            <button className={styles.playAgainButton} onClick={onPlayAgain}>
              NEW SCAN
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
