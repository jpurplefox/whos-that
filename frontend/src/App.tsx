import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import type { Difficulty, GameResponse } from './types/api';
import { api } from './services/api';
import { Home } from './components/Home';
import { Game } from './components/Game';
import { GameOver } from './components/GameOver';
import { LanguageSwitcher } from './components/LanguageSwitcher';
import './App.css';

type GameState = 'home' | 'playing' | 'game-over';

function App() {
  const { t, i18n } = useTranslation();
  const [gameState, setGameState] = useState<GameState>('home');
  const [currentGame, setCurrentGame] = useState<GameResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    document.title = t('pageTitle');
    const meta = document.querySelector('meta[name="description"]');
    if (meta) {
      meta.setAttribute('content', t('pageDescription'));
    }
  }, [t, i18n.language]);

  const handleStartGame = async (difficulty: Difficulty) => {
    setIsLoading(true);
    setError(null);

    try {
      const game = await api.createGame({ difficulty });
      setCurrentGame(game);
      setGameState('playing');
    } catch (err) {
      setError(err instanceof Error ? err.message : t('game.errorStartGame'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleGameOver = (finalGame: GameResponse) => {
    setCurrentGame(finalGame);
    setGameState('game-over');
  };

  const handlePlayAgain = () => {
    setCurrentGame(null);
    setGameState('home');
    setError(null);
  };

  return (
    <div className="app">
      <LanguageSwitcher />
      <div className="pokedex-device">
        <div className="container">
          {isLoading && <div className="loading">{t('game.loading')}</div>}

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
    </div>
  );
}

export default App;
