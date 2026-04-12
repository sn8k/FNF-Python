# FNF Lightweight Python Game - Project Instructions

This is a lightweight Friday Night Funkin' game built with Python and Pygame with a complete menu system, story mode support, and chart/week editors.

## Project Overview

**important** : AGENTS.md has the final word on every word in this document. Agents.md must be followed.

A modular, sprite-placeholder-ready implementation of FNF with:
- Complete menu navigation system
- Hit note gameplay system
- Free Play and Story Mode support
- Level pack (week) system with editor
- Chart editor for custom songs
- Scoring and accuracy tracking
- Opponent animations
- Custom chart system
- Fully customizable sprites and keybinds

## Key Files

- `main.py` - Game entry point
- `src/game.py` - Core game logic and state management
- `src/menu.py` - All menu screens (Main, Play, Free Play, Story Mode, Options)
- `src/sprites.py` - All sprite classes (Note, Character, UI elements)
- `src/settings.py` - Settings/preferences management
- `src/chart_editor.py` - Chart editor tool for creating songs
- `src/week_manager.py` - Week/level pack management system
- `src/week_editor.py` - Week editor tool for creating story mode packs
- `data/config.json` - Game configuration
- `data/settings.json` - User settings
- `data/charts/` - Song chart files (JSON format)
- `data/weeks/` - Level pack files

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```
Requires: Python 3.7+, Pygame 2.5.0

### 2. Run the Game
```bash
python main.py
```

### 3. Play
- **PLAY Menu** → Choose Free Play or Story Mode
  - **Free Play**: Select any song
  - **Story Mode**: Select a week (level pack)
- **W/A/S/D**: Hit notes in 4 lanes
- **SPACE**: Start/pause
- **ESC**: Return to menu

### 4. Create Content
```bash
# Create custom charts/songs
python -m src.chart_editor

# Create level packs/weeks
python -m src.week_editor
```

## Menu Navigation

```
Main Menu
├── PLAY
│   ├── FREE PLAY → Select Song → Play
│   └── STORY MODE → Select Week → Play
├── OPTIONS
│   ├── Volume Control (Master, Music, Effects)
│   ├── Keybind Configuration (W/A/S/D)
│   ├── Scroll Mode (Downscroll, Upscroll, Sidescroll)
│   └── Reset to Defaults
└── QUIT
```

## Game Features

- **Main Menu**: Navigate between Play, Options, and Quit
- **Play Menu**: Choose between Free Play or Story Mode
- **Free Play**: Play any individual song
- **Story Mode**: Play through organized level packs with multiple songs
- **Week Editor**: Create and manage custom level packs
- **Chart Editor**: Create custom song charts
- **Options Menu**: Customize everything (volume, keybinds, scroll mode)
- **Settings Persistence**: All settings saved to JSON

## Sprite Customization

All sprites are currently simple colored rectangles or placeholder images. Replace them:

1. **Notes** - Colored rectangles (see src/sprites.py)
2. **Characters** - Loaded from `assets/sprites/Characters/`
   - Player sprites: `assets/sprites/Characters/Player/`
   - Enemy sprites: `assets/sprites/Characters/EnemyTest/`
3. **Backgrounds** - Menu backgrounds in `assets/sprites/MenuBackGrounds/`
   - Main Menu: Sticky.png
   - Play Menu & Selections: Drako.png

## Configuration

Edit `data/config.json` to adjust:
- Window size, FPS
- Hit timing windows (perfect, great, good, bad)
- Note spawn distance
- Scoring values

## Adding Content

### Add a Song
1. Use chart editor: `python -m src.chart_editor`
2. Create notes on the timeline
3. Save as `data/charts/song_name.json`
4. Song appears in Free Play menu

### Add a Week (Level Pack)
1. Use week editor: `python -m src.week_editor`
2. Select songs to add to the week
3. Choose a background
4. Save with a week name
5. Week appears in Story Mode menu

## Code Structure

- **Game Loop**: `src/game.py` - Handles state management and main loop
- **Sprite System**: `src/sprites.py` - All drawable objects
- **Menu System**: `src/menu.py` - All UI screens and components
- **Settings System**: `src/settings.py` - Preference management
- **Week System**: `src/week_manager.py` - Level pack management
- **Editors**: `src/chart_editor.py` and `src/week_editor.py` - Content creation tools

## Next Steps

1. Draw custom sprites for notes and characters
2. Add music/sound playback
3. Create multiple weeks for story mode
4. Add difficulty levels
5. Implement smooth animations
6. Add more visual effects

Ready to play and create!
