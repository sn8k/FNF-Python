# Friday Night Funkin' Lightweight

A lightweight Python Pygame implementation of Friday Night Funkin' with basic game mechanics and modular design for easy sprite customization.

## Features

- **Hit Note System**: Fall-down notes that spawn based on chart timing
- **Scoring System**: Perfect, Great, Good, Bad, and Miss ratings
- **Combo Counter**: Track consecutive hit streaks
- **Accuracy Tracking**: Real-time accuracy percentage
- **Player Animations**: Right-side player character responds to successful hits
- **Chart System**: Custom song charts with JSON support
- **Chart Editor**: Simple built-in GUI editor for creating custom charts
- **Main Menu System**: Navigate between Play, Options, and Quit
- **Animated Frontpage Title**: Main menu logo gently moves to draw the eye
- **Intro Screen**: A skippable furry lama intro plays before the main menu
- **Play Menu**: Choose between Free Play or Story Mode
- **Free Play**: Select and play any song individually
- **Story Mode**: Play through organized level packs (weeks)
- **Week Editor**: Create and manage custom level packs/weeks
- **Options Menu**: Customize keybinds, scroll mode, display mode, and volume levels
- **Settings Management**: All preferences saved and automatically restored
- **Modular Design**: Separate sprite files ready for custom graphics
- **Drako Background**: Dynamic menu background for play selection

## Project Structure

```
fnf python/
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── requirements-dev.txt    # Build dependencies
├── README.md              # This file
├── scripts/               # Build scripts
├── packaging/             # PyInstaller specs
├── src/
│   ├── __init__.py
│   ├── game.py            # Core game logic and state management
│   ├── sprites.py         # Sprite classes (Note, Character, etc.)
│   ├── menu.py            # Menu screens and UI components
│   ├── settings.py        # Settings/preferences management
│   ├── chart_editor.py    # Chart editor tool
│   ├── week_manager.py    # Week/level pack management system
│   └── week_editor.py     # Week editor tool
├── data/
│   ├── config.json        # Game configuration
│   ├── settings.json      # User settings (created or repaired on launch)
│   ├── charts/            # Song charts (JSON format)
│   │   └── test_song.json # Example chart
│   └── weeks/             # Level packs/weeks
│       └── (created by week editor)
└── assets/
    ├── Songs/             # Song audio files (.mp3, .ogg, .wav)
    └── sprites/
        ├── Characters/    # Player and Enemy sprites
        ├── MenuBackGrounds/ # Menu background images (Sticky.png, Drako.png, etc.)
        └── Stages/        # Stage backgrounds
```

## Installation

### Quick Start (Recommended)

**Windows:**
```bash
install.bat
```

**Linux/Mac:**
```bash
bash install.sh
```

### Manual Installation

If the scripts above don't work:

1. Clone or download this project
2. Install Python 3.7+ from [python.org](https://www.python.org/downloads/) (NOT Microsoft Store version if possible)
3. Install Pygame:

**Option A (Recommended):**
```bash
pip install pygame==2.5.0
```

**Option B (Using --user flag for limited Python installations):**
```bash
pip install --user pygame==2.5.0
```

**Option C (Using Anaconda/Conda):**
```bash
conda install pygame
```

**Option D (If binary wheels fail, upgrade pip first):**
```bash
pip install --upgrade pip
pip install pygame==2.5.0
```

### Troubleshooting

If pygame doesn't install:
- **Windows App Store Python**: The Microsoft Store Python has limited pip write permissions. Try:
  - Installing official Python from [python.org](https://www.python.org)
  - Or use Anaconda: [anaconda.com](https://www.anaconda.com)
  
- **Compilation failures**: If pygame tries building from source, try `--prefer-binary`:
  ```bash
  pip install --prefer-binary pygame
  ```

- **Permission denied errors**: Try with `--user`:
  ```bash
  pip install --user pygame
  ```

## How to Play

### Starting the Game
```bash
python main.py
```

On Windows, `menu.bat` opens a launcher menu with choices for the game, the chart editor, and the latest logs.

### Main Menu
At startup, a skippable intro screen presents a giant furry lama before the main menu appears.

When you launch the game, you'll see the main menu with three options:
- **PLAY** - Access play modes (Free Play or Story Mode)
- **OPTIONS** - Open the settings menu
- **QUIT** - Exit the game

The title on the frontpage has a light idle animation so the menu feels less static.
Type `AVRIL` on the main menu to enable the April easter egg: the **QUIT** button flees from the mouse, stays inside the window, and moves faster when the mouse moves faster.

### Play Menu
After selecting PLAY, choose your mode:
- **FREE PLAY** - Play any individual song from your chart library
- **STORY MODE** - Play through organized level packs (weeks)
- **BACK** - Return to main menu

#### Free Play Mode
- See a list of all available songs
- Select any song to play immediately
- Click BACK to choose a different song or mode
- Press ESC to return to play menu

#### Story Mode
- See a list of all available weeks (level packs)
- Select a week to play its songs in sequence
- Each week can contain multiple songs and enemies
- Press ESC to return to play menu

### Controls During Gameplay
- **A/S/W/D**: Default physical lane keys on QWERTY
- **Q/S/Z/D**: Same default physical lane keys on AZERTY
- **SPACE**: Start/pause the chart and loaded song audio
- **ESC**: Open the pause menu

### Pause Menu
- **RESUME**: Return to the current chart without resetting score, combo, timing or spawned notes
- **OPTIONS**: Open the existing options screen, then return to the pause menu
- **RESTART**: Restart the current chart from zero with a clean gameplay state
- **QUIT**: Stop the current chart and return to the main menu

### Easter Egg
During an active chart, the pause menu, or options opened from pause, enter:

```text
UP, UP, DOWN, DOWN, LEFT, RIGHT, LEFT, RIGHT, B, A
```

The game opens `https://www.youtube.com/watch?v=dQw4w9WgXcQ&autoplay=1` in the default browser and shows `You've been so fuckin rick Rolled dude ! Ahah bad chance`. Browser autoplay can still be blocked by the browser's local policy.
The sequence resets if you leave ingame contexts or if the game window loses focus.

### Options Menu

The Options menu allows you to customize your gameplay experience:

#### Volume Control
Three separate volume sliders:
- **Master Volume**: Overall game volume (0-100)
- **Music Volume**: Song/background music volume (0-100)
- **Effects Volume**: Sound effects volume (0-100)

#### Keybind Configuration
Customize your control scheme by clicking on each key binding:
- **Left, Down, Up, Right**: Click to rebind, then press any key
- The selector will light up while listening for input
- Press ESC or click another binding to cancel
- Gameplay binds follow the physical key position first, so the default layout stays playable on both QWERTY and AZERTY
- If you reuse an existing gameplay bind, the options screen swaps the duplicate so each lane keeps a unique key

#### Scroll Mode
Choose how notes fall on screen:
- **[DOWNSCROLL]** - Notes fall from top to bottom (default)
- **[UPSCROLL]** - Notes rise from bottom to top
- **[SIDESCROLL]** - Notes move from side to side

Click any mode to select it.

#### Display Mode
- **[WINDOWED]** - Run the game in a standard 1280x720 window
- **[FULLSCREEN]** - Run the game in fullscreen using the same base resolution

The selected display mode is saved in `data/settings.json` and applied when you leave the options menu or restart the game.

#### Settings Management
- **BACK Button**: Save your settings and return to main menu
- **RESET Button**: Restore all settings to defaults

All settings are automatically saved when you return to the main menu.

### Gameplay

When you start a game:
1. The game loads the chart JSON and tries to load matching audio from `assets/Songs/`
2. Colored notes fall down the screen
3. Hit each note when it reaches the hit zone (green border)
4. Timing accuracy affects scoring:
   - **Perfect** (25ms): 350 points
   - **Great** (50ms): 200 points
   - **Good** (100ms): 100 points
   - **Bad** (150ms): 0 points
   - **Miss**: 0 points and combo breaks

If no audio file is found, the chart remains playable in muted fallback mode and a warning is written to the logs.

5. Maintain combos for a high score!

## Chart Editor

Create custom songs using the built-in editor:

```bash
python -m src.chart_editor
```

On Windows, `menu.bat` can launch the editor from the same menu as the game.

### Editor Controls
- **Left/Right**: Scroll the timeline
- **Up/Down**: Zoom the timeline
- **Left Click**: Add a note in the clicked lane and snapped time
- **Right Click**: Delete a nearby note in the clicked lane
- **Mouse Wheel**: Scroll the timeline
- **TAB / SHIFT+TAB**: Select next or previous audio file
- **ENTER**: Reload selected audio file
- **P**: Select the next player character folder
- **O**: Select the next enemy character folder
- **SPACE**: Play/pause audio preview when audio is available
- **SHIFT+C**: Clear all notes
- **CTRL+S**: Save chart
- **ESC**: Exit editor

Charts are saved as JSON files in `data/charts/`. The editor saves selected audio in the chart `audio` field, and selected versus characters in `player` and `enemy`.

## Week Manager

Check week and chart discovery from the command line:

```bash
python -m src.week_manager
```

The command lists available weeks from `data/weeks/` and available charts from `data/charts/`.

## Week Editor

Create and manage level packs (weeks) for Story Mode:

```bash
python -m src.week_editor
```

### Week Editor Features
- **Week Name**: Enter a custom name for your week
- **Add Songs**: Select from available charts to add to your week
- **Remove Songs**: Remove the last added song from your week
- **Background Selection**: Choose a background image for your week
- **Save Week**: Save your week to make it available in Story Mode

### Editor Controls
- **Up/Down**: Navigate available songs
- **A**: Add selected song to week
- **R**: Remove last song from week
- **Left/Right**: Change background
- **S**: Save week
- **Click on name field**: Edit week name
- **ESC**: Exit editor

Weeks are saved as JSON files in `data/weeks/`

## Chart File Format

```json
{
  "name": "My Song",
  "audio": "assets/Songs/My Song.mp3",
  "player": "Player",
  "enemy": "EnemyTest",
  "bpm": 120,
  "offset": 0,
  "notes": [
    {"time": 1000, "lane": 0},
    {"time": 1500, "lane": 1},
    {"time": 2000, "lane": 2},
    {"time": 2500, "lane": 3}
  ]
}
```

- **time**: Target hit time in milliseconds
- **lane**: Lane number (0-3 for Left, Down, Up, Right)
- **audio**: Optional relative path or filename for the song audio. If omitted, the game tries `assets/Songs/<chart file name>` and `assets/Songs/<chart name>` with `.mp3`, `.ogg`, then `.wav`.
- **player**: Optional folder name from `assets/sprites/Characters/` for the right-side playable character.
- **enemy**: Optional folder name from `assets/sprites/Characters/` for the left-side opponent.

## Customization

### In-Game Settings Menu
The easiest way to customize everything is through the Options menu:
1. Click **OPTIONS** from the main menu
2. Adjust volume sliders for music and effects
3. Customize your keybinds by clicking each button and pressing a key
4. Select your preferred scroll mode (downscroll, upscroll, or sidescroll)
5. Click **BACK** to save your settings

Your settings are automatically saved to `data/settings.json`, normalized to the latest schema, and restored when you launch the game again.

### Adding Custom Character Sprites
Character sprites are loaded from `assets/sprites/Characters/`:

**Player sprites** go in: `assets/sprites/Characters/Player/`
**Enemy sprites** go in: `assets/sprites/Characters/EnemyTest/`

Required PNG files for each directory:
- `Idle.png` - Idle animation frame
- `Up.png` - Up direction animation
- `Down.png` - Down direction animation
- `Left.png` - Left direction animation
- `Right.png` - Right direction animation

The game will automatically load and use these sprites. The enemy sprite is automatically flipped horizontally.

### Game Configuration

Edit `data/config.json` for advanced settings:

```json
{
  "window": {
    "width": 1280,
    "height": 720,
    "fps": 60
  },
  "gameplay": {
    "spawn_distance": 500,
    "hit_window": 150,
    "perfect_range": 25,
    "great_range": 50,
    "good_range": 100,
    "bad_range": 150,
    "note_approach_time_ms": 1500
  },
  "scoring": {
    "perfect": 350,
    "great": 200,
    "good": 100,
    "bad": 0,
    "miss": 0
  },
  "lanes": 4,
  "note_size": 60,
  "menu": {
    "intro_enabled": true,
    "intro_duration_ms": 2400,
    "title_animation_amplitude_px": 10,
    "title_animation_speed": 0.003,
    "title_rotation_degrees": 2.0,
    "title_scale_amplitude": 0.025,
    "exit_evasion_radius_px": 170,
    "exit_evasion_max_speed_px": 520,
    "exit_evasion_smoothness": 0.18
  },
  "logging": {
    "directory": "logs",
    "user": {
      "enabled": true,
      "level": "INFO",
      "file": "user.log",
      "console": true
    },
    "debug": {
      "enabled": true,
      "level": "DEBUG",
      "file": "debug.log",
      "console": false
    }
  }
}
```

If `data/config.json` is missing, invalid, or incomplete, the launcher recreates it from the built-in defaults and writes the merged result back to disk.

- **spawn_distance**: How far above the hit zone notes appear
- **hit_window**: Total milliseconds for valid hits
- **note_approach_time_ms**: Time notes spend travelling toward the hit zone
- **Hit ranges**: Timing windows for each accuracy level
- **scoring**: Points awarded for each accuracy
- **menu.exit_evasion_radius_px**: Mouse distance that starts the `AVRIL` quit-button evasion
- **menu.exit_evasion_max_speed_px**: Maximum evasion speed contribution
- **menu.exit_evasion_smoothness**: Smooth interpolation factor for the evasive button movement
- **logging.directory**: Folder where log files are written
- **logging.user**: Player-facing logs for important messages
- **logging.debug**: Technical diagnostics for troubleshooting

### Logging Policy

The project now uses two configurable log streams:
- `logs/user.log` for user-facing messages
- `logs/debug.log` for technical diagnostics

Both streams are configured in `data/config.json`. You can enable or disable console output independently for each stream.
On Windows, `menu.bat` can show the last lines of both active log files.

### Settings File

Manual settings are stored in `data/settings.json`:

```json
{
  "keybinds": {
    "left": {
      "key": "a",
      "scancode": 4,
      "display": "A / Q"
    },
    "down": {
      "key": "s",
      "scancode": 22,
      "display": "S"
    },
    "up": {
      "key": "w",
      "scancode": 26,
      "display": "W / Z"
    },
    "right": {
      "key": "d",
      "scancode": 7,
      "display": "D"
    }
  },
  "display": {
    "mode": "windowed"
  },
  "scroll_mode": "downscroll",
  "volume": {
    "master": 70,
    "music": 70,
    "effects": 70
  }
}
```

Existing string-only keybinds are migrated automatically on launch. You can edit this file directly, or use the Options menu (recommended).

## Redistributable Builds

The project can generate Windows redistributables with PyInstaller. Builds use one-folder mode so `assets/`, `data/`, and `DOCS/` remain visible and editable in the output folder.

### Release Build

```bash
scripts\build_release.bat -Clean
```

Outputs:
- `dist/FNF-Python-release/FNF-Python.exe`
- `artifacts/FNF-Python-release.zip`

### Debug Build

```bash
scripts\build_debug.bat -Clean
```

Outputs:
- `dist/FNF-Python-debug/FNF-Python-Debug.exe`
- `artifacts/FNF-Python-debug.zip`

### Build Both Variants

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build.ps1 -Configuration all -Clean
```

The build script installs runtime dependencies from `requirements.txt` and build dependencies from `requirements-dev.txt` unless `-SkipInstall` is passed. Use `-NoArchive` to keep only the folders in `dist/`.

## Future Enhancements

- [ ] Multiple song support with song select screen
- [ ] Difficulty levels
- [ ] Health system
- [ ] Animations for character movements
- [ ] Sound effects for hit/miss feedback
- [ ] Score leaderboards
- [ ] Different game modes (story, free play, etc.)
- [ ] Multiplayer support

## License

Free to use and modify!
