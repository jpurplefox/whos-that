import { useState } from 'react';
import type { Difficulty, GameResponse } from './types/api';
import { api } from './services/api';
import { Home } from './components/Home';
import { Game } from './components/Game';
import { GameOver } from './components/GameOver';
import './App.css';

type GameState = 'home' | 'playing' | 'game-over';

function App() {
  const [gameState, setGameState] = useState<GameState>('home');
  const [currentGame, setCurrentGame] = useState<GameResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleStartGame = async (difficulty: Difficulty) => {
    setIsLoading(true);
    setError(null);

    try {
      const game = await api.createGame({ difficulty });
      setCurrentGame(game);
      setGameState('playing');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start game');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGameOver = () => {
    setGameState('game-over');
  };

  const handlePlayAgain = () => {
    setCurrentGame(null);
    setGameState('home');
    setError(null);
  };

  return (
    <div className="app">
      <div className="container">
        {isLoading && <div className="loading">Loading...</div>}

        {error && <div className="error">{error}</div>}

        {!isLoading && gameState === 'home' && (
          <Home onStartGame={handleStartGame} />
        )}

        {!isLoading && gameState === 'playing' && currentGame && (
          <Game initialGame={currentGame} onGameOver={handleGameOver} />
        )}

        {!isLoading && gameState === 'game-over' && currentGame && (
          <GameOver game={currentGame} onPlayAgain={handlePlayAgain} />
        )}
      </div>
    </div>
  );
}

export default App;
