import { describe, it, expect, vi, beforeEach } from 'vitest';
import type { Pokemon } from '../types/api';

// Mock the api module
vi.mock('./api', () => ({
  api: {
    listPokemon: vi.fn(),
  },
}));

const mockPokemonList: Pokemon[] = [
  { id: 1, name: 'Bulbasaur', image_url: 'https://example.com/bulbasaur.png' },
  { id: 25, name: 'Pikachu', image_url: 'https://example.com/pikachu.png' },
  { id: 150, name: 'Mewtwo', image_url: 'https://example.com/mewtwo.png' },
];

describe('pokemonCache', () => {
  beforeEach(async () => {
    // Reset modules to clear module-level state
    vi.resetModules();
  });

  it('returns cached list on repeated calls', async () => {
    const { api } = await import('./api');
    const { getPokemonList } = await import('./pokemonCache');

    vi.mocked(api.listPokemon).mockResolvedValue(mockPokemonList);

    const firstCall = await getPokemonList();
    const secondCall = await getPokemonList();

    expect(firstCall).toEqual(mockPokemonList);
    expect(secondCall).toEqual(mockPokemonList);
    expect(api.listPokemon).toHaveBeenCalledTimes(1);
  });

  it('does not re-fetch when data is already cached', async () => {
    const { api } = await import('./api');
    const { getPokemonList } = await import('./pokemonCache');

    vi.mocked(api.listPokemon).mockClear().mockResolvedValue(mockPokemonList);

    await getPokemonList();
    await getPokemonList();
    await getPokemonList();

    expect(api.listPokemon).toHaveBeenCalledTimes(1);
  });

  it('resets and allows retry after fetch failure', async () => {
    const { api } = await import('./api');
    const { getPokemonList } = await import('./pokemonCache');

    const error = new Error('Network error');
    vi.mocked(api.listPokemon).mockClear()
      .mockRejectedValueOnce(error)
      .mockResolvedValueOnce(mockPokemonList);

    await expect(getPokemonList()).rejects.toThrow('Network error');

    const result = await getPokemonList();
    expect(result).toEqual(mockPokemonList);
    expect(api.listPokemon).toHaveBeenCalledTimes(2);
  });

  it('deduplicates concurrent calls', async () => {
    const { api } = await import('./api');
    const { getPokemonList } = await import('./pokemonCache');

    vi.mocked(api.listPokemon).mockClear().mockResolvedValue(mockPokemonList);

    const [result1, result2, result3] = await Promise.all([
      getPokemonList(),
      getPokemonList(),
      getPokemonList(),
    ]);

    expect(result1).toEqual(mockPokemonList);
    expect(result2).toEqual(mockPokemonList);
    expect(result3).toEqual(mockPokemonList);
    expect(api.listPokemon).toHaveBeenCalledTimes(1);
  });

  it('findPokemonByName returns pokemon when cached', async () => {
    const { api } = await import('./api');
    const { getPokemonList, findPokemonByName } = await import('./pokemonCache');

    vi.mocked(api.listPokemon).mockResolvedValue(mockPokemonList);

    await getPokemonList();

    const pikachu = findPokemonByName('Pikachu');
    expect(pikachu).toEqual(mockPokemonList[1]);
  });

  it('findPokemonByName returns undefined when not cached', async () => {
    const { findPokemonByName } = await import('./pokemonCache');

    const result = findPokemonByName('Pikachu');
    expect(result).toBeUndefined();
  });

  it('findPokemonByName returns undefined when pokemon not in list', async () => {
    const { api } = await import('./api');
    const { getPokemonList, findPokemonByName } = await import('./pokemonCache');

    vi.mocked(api.listPokemon).mockResolvedValue(mockPokemonList);

    await getPokemonList();

    const result = findPokemonByName('NonExistent');
    expect(result).toBeUndefined();
  });
});
