import en from './types/en.json';
import es from './types/es.json';

const vocabularies: Record<string, Record<string, string>> = { en, es };

export function getTypeName(slug: string, language: string): string {
  const vocab = vocabularies[language] ?? vocabularies['en'];
  return vocab?.[slug] ?? slug.charAt(0).toUpperCase() + slug.slice(1);
}
