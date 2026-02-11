import en from './moves/en.json';
import es from './moves/es.json';

const vocabularies: Record<string, Record<string, string>> = { en, es };

function formatSlug(slug: string): string {
  return slug
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

export function getMoveName(slug: string, language: string): string {
  const vocab = vocabularies[language] ?? vocabularies['en'];
  return vocab?.[slug] ?? formatSlug(slug);
}
