import { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import type { Difficulty, GameResponse } from './types/api';
import { api } from './services/api';
import { trackAppOpened, trackGameStarted, isReturningUser } from './services/analytics';
import { useAuth } from './contexts/AuthContext';
import { Home } from './components/Home';
import { Game } from './components/Game';
import { GameOver } from './components/GameOver';
import { HeaderBar } from './components/HeaderBar';
import './App.css';

type GameState = 'home' | 'playing' | 'game-over';

function App() {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const [gameState, setGameState] = useState<GameState>('home');
  const [currentGame, setCurrentGame] = useState<GameResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [difficulty, setDifficulty] = useState<Difficulty>('easy');
  const sessionGameNumberRef = useRef(0);

  useEffect(() => {
    document.title = t('pageTitle');
    const meta = document.querySelector('meta[name="description"]');
    if (meta) {
      meta.setAttribute('content', t('pageDescription'));
    }
  }, [t, i18n.language]);

  const prevUserRef = useRef(user);
  useEffect(() => {
    if (prevUserRef.current && !user && gameState === 'playing') {
      setCurrentGame(null);
      setGameState('home');
    }
    prevUserRef.current = user;
  }, [user, gameState]);

  useEffect(() => {
    const referrer = document.referrer
      ? new URL(document.referrer).origin
      : '';
    trackAppOpened({
      language: i18n.language,
      referrer,
      is_returning_user: isReturningUser(),
    });
  }, []);

  const handleStartGame = async (selectedDifficulty: Difficulty) => {
    setIsLoading(true);
    setError(null);
    setDifficulty(selectedDifficulty);

    try {
      const game = await api.createGame({ difficulty: selectedDifficulty });
      setCurrentGame(game);
      setGameState('playing');

      sessionGameNumberRef.current += 1;
      trackGameStarted({
        difficulty: selectedDifficulty,
        game_id: game.id!,
        initial_battery: game.battery,
        max_attempts: game.attempts_remaining,
        session_game_number: sessionGameNumberRef.current,
      });
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
      <HeaderBar />
      <div className="pokedex-device">
        <div className="container">
          {isLoading && <div className="loading">{t('game.loading')}</div>}

          {error && <div className="error">{error}</div>}

          {!isLoading && gameState === 'home' && (
            <Home onStartGame={handleStartGame} />
          )}

          {!isLoading && gameState === 'playing' && currentGame && (
            <Game initialGame={currentGame} onGameOver={handleGameOver} difficulty={difficulty} />
          )}

          {!isLoading && gameState === 'game-over' && currentGame && (
            <GameOver
              game={currentGame}
              onPlayAgain={handlePlayAgain}
              difficulty={difficulty}
              gamesPlayedThisSession={sessionGameNumberRef.current}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
