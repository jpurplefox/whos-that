import { useTranslation } from 'react-i18next';
import styles from './LanguageSwitcher.module.css';

export function LanguageSwitcher() {
  const { i18n } = useTranslation();
  const isSpanish = i18n.language.startsWith('es');

  const switchLanguage = (lang: string) => {
    i18n.changeLanguage(lang);
  };

  return (
    <div className={styles.switcher}>
      <button
        className={`${styles.option} ${!isSpanish ? styles.active : ''}`}
        onClick={() => switchLanguage('en')}
        aria-label="English"
      >
        EN
      </button>
      <button
        className={`${styles.option} ${isSpanish ? styles.active : ''}`}
        onClick={() => switchLanguage('es')}
        aria-label="Español"
      >
        ES
      </button>
      <div className={`${styles.slider} ${isSpanish ? styles.sliderRight : ''}`} />
    </div>
  );
}
