# factory-poc3-demo

## Ping Pong 2D (Python stdlib, tkinter)

Jeu de ping-pong 2D jouable en desktop à 800×600 : mode solo contre IA et
mode deux joueurs sur clavier partagé, victoire au premier à 5 points.

### Lancement

```bash
python3 main.py
```

Menu : `1` = Solo vs IA, `2` = 2 Joueurs, `Q` = Quitter.

Contrôles : joueur 1 (gauche) `Z` / `S`, joueur 2 (droite) `↑` / `↓`
(mode 2 joueurs), `P` ou `Espace` = pause.

### Architecture

- `config.py` : dataclass frozen `Config` (constantes typées)
- `entities.py` : modèle physique (`Paddle`, `Ball`)
- `game_state.py` : `GameMode`, `GameStatus`, `Score`
- `ai_controller.py` : `AIController` (mode solo)
- `input_handler.py` : `InputHandler` (entrées clavier)
- `renderer.py` : `Renderer` (canvas tkinter)
- `game_engine.py` : `GameEngine` (boucle et collisions)
- `main.py` : `Application` + `main()`

### Tests

```bash
python3 -m unittest discover -s . -p "test_*.py"
```
