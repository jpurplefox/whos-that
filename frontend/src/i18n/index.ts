import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import en from './locales/en.ts';
import es from './locales/es.ts';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: { en, es },
    fallbackLng: 'en',
    interpolation: { escapeValue: false },
    detection: {
      order: ['localStorage', 'navigator'],
      lookupLocalStorage: 'whos_that_lang',
      caches: ['localStorage'],
    },
  });

export default i18n;
