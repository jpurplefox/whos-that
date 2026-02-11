import { useTranslation } from 'react-i18next';
import type { Hint, Stat, Comparison, StatHint, ComparisonHint, PrimaryTypeHint, SecondaryTypeHint, FullyEvolvedHint, EffectivenessHint, MoveHint } from '../types/api';
import { findPokemonByName } from '../services/pokemonCache';
import { getMoveName } from '../i18n/vocabulary/moves';
import styles from './HintCard.module.css';

const STAT_ORDER: Stat[] = ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed'];

const STAT_LABEL_KEYS: Record<Stat, string> = {
  hp: 'stat.hp',
  attack: 'stat.attack',
  defense: 'stat.defense',
  sp_attack: 'stat.sp_attack',
  sp_defense: 'stat.sp_defense',
  speed: 'stat.speed',
};

const COMPARISON_ICONS: Record<Comparison, string> = {
  higher: '\u2191',
  lower: '\u2193',
  equal: '=',
};

interface HintCardProps {
  hint: Hint;
  isNew?: boolean;
}

interface HintRendererProps<T extends Hint> {
  hint: T;
  isNew: boolean;
}

function StatCard({ hint, isNew }: HintRendererProps<StatHint>) {
  return (
    <div className={`${styles.hintCard} ${styles.stat} ${isNew ? styles.newCard : ''}`}>
      <div className={styles.hintContent}>
        <div className={styles.statName}>{hint.stat.replace('_', ' ')}</div>
        <div className={styles.statValue}>{hint.value}</div>
      </div>
    </div>
  );
}

function ComparisonCard({ hint, isNew }: HintRendererProps<ComparisonHint>) {
  const { t } = useTranslation();
  const pokemonData = findPokemonByName(hint.pokemon);
  return (
    <div className={`${styles.hintCard} ${styles.comparison} ${isNew ? styles.newCard : ''}`}>
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
              <div className={styles.comparisonStat}>{t(STAT_LABEL_KEYS[stat])}</div>
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

function PrimaryTypeCard({ hint, isNew }: HintRendererProps<PrimaryTypeHint>) {
  const { t } = useTranslation();
  return (
    <div className={`${styles.hintCard} ${styles.type} ${isNew ? styles.newCard : ''}`}>
      <div className={styles.hintContent}>
        <div className={styles.statName}>{t('hintCard.primaryType')}</div>
        <div className={styles.typeValue}>{hint.primary_type}</div>
      </div>
    </div>
  );
}

function SecondaryTypeCard({ hint, isNew }: HintRendererProps<SecondaryTypeHint>) {
  const { t } = useTranslation();
  return (
    <div className={`${styles.hintCard} ${styles.type} ${isNew ? styles.newCard : ''}`}>
      <div className={styles.hintContent}>
        <div className={styles.statName}>{t('hintCard.secondaryType')}</div>
        <div className={hint.secondary_type ? styles.typeValue : `${styles.typeValue} ${styles.none}`}>
          {hint.secondary_type || t('hintCard.none')}
        </div>
      </div>
    </div>
  );
}

function FullyEvolvedCard({ hint, isNew }: HintRendererProps<FullyEvolvedHint>) {
  const { t } = useTranslation();
  return (
    <div className={`${styles.hintCard} ${styles.evolution} ${isNew ? styles.newCard : ''}`}>
      <div className={styles.hintContent}>
        <div className={hint.is_fully_evolved ? `${styles.evolutionValue} ${styles.yes}` : `${styles.evolutionValue} ${styles.no}`}>
          {hint.is_fully_evolved ? t('hintCard.fullyEvolved') : t('hintCard.notFullyEvolved')}
        </div>
      </div>
    </div>
  );
}

function EffectivenessCard({ hint, isNew }: HintRendererProps<EffectivenessHint>) {
  const { t } = useTranslation();
  // Handle completion hint (when all attributes revealed)
  if (hint.relation === 'completion') {
    return (
      <div className={`${styles.hintCard} ${styles.effectiveness} ${isNew ? styles.newCard : ''}`}>
        <div className={styles.hintContent}>
          <div className={styles.typeValue}>{t('hintCard.allRevealed')}</div>
        </div>
      </div>
    );
  }

  return (
    <div className={`${styles.hintCard} ${styles.effectiveness} ${isNew ? styles.newCard : ''}`}>
      <div className={styles.effectivenessContent}>
        <div className={styles.effectivenessRelation}>{hint.relation}</div>
        <div className={styles.effectivenessElement}>{hint.element}</div>
        {hint.multiplier !== null && (
          <div className={styles.effectivenessMultiplier}>&times;{hint.multiplier}</div>
        )}
      </div>
    </div>
  );
}

function MoveCard({ hint, isNew }: HintRendererProps<MoveHint>) {
  const { t, i18n } = useTranslation();
  // Handle completion hint (when all moves revealed)
  if (hint.move === null) {
    return (
      <div className={`${styles.hintCard} ${styles.moves} ${isNew ? styles.newCard : ''}`}>
        <div className={styles.hintContent}>
          <div className={styles.typeValue}>{t('hintCard.allMovesRevealed')}</div>
        </div>
      </div>
    );
  }

  return (
    <div className={`${styles.hintCard} ${styles.moves} ${isNew ? styles.newCard : ''}`}>
      <div className={styles.hintContent}>
        <div className={styles.statName}>{t('hintCard.move')}</div>
        <div className={styles.moveValue}>{getMoveName(hint.move, i18n.language)}</div>
      </div>
    </div>
  );
}

const HINT_RENDERERS: Record<Hint['type'], React.FC<HintRendererProps<any>>> = {
  stat: StatCard,
  comparison: ComparisonCard,
  primary_type: PrimaryTypeCard,
  secondary_type: SecondaryTypeCard,
  fully_evolved: FullyEvolvedCard,
  effectiveness: EffectivenessCard,
  moves: MoveCard,
};

export function HintCard({ hint, isNew = false }: HintCardProps) {
  const Renderer = HINT_RENDERERS[hint.type];

  if (!Renderer) {
    return null;
  }

  return <Renderer hint={hint} isNew={isNew} />;
}
