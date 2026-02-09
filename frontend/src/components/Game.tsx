import { useState } from 'react';
import type { GameResponse, HintType } from '../types/api';
import { api } from '../services/api';
import { HintCard } from './HintCard';
import { PokemonSearch } from './PokemonSearch';
import { BatteryIndicator } from './BatteryIndicator';
import { AttemptsIndicator } from './AttemptsIndicator';
import { HintShop } from './HintShop';
import styles from './Game.module.css';

interface GameProps {
  initialGame: GameResponse;
  onGameOver: (game: GameResponse) => void;
}

export function Game({ initialGame, onGameOver }: GameProps) {
  const [game, setGame] = useState<GameResponse>(initialGame);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hoveredHintCost, setHoveredHintCost] = useState<number | null>(null);

  const handleGuess = async (pokemonName: string) => {
    if (isLoading) return;

    setIsLoading(true);
    setError(null);

    try {
      const updatedGame = await api.makeGuess(game.id!, {
        pokemon_name: pokemonName,
      });
      setGame(updatedGame);

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

  return (
    <div className={styles.game}>
      {/* UPPER SECTION */}
      <div className={styles.upperSection}>
        <div className={styles.deviceHeader}>
          <div className={styles.blueLens}></div>
          <div className={styles.statusLEDs}>
            <span className={`${styles.led} ${isLowBattery ? styles.blinking : ''}`}></span>
            <span className={styles.led}></span>
            <span className={styles.led}></span>
          </div>
        </div>

        <div className={styles.mainScreen}>
          <div className={styles.screenContent}>
            <div className={styles.statusDisplay}>
              <BatteryIndicator
                battery={game.battery}
                maxBattery={game.max_battery}
                hoveredHintCost={hoveredHintCost}
              />
              <AttemptsIndicator
                attemptsRemaining={game.attempts_remaining}
                totalAttempts={game.attempts_remaining + game.attempts.length}
              />
            </div>

            <div className={styles.mysterySilhouette}>
              <div className={styles.scanningEffect}></div>
              <div className={styles.scanLine}></div>
              <div className={styles.silhouetteImage}>?</div>
              <p className={styles.mysteryLabel}>MYSTERY POKÉMON</p>
            </div>
          </div>
        </div>
      </div>

      {/* HINGE */}
      <div className={styles.hinge}>
        <div className={styles.hingeBar}></div>
        <div className={styles.hingeConnector}></div>
      </div>

      {/* LOWER SECTION */}
      <div className={styles.lowerSection}>
        <HintShop
          availableHints={game.available_hints}
          battery={game.battery}
          isLoading={isLoading}
          onConsultHint={handleConsultHint}
          onHoverCost={setHoveredHintCost}
        />

        {game.hints.length > 0 && (
          <div className={styles.infoScreen}>
            <div className={styles.screenWrapper}>
              <div className={styles.hintsSection}>
                <h3 className={styles.sectionTitle}>DATA RETRIEVED</h3>
                <div className={styles.hintsGrid}>
                  {[...game.hints].reverse().map((hint, index) => (
                    <HintCard
                      key={game.hints.length - 1 - index}
                      hint={hint}
                      isNew={index === 0}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        <div className={styles.inputScreen}>
          <div className={styles.inputWrapper}>
            <h3 className={styles.inputTitle}>IDENTIFY POKÉMON</h3>
            <PokemonSearch onSelect={handleGuess} disabled={isLoading} />
            {error && <div className="error">{error}</div>}
          </div>
        </div>
      </div>
    </div>
  );
}
