import { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import type { Pokemon } from '../types/api';
import { getPokemonList } from '../services/pokemonCache';
import styles from './PokemonSearch.module.css';

interface PokemonSearchProps {
  onSelect: (name: string) => void;
  disabled?: boolean;
}

export function PokemonSearch({ onSelect, disabled }: PokemonSearchProps) {
  const { t } = useTranslation();
  const [query, setQuery] = useState('');
  const [pokemon, setPokemon] = useState<Pokemon[]>([]);
  const [filtered, setFiltered] = useState<Pokemon[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    getPokemonList().then(setPokemon).catch(() => {});
  }, []);

  useEffect(() => {
    if (!disabled) {
      inputRef.current?.focus();
    }
  }, [disabled]);

  useEffect(() => {
    if (!query.trim()) {
      setFiltered([]);
      setIsOpen(false);
      return;
    }
    const q = query.toLowerCase();
    const matches = pokemon.filter((p) => p.name.includes(q)).slice(0, 8);
    setFiltered(matches);
    setIsOpen(matches.length > 0);
    setActiveIndex(-1);
  }, [query, pokemon]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const selectPokemon = (name: string) => {
    setQuery('');
    setIsOpen(false);
    onSelect(name);
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveIndex((i) => Math.min(i + 1, filtered.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveIndex((i) => Math.max(i - 1, 0));
    } else if (e.key === 'Enter' && activeIndex >= 0) {
      e.preventDefault();
      selectPokemon(filtered[activeIndex].name);
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  return (
    <div className={styles.container} ref={containerRef}>
      <input
        ref={inputRef}
        type="text"
        className={styles.input}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        onFocus={() => { if (filtered.length > 0) setIsOpen(true); }}
        placeholder={t('search.placeholder')}
        disabled={disabled}
        autoFocus
      />
      {isOpen && (
        <ul className={styles.dropdown}>
          {filtered.map((p, index) => (
            <li
              key={p.id}
              className={`${styles.option} ${index === activeIndex ? styles.active : ''}`}
              onMouseEnter={() => setActiveIndex(index)}
              onMouseDown={() => selectPokemon(p.name)}
            >
              <img src={p.image_url} alt={p.name} className={styles.sprite} />
              <span className={styles.name}>{p.name}</span>
              <span className={styles.number}>#{p.id.toString().padStart(3, '0')}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
