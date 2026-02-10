const es = {
  translation: {
    // Page title & meta
    pageTitle: 'Quien es ese Pokemon?',
    pageDescription: 'Pon a prueba tu conocimiento Pokemon! Adivina el Pokemon misterioso usando pistas.',

    // Home
    'home.title': 'Quien es ese Pokemon?',
    'home.subtitle': 'Pon a prueba tu conocimiento Pokemon! Adivina el Pokemon misterioso usando pistas.',
    'home.chooseDifficulty': 'Elige tu Dificultad',
    'home.easy': 'Facil',
    'home.medium': 'Medio',
    'home.hard': 'Dificil',
    'home.startGame': 'Iniciar Juego',

    // Game
    'game.mysteryPokemon': 'POKEMON MISTERIOSO',
    'game.knownData': 'DATOS CONOCIDOS',
    'game.submitGuess': 'ENVIAR RESPUESTA',
    'game.loading': 'Cargando...',
    'game.errorStartGame': 'Error al iniciar el juego',
    'game.errorGuess': 'Error al enviar respuesta',
    'game.errorHint': 'Error al consultar pista',

    // Game Over
    'gameOver.scanComplete': 'ESCANEO COMPLETO',
    'gameOver.scanFailed': 'ESCANEO FALLIDO',
    'gameOver.identified': 'POKEMON IDENTIFICADO EXITOSAMENTE',
    'gameOver.unsuccessful': 'IDENTIFICACION FALLIDA',
    'gameOver.finalScore': 'PUNTUACION FINAL',
    'gameOver.newScan': 'NUEVO ESCANEO',

    // HintShop
    'hintShop.title': 'SOLICITAR NUEVOS DATOS',
    'hintShop.used': 'USADA',
    'hintShop.lowPwr': 'BAJA PWR',

    // Hint labels (from hintConfig)
    'hint.randomStat': 'Stat Aleatorio',
    'hint.primaryType': 'Tipo Primario',
    'hint.secondaryType': 'Tipo Secundario',
    'hint.evolutionStatus': 'Estado de Evolucion',
    'hint.typeEffectiveness': 'Efectividad de Tipo',

    // HintCard
    'hintCard.primaryType': 'Tipo Primario',
    'hintCard.secondaryType': 'Tipo Secundario',
    'hintCard.none': 'Ninguno',
    'hintCard.fullyEvolved': 'Totalmente Evolucionado',
    'hintCard.notFullyEvolved': 'No Totalmente Evolucionado',
    'hintCard.allRevealed': 'Todas las debilidades y resistencias reveladas!',

    // Stat labels
    'stat.hp': 'PS',
    'stat.attack': 'Ataque',
    'stat.defense': 'Defensa',
    'stat.sp_attack': 'At. Esp',
    'stat.sp_defense': 'Df. Esp',
    'stat.speed': 'Velocidad',

    // Indicators
    'indicator.pwr': 'PWR',
    'indicator.tries': 'INTENTOS',

    // Search
    'search.placeholder': 'Buscar Pokemon...',
    'search.loadError': 'Error al cargar la lista de Pokemon. Recarga la pagina.',
  },
} as const;

export default es;
