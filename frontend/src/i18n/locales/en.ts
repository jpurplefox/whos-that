const en = {
  translation: {
    // Page title & meta
    pageTitle: "Who's That Pokemon?",
    pageDescription: 'Test your Pokemon knowledge! Guess the mystery Pokemon using hints.',

    // Home
    'home.title': "Who's That Pokemon?",
    'home.subtitle': 'Test your Pokemon knowledge! Guess the mystery Pokemon using hints.',
    'home.chooseDifficulty': 'Choose Your Difficulty',
    'home.easy': 'Easy',
    'home.medium': 'Medium',
    'home.hard': 'Hard',
    'home.startGame': 'Start Game',

    // Game
    'game.mysteryPokemon': 'MYSTERY POKEMON',
    'game.knownData': 'KNOWN DATA',
    'game.submitGuess': 'SUBMIT GUESS',
    'game.analyzing': 'ANALYZING DATA...',
    'game.loading': 'Loading...',
    'game.errorStartGame': 'Failed to start game',
    'game.errorGuess': 'Failed to make guess',
    'game.errorHint': 'Failed to consult hint',

    // Game Over
    'gameOver.scanComplete': 'SCAN COMPLETE',
    'gameOver.scanFailed': 'SCAN FAILED',
    'gameOver.identified': 'POKEMON SUCCESSFULLY IDENTIFIED',
    'gameOver.unsuccessful': 'IDENTIFICATION UNSUCCESSFUL',
    'gameOver.finalScore': 'FINAL SCORE',
    'gameOver.newScan': 'NEW SCAN',

    // HintShop
    'hintShop.title': 'REQUEST NEW DATA',
    'hintShop.used': 'USED',
    'hintShop.lowPwr': 'LOW PWR',

    // Hint labels (from hintConfig)
    'hint.randomStat': 'Random Stat',
    'hint.primaryType': 'Primary Type',
    'hint.secondaryType': 'Secondary Type',
    'hint.evolutionStatus': 'Evolution Status',
    'hint.typeEffectiveness': 'Type Effectiveness',
    'hint.pokemonMoves': 'Moves',

    // HintCard
    'hintCard.primaryType': 'Primary Type',
    'hintCard.secondaryType': 'Secondary Type',
    'hintCard.none': 'None',
    'hintCard.fullyEvolved': 'Fully Evolved',
    'hintCard.notFullyEvolved': 'Not Fully Evolved',
    'hintCard.allRevealed': 'All weaknesses & resistances revealed!',
    'hintCard.weakness': 'Weak to',
    'hintCard.resistance': 'Resists',
    'hintCard.immunity': 'Immune to',
    'hintCard.move': 'Move',
    'hintCard.allMovesRevealed': 'All moves revealed!',

    // Stat labels
    'stat.hp': 'HP',
    'stat.attack': 'Attack',
    'stat.defense': 'Defense',
    'stat.sp_attack': 'Sp. Atk',
    'stat.sp_defense': 'Sp. Def',
    'stat.speed': 'Speed',

    // Indicators
    'indicator.pwr': 'PWR',
    'indicator.tries': 'TRIES',

    // Search
    'search.placeholder': 'Search Pokemon...',
    'search.loadError': 'Failed to load Pokemon list. Please reload.',

    // Auth
    'auth.signIn': 'Sign in',
    'auth.signOut': 'Sign out',
    'auth.signingIn': 'Linking...',
    'auth.popupBlocked': 'Please allow popups for this site',
    'auth.loginFailed': 'Login failed. Please try again.',
  },
} as const;

export default en;
