import { describe, it, expect, vi, beforeEach } from 'vitest';
import { api } from './api';
import type { CreateGameRequest, GuessRequest, ConsultRequest, Pokemon, GameResponse } from '../types/api';

describe('api', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    global.fetch = vi.fn();
  });

  describe('listPokemon', () => {
    it('returns parsed list on success', async () => {
      const mockPokemon: Pokemon[] = [
        { id: 1, name: 'Bulbasaur', image_url: 'https://example.com/bulbasaur.png' },
        { id: 25, name: 'Pikachu', image_url: 'https://example.com/pikachu.png' },
      ];

      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        json: async () => mockPokemon,
      } as Response);

      const result = await api.listPokemon();

      expect(fetch).toHaveBeenCalledWith('/pokemon');
      expect(result).toEqual(mockPokemon);
    });

    it('throws error on failure', async () => {
      vi.mocked(fetch).mockResolvedValue({
        ok: false,
        statusText: 'Internal Server Error',
      } as Response);

      await expect(api.listPokemon()).rejects.toThrow('Failed to list pokemon: Internal Server Error');
    });
  });

  describe('createGame', () => {
    it('sends correct request body and returns parsed response', async () => {
      const request: CreateGameRequest = { difficulty: 'medium' };
      const mockResponse: GameResponse = {
        id: 'game-123',
        created_at: '2026-02-09T12:00:00Z',
        is_won: false,
        is_over: false,
        attempts_remaining: 5,
        attempts: [],
        hints: [],
        available_hints: [],
        battery: 10,
        max_battery: 10,
        battery_recovery: 2,
        score: null,
        pokemon: null,
      };

      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await api.createGame(request);

      expect(fetch).toHaveBeenCalledWith('/games', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });
      expect(result).toEqual(mockResponse);
    });

    it('throws error on failure', async () => {
      vi.mocked(fetch).mockResolvedValue({
        ok: false,
        statusText: 'Bad Request',
      } as Response);

      await expect(api.createGame({ difficulty: 'easy' })).rejects.toThrow('Failed to create game: Bad Request');
    });
  });

  describe('getGame', () => {
    it('sends correct request and returns parsed response', async () => {
      const gameId = 'game-123';
      const mockResponse: GameResponse = {
        id: gameId,
        created_at: '2026-02-09T12:00:00Z',
        is_won: false,
        is_over: false,
        attempts_remaining: 5,
        attempts: [],
        hints: [],
        available_hints: [],
        battery: 10,
        max_battery: 10,
        battery_recovery: 2,
        score: null,
        pokemon: null,
      };

      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await api.getGame(gameId);

      expect(fetch).toHaveBeenCalledWith(`/games/${gameId}`);
      expect(result).toEqual(mockResponse);
    });
  });

  describe('makeGuess', () => {
    it('sends correct request and returns response', async () => {
      const gameId = 'game-123';
      const request: GuessRequest = { pokemon_name: 'Pikachu' };
      const mockResponse: GameResponse = {
        id: gameId,
        created_at: '2026-02-09T12:00:00Z',
        is_won: true,
        is_over: true,
        attempts_remaining: 4,
        attempts: ['Pikachu'],
        hints: [],
        available_hints: [],
        battery: 10,
        max_battery: 10,
        battery_recovery: 2,
        score: 100,
        pokemon: { id: 25, name: 'Pikachu', image_url: 'https://example.com/pikachu.png' },
      };

      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await api.makeGuess(gameId, request);

      expect(fetch).toHaveBeenCalledWith(`/games/${gameId}/guess`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });
      expect(result).toEqual(mockResponse);
    });

    it('throws error with response text on non-ok response', async () => {
      const gameId = 'game-123';
      const request: GuessRequest = { pokemon_name: 'InvalidPokemon' };

      vi.mocked(fetch).mockResolvedValue({
        ok: false,
        statusText: 'Bad Request',
        text: async () => 'Pokemon not found',
      } as Response);

      await expect(api.makeGuess(gameId, request)).rejects.toThrow('Pokemon not found');
    });

    it('throws error with statusText when response text is empty', async () => {
      const gameId = 'game-123';
      const request: GuessRequest = { pokemon_name: 'InvalidPokemon' };

      vi.mocked(fetch).mockResolvedValue({
        ok: false,
        statusText: 'Internal Server Error',
        text: async () => '',
      } as Response);

      await expect(api.makeGuess(gameId, request)).rejects.toThrow('Failed to make guess: Internal Server Error');
    });
  });

  describe('consultHint', () => {
    it('sends correct request and returns response', async () => {
      const gameId = 'game-123';
      const request: ConsultRequest = { hint_type: 'primary_type' };
      const mockResponse: GameResponse = {
        id: gameId,
        created_at: '2026-02-09T12:00:00Z',
        is_won: false,
        is_over: false,
        attempts_remaining: 5,
        attempts: [],
        hints: [{ type: 'primary_type', primary_type: 'Electric' }],
        available_hints: [],
        battery: 8,
        max_battery: 10,
        battery_recovery: 2,
        score: null,
        pokemon: null,
      };

      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await api.consultHint(gameId, request);

      expect(fetch).toHaveBeenCalledWith(`/games/${gameId}/consult`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });
      expect(result).toEqual(mockResponse);
    });

    it('throws error with response text on non-ok response', async () => {
      const gameId = 'game-123';
      const request: ConsultRequest = { hint_type: 'stat' };

      vi.mocked(fetch).mockResolvedValue({
        ok: false,
        statusText: 'Bad Request',
        text: async () => 'Insufficient battery',
      } as Response);

      await expect(api.consultHint(gameId, request)).rejects.toThrow('Insufficient battery');
    });

    it('throws error with statusText when response text is empty', async () => {
      const gameId = 'game-123';
      const request: ConsultRequest = { hint_type: 'stat' };

      vi.mocked(fetch).mockResolvedValue({
        ok: false,
        statusText: 'Internal Server Error',
        text: async () => '',
      } as Response);

      await expect(api.consultHint(gameId, request)).rejects.toThrow('Failed to consult hint: Internal Server Error');
    });
  });
});
