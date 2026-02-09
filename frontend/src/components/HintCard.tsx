import type { Hint, Stat, Comparison } from '../types/api';
import { findPokemonByName } from '../services/pokemonCache';
import styles from './HintCard.module.css';

const STAT_ORDER: Stat[] = ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed'];

const STAT_LABELS: Record<Stat, string> = {
  hp: 'HP',
  attack: 'Attack',
  defense: 'Defense',
  sp_attack: 'Sp. Atk',
  sp_defense: 'Sp. Def',
  speed: 'Speed',
};

const COMPARISON_ICONS: Record<Comparison, string> = {
  higher: '\u2191',
  lower: '\u2193',
  equal: '=',
};

interface HintCardProps {
  hint: Hint;
}

export function HintCard({ hint }: HintCardProps) {
  if (hint.type === 'stat') {
    return (
      <div className={`${styles.hintCard} ${styles.stat}`}>
        <div className={styles.hintType}>Stat</div>
        <div className={styles.hintContent}>
          <div className={styles.statName}>{hint.stat.replace('_', ' ')}</div>
          <div className={styles.statValue}>{hint.value}</div>
        </div>
      </div>
    );
  }

  if (hint.type === 'comparison') {
    const pokemonData = findPokemonByName(hint.pokemon);
    return (
      <div className={`${styles.hintCard} ${styles.comparison}`}>
        <div className={styles.hintType}>Comparison</div>
        <div className={styles.comparisonPokemonHeader}>
          {pokemonData && (
            <img src={pokemonData.image_url} alt={hint.pokemon} className={styles.comparisonSprite} />
          )}
          <span className={styles.comparisonPokemon}>{hint.pokemon}</span>
        </div>
        <div className={styles.comparisonGrid}>
          {STAT_ORDER.map((stat) => {
            const comparison = hint.comparisons[stat];
            if (!comparison) return null;
            return (
              <div key={stat} className={styles.comparisonItem}>
                <div className={styles.comparisonStat}>{STAT_LABELS[stat]}</div>
                <div className={`${styles.comparisonValue} ${styles[comparison]}`}>
                  {COMPARISON_ICONS[comparison]}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  if (hint.type === 'primary_type') {
    return (
      <div className={`${styles.hintCard} ${styles.type}`}>
        <div className={styles.hintType}>Primary Type</div>
        <div className={styles.hintContent}>
          <div className={styles.typeValue}>{hint.primary_type}</div>
        </div>
      </div>
    );
  }

  if (hint.type === 'secondary_type') {
    return (
      <div className={`${styles.hintCard} ${styles.type}`}>
        <div className={styles.hintType}>Secondary Type</div>
        <div className={styles.hintContent}>
          <div className={hint.secondary_type ? styles.typeValue : `${styles.typeValue} ${styles.none}`}>
            {hint.secondary_type || 'None'}
          </div>
        </div>
      </div>
    );
  }

  if (hint.type === 'fully_evolved') {
    return (
      <div className={`${styles.hintCard} ${styles.evolution}`}>
        <div className={styles.hintType}>Evolution Status</div>
        <div className={styles.hintContent}>
          <div className={hint.is_fully_evolved ? `${styles.evolutionValue} ${styles.yes}` : `${styles.evolutionValue} ${styles.no}`}>
            {hint.is_fully_evolved ? 'Fully Evolved' : 'Not Fully Evolved'}
          </div>
        </div>
      </div>
    );
  }

  if (hint.type === 'effectiveness') {
    // Handle completion hint (when all attributes revealed)
    if (hint.relation === 'completion') {
      return (
        <div className={`${styles.hintCard} ${styles.effectiveness}`}>
          <div className={styles.hintType}>Type Effectiveness</div>
          <div className={styles.hintContent}>
            <div className={styles.typeValue}>All type attributes revealed!</div>
          </div>
        </div>
      );
    }

    return (
      <div className={`${styles.hintCard} ${styles.effectiveness}`}>
        <div className={styles.hintType}>Type Effectiveness</div>
        <div className={styles.effectivenessContent}>
          <div className={styles.effectivenessRelation}>{hint.relation}</div>
          <div className={styles.effectivenessElement}>{hint.element}</div>
          {hint.multiplier !== null && (
            <div className={styles.effectivenessMultiplier}>×{hint.multiplier}</div>
          )}
        </div>
      </div>
    );
  }

  return null;
}
