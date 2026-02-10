import { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import type { Difficulty, GameResponse, HintType } from '../types/api';
import { api } from '../services/api';
import { trackGuessSubmitted, trackGameEnded, trackHintPurchased } from '../services/analytics';
import { HintCard } from './HintCard';
import { PokemonSearch } from './PokemonSearch';
import { BatteryIndicator } from './BatteryIndicator';
import { AttemptsIndicator } from './AttemptsIndicator';
import { HintShop } from './HintShop';
import styles from './Game.module.css';

interface GameProps {
  initialGame: GameResponse;
  onGameOver: (game: GameResponse) => void;
  difficulty: Difficulty;
}

export function Game({ initialGame, onGameOver, difficulty }: GameProps) {
  const { t } = useTranslation();
  const [game, setGame] = useState<GameResponse>(initialGame);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hoveredHintCost, setHoveredHintCost] = useState<number | null>(null);
  const gameStartTimeRef = useRef(Date.now());

  const handleGuess = async (pokemonName: string) => {
    if (isLoading) return;

    setIsLoading(true);
    setError(null);

    try {
      const updatedGame = await api.makeGuess(game.id!, {
        pokemon_name: pokemonName,
      });
      setGame(updatedGame);

      const attemptNumber = updatedGame.attempts.length;
      const hintsUsedCount = updatedGame.hints.filter(h => h.type !== 'comparison').length;
      const timeSinceStart = Math.round((Date.now() - gameStartTimeRef.current) / 1000);

      trackGuessSubmitted({
        game_id: game.id!,
        difficulty,
        guessed_pokemon: pokemonName,
        is_correct: updatedGame.is_won,
        attempt_number: attemptNumber,
        battery_remaining: updatedGame.battery,
        hints_used_count: hintsUsedCount,
        time_since_game_start: timeSinceStart,
      });

      if (updatedGame.is_over) {
        const purchasedHintTypes = updatedGame.hints
          .filter(h => h.type !== 'comparison')
          .map(h => h.type) as HintType[];

        trackGameEnded({
          game_id: game.id!,
          difficulty,
          result: updatedGame.is_won ? 'won' : 'lost',
          score: updatedGame.score ?? 0,
          total_attempts_used: updatedGame.attempts.length,
          battery_remaining: updatedGame.battery,
          hints_purchased_count: purchasedHintTypes.length,
          hint_types_purchased: purchasedHintTypes,
          game_duration_seconds: timeSinceStart,
          target_pokemon_name: updatedGame.pokemon?.name ?? '',
        });

        setTimeout(() => onGameOver(updatedGame), 500);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : t('game.errorGuess'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleConsultHint = async (hintType: HintType) => {
    if (isLoading) return;

    const batteryBefore = game.battery;
    const hintInfo = game.available_hints.find(h => h.type === hintType);
    const hintCost = hintInfo?.cost ?? 0;
    const hintsAlreadyPurchased = game.hints.filter(h => h.type !== 'comparison').length;

    setIsLoading(true);
    setError(null);

    try {
      const updatedGame = await api.consultHint(game.id!, {
        hint_type: hintType,
      });
      setGame(updatedGame);

      trackHintPurchased({
        game_id: game.id!,
        difficulty,
        hint_type: hintType,
        hint_cost: hintCost,
        battery_before: batteryBefore,
        battery_after: updatedGame.battery,
        attempt_number: updatedGame.attempts.length,
        hints_already_purchased: hintsAlreadyPurchased,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : t('game.errorHint'));
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
              <p className={styles.mysteryLabel}>{t('game.mysteryPokemon')}</p>
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
                <h3 className={styles.sectionTitle}>{t('game.knownData')}</h3>
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
            <h3 className={styles.inputTitle}>{t('game.submitGuess')}</h3>
            <PokemonSearch onSelect={handleGuess} disabled={isLoading} />
            {error && <div className="error">{error}</div>}
          </div>
        </div>
      </div>
    </div>
  );
}
