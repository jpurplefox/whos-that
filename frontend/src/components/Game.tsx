import { useState } from 'react';
import type { GameResponse, HintType } from '../types/api';
import { api } from '../services/api';
import { HintCard } from './HintCard';
import { PokemonSearch } from './PokemonSearch';
import styles from './Game.module.css';

interface GameProps {
  initialGame: GameResponse;
  onGameOver: (game: GameResponse) => void;
}

export function Game({ initialGame, onGameOver }: GameProps) {
  const [game, setGame] = useState<GameResponse>(initialGame);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

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

  const getHintMetadata = (type: HintType): { icon: string; colorClass: string } => {
    const metadata: Record<HintType, { icon: string; colorClass: string }> = {
      stat: { icon: '📊', colorClass: styles.hintStat },
      primary_type: { icon: '🏷️', colorClass: styles.hintType },
      secondary_type: { icon: '🏷️', colorClass: styles.hintType },
      fully_evolved: { icon: '⚡', colorClass: styles.hintEvolution },
      effectiveness: { icon: '⚔️', colorClass: styles.hintEffectiveness },
    };
    return metadata[type];
  };

  const getDisabledReason = (availableHint: typeof game.available_hints[0]): 'purchased' | 'low-battery' | null => {
    if (!availableHint.available) return 'purchased';
    if (game.battery < (availableHint.cost || 0)) return 'low-battery';
    return null;
  };

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
              <div className={styles.batteryDisplay}>
                <div className={styles.batteryLabel}>BATTERY</div>
                <div className={`${styles.batteryValue} ${isLowBattery ? styles.warning : ''}`}>
                  {game.battery}/{game.max_battery}
                </div>
              </div>
              <div className={styles.attemptsDisplay}>
                <div className={styles.attemptsLabel}>ATTEMPTS</div>
                <div className={styles.attemptsValue}>{game.attempts_remaining}</div>
              </div>
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
        {game.hints.length > 0 && (
          <div className={styles.infoScreen}>
            <div className={styles.screenWrapper}>
              <div className={styles.hintsSection}>
                <h3 className={styles.sectionTitle}>DATA RETRIEVED</h3>
                <div className={styles.hintsGrid}>
                  {game.hints.map((hint, index) => (
                    <HintCard key={index} hint={hint} />
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        <div className={styles.controlPanel}>
          <h3 className={styles.controlTitle}>POKEDEX CONSULTATION ({game.battery} battery)</h3>
          <div className={styles.hintShop}>
            {game.available_hints
              .filter((h) => h.cost !== null)
              .map((availableHint) => {
                const metadata = getHintMetadata(availableHint.type);
                const disabledReason = getDisabledReason(availableHint);
                const isDisabled = disabledReason !== null || isLoading;
                return (
                  <button
                    key={availableHint.type}
                    className={`${styles.hintButton} ${metadata.colorClass} ${
                      disabledReason === 'purchased' ? styles.purchased :
                      disabledReason === 'low-battery' ? styles.lowBattery : ''
                    }`}
                    onClick={() => handleConsultHint(availableHint.type)}
                    disabled={isDisabled}
                  >
                    <span className={styles.hintIcon}>{metadata.icon}</span>
                    <span className={styles.hintLabel}>{getHintTypeLabel(availableHint.type)}</span>
                    <div className={styles.hintCostWrapper}>
                      <span className={styles.hintCost}>{availableHint.cost}</span>
                      <span className={styles.powerUnit}>⚡</span>
                    </div>
                    {disabledReason === 'purchased' && (
                      <span className={styles.disabledLabel}>USED</span>
                    )}
                    {disabledReason === 'low-battery' && (
                      <span className={styles.disabledLabel}>LOW PWR</span>
                    )}
                  </button>
                );
              })}
          </div>
        </div>

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
