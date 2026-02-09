# Who's That Pokémon? Frontend

A React + TypeScript frontend for the "Who's That Pokémon?" guessing game.

## Features

- Clean, modern Pokémon-themed UI
- Three difficulty levels (Easy, Medium, Hard)
- Real-time hint system with battery management
- Stat comparison visualizations
- Fully responsive design (mobile-first)
- Anonymous play (no authentication required)

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **CSS Modules** - Scoped styling

## Prerequisites

- Node.js 16+ and npm
- Backend API running on `http://localhost:8000`

## Installation

```bash
cd frontend
npm install
```

## Development

Start the development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173` and will proxy API requests to `http://localhost:8000`.

## Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Project Structure

```
frontend/
├── src/
│   ├── components/        # React components
│   │   ├── Home.tsx       # Home screen with difficulty selection
│   │   ├── Game.tsx       # Main game screen
│   │   ├── GameOver.tsx   # Game over screen with results
│   │   └── HintCard.tsx   # Individual hint display component
│   ├── services/
│   │   └── api.ts         # API service for backend communication
│   ├── types/
│   │   └── api.ts         # TypeScript type definitions
│   ├── App.tsx            # Main app component
│   ├── App.css            # Global styles
│   └── main.tsx           # Entry point
├── vite.config.ts         # Vite configuration with proxy
└── package.json
```

## API Endpoints Used

- `POST /games` - Create a new game
- `GET /games/{game_id}` - Get game state
- `POST /games/{game_id}/guess` - Make a guess
- `POST /games/{game_id}/consult` - Consult a hint

## Game Flow

1. **Home Screen**: Select difficulty and start game
2. **Game Screen**:
   - View hints and comparisons
   - Monitor battery level
   - Purchase hints from Pokedex
   - Make guesses
3. **Game Over Screen**:
   - See the revealed Pokémon
   - View final score
   - Play again

## Styling

The app uses a dark theme with Pokémon-inspired colors:
- Primary: Red (#cc0000)
- Secondary: Blue (#3466af)
- Dark background with gradient
- CSS custom properties for consistency

All components use CSS Modules for scoped styling.
