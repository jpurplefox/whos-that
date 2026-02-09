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
      <h1 className={`${styles.title} ${is_won ? styles.won : styles.lost}`}>
        {is_won ? 'You Won!' : 'Game Over'}
      </h1>

      <p className={styles.message}>
        {is_won
          ? 'Congratulations! You guessed the Pokémon!'
          : "Better luck next time! Here's the mystery Pokémon:"}
      </p>

      <div className={styles.pokemonReveal}>
        <img
          src={pokemon.image_url}
          alt={pokemon.name}
          className={styles.pokemonImage}
        />
        <div className={styles.pokemonName}>{pokemon.name}</div>
        <div className={styles.pokemonId}>#{pokemon.id.toString().padStart(3, '0')}</div>
      </div>

      <div className={styles.score}>
        <div className={styles.scoreLabel}>Final Score</div>
        <div className={styles.scoreValue}>{score || 0}</div>
      </div>

      <div className={styles.actions}>
        <button className={styles.playAgainButton} onClick={onPlayAgain}>
          Play Again
        </button>
      </div>
    </div>
  );
}
