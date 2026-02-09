import type { CreateGameRequest, GameResponse, GuessRequest, ConsultRequest, Pokemon } from '../types/api';

const API_BASE = '';

export const api = {
  async listPokemon(): Promise<Pokemon[]> {
    const response = await fetch(`${API_BASE}/pokemon`);

    if (!response.ok) {
      throw new Error(`Failed to list pokemon: ${response.statusText}`);
    }

    return response.json();
  },

  async createGame(request: CreateGameRequest): Promise<GameResponse> {
    const response = await fetch(`${API_BASE}/games`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to create game: ${response.statusText}`);
    }

    return response.json();
  },

  async getGame(gameId: string): Promise<GameResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}`);

    if (!response.ok) {
      throw new Error(`Failed to get game: ${response.statusText}`);
    }

    return response.json();
  },

  async makeGuess(gameId: string, request: GuessRequest): Promise<GameResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}/guess`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || `Failed to make guess: ${response.statusText}`);
    }

    return response.json();
  },

  async consultHint(gameId: string, request: ConsultRequest): Promise<GameResponse> {
    const response = await fetch(`${API_BASE}/games/${gameId}/consult`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || `Failed to consult hint: ${response.statusText}`);
    }

    return response.json();
  },
};
