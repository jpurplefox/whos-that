import type { Pokemon } from '../types/api';
import { api } from './api';

let cached: Pokemon[] | null = null;
let loading: Promise<Pokemon[]> | null = null;

export async function getPokemonList(): Promise<Pokemon[]> {
  if (cached) return cached;
  if (!loading) {
    loading = api.listPokemon().then((list) => {
      cached = list;
      return list;
    });
  }
  return loading;
}

export function findPokemonByName(name: string): Pokemon | undefined {
  return cached?.find((p) => p.name === name);
}
