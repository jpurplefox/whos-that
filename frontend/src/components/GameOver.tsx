import { useTranslation } from 'react-i18next';
import type { Difficulty, GameResponse } from '../types/api';
import { trackPlayAgainClicked } from '../services/analytics';
import styles from './GameOver.module.css';

interface GameOverProps {
  game: GameResponse;
  onPlayAgain: () => void;
  difficulty: Difficulty;
  gamesPlayedThisSession: number;
}

export function GameOver({ game, onPlayAgain, difficulty, gamesPlayedThisSession }: GameOverProps) {
  const { t } = useTranslation();
  const { is_won, pokemon, score } = game;

  if (!pokemon) {
    return null;
  }

  const handlePlayAgain = () => {
    trackPlayAgainClicked({
      previous_game_id: game.id!,
      previous_result: is_won ? 'won' : 'lost',
      previous_score: score ?? 0,
      previous_difficulty: difficulty,
      games_played_this_session: gamesPlayedThisSession,
    });
    onPlayAgain();
  };

  return (
    <div className={styles.gameOver}>
      <div className={styles.screenBorder}>
        <div className={styles.resultScreen}>
          <h1 className={`${styles.title} ${is_won ? styles.won : styles.lost}`}>
            {is_won ? t('gameOver.scanComplete') : t('gameOver.scanFailed')}
          </h1>

          <p className={styles.message}>
            {is_won
              ? t('gameOver.identified')
              : t('gameOver.unsuccessful')}
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
            <div className={styles.scoreLabel}>{t('gameOver.finalScore')}</div>
            <div className={styles.scoreValue}>{score || 0}</div>
          </div>

          <div className={styles.actions}>
            <button className={styles.playAgainButton} onClick={handlePlayAgain}>
              {t('gameOver.newScan')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
