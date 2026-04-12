"""
Core game logic for Friday Night Funkin' Lightweight
"""
import pygame
import json
from enum import Enum
from pathlib import Path
from src.logging_utils import get_debug_logger, get_user_logger, load_project_config
from src.resources import get_resource_path
from src.sprites import Note, HitZone, Character, NoteType, FloatingScore
from src.settings import Settings
from src.menu import MenuScreen, OptionsScreen, PlayMenu, SongListMenu, WeekListMenu
from src.week_manager import WeekManager, ChartManager


SUPPORTED_AUDIO_EXTENSIONS = (".mp3", ".ogg", ".wav")
user_logger = get_user_logger("game")
debug_logger = get_debug_logger("game")

class GameState(Enum):
    """Game states"""
    MENU = 0
    OPTIONS = 1
    PLAYING = 2
    PAUSED = 3
    PLAY_MENU = 4
    FREE_PLAY = 5
    STORY_MODE = 6
    QUIT = 7

class Game:
    def __init__(self):
        """Initialize the game"""
        self.config_path = get_resource_path("data", "config.json")
        self.load_config()
        
        self.screen = pygame.display.set_mode(
            (self.config['window']['width'], self.config['window']['height'])
        )
        pygame.display.set_caption("Friday Night Funkin' Lightweight")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize settings
        self.settings = Settings()
        self.apply_keybinds()
        
        # Initialize game state
        self.game_state = GameState.MENU
        self.init_game_state()
        
        # Setup sprites for game
        self.setup_sprites()
        
        # Initialize managers
        self.week_manager = WeekManager()
        self.chart_manager = ChartManager()
        
        # Ensure at least one week exists
        if not self.week_manager.get_week_names():
            self.week_manager.create_default_week()
        
        # Initialize menu screens
        self.menu_screen = MenuScreen(
            on_play=self.start_game,
            on_options=self.show_options,
            on_quit=self.quit_game
        )
        self.options_screen = None
        self.play_menu = None
        self.free_play_menu = None
        self.story_mode_menu = None
        self.current_week = None
        
    def apply_keybinds(self):
        """Apply saved keybinds to key_map"""
        key_names = {
            "a": pygame.K_a,
            "s": pygame.K_s,
            "w": pygame.K_w,
            "d": pygame.K_d,
        }
        
        self.key_map = {}
        keybinds = self.settings.get("keybinds", {})
        
        for i, (action, default_key) in enumerate([
            ("left", "a"),
            ("down", "s"),
            ("up", "w"),
            ("right", "d"),
        ]):
            key_name = keybinds.get(action, default_key)
            key_code = key_names.get(key_name, pygame.K_a)
            self.key_map[key_code] = i
        
    def load_config(self):
        """Load configuration from JSON"""
        self.config = load_project_config(self.config_path)
        debug_logger.debug("Configuration de jeu chargee depuis %s", self.config_path)
            
    def init_game_state(self):
        """Initialize game state variables"""
        self.current_song_time = 0
        self.song_start_time = 0
        self.playing = False
        self.paused = False
        self.spawned_notes = set()
        self.current_audio_path = None
        self.audio_loaded = False
        self.audio_started = False
        
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.accuracy = 0.0
        self.hit_count = {"perfect": 0, "great": 0, "good": 0, "bad": 0, "miss": 0}
        
        self.keys_pressed = [False] * 4  # LEFT, DOWN, UP, RIGHT
    
    def start_game(self):
        """Start a new game from menu - show play menu"""
        self.show_play_menu()
    
    def start_free_play(self):
        """Show free play menu"""
        self.game_state = GameState.FREE_PLAY
    
    def start_story_mode(self):
        """Show story mode menu"""
        self.game_state = GameState.STORY_MODE
    
    def play_song(self, song_name):
        """Start playing a specific song"""
        self.stop_song_playback()
        self.init_game_state()
        self.setup_sprites()
        chart_path = get_resource_path("data", "charts", f"{song_name}.json")
        if chart_path.exists():
            with open(chart_path, 'r', encoding="utf-8") as f:
                self.chart = json.load(f)
            debug_logger.info("Chart charge: %s", chart_path)
        else:
            debug_logger.warning(
                "Chart introuvable pour '%s', chargement du chart par defaut.", song_name
            )
            self.load_chart()
        self.load_song_audio(song_name)
        self.game_state = GameState.PLAYING

    def get_music_volume(self):
        """Return the configured music volume as a pygame float."""
        def normalize(value, default):
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                numeric = default
            return max(0.0, min(100.0, numeric))

        master = normalize(self.settings.get("volume.master", 70), 70)
        music = normalize(self.settings.get("volume.music", 70), 70)
        return (master / 100.0) * (music / 100.0)

    def ensure_mixer_ready(self):
        """Initialize pygame mixer when audio playback is requested."""
        if pygame.mixer.get_init():
            return True

        try:
            pygame.mixer.init()
            return True
        except pygame.error as error:
            user_logger.warning("Audio indisponible, lecture du chart en mode muet.")
            debug_logger.warning("Initialisation audio impossible: %s", error)
            return False

    def find_song_audio_path(self, song_name):
        """Find the audio file matching a chart or its optional audio field."""
        song_dir = get_resource_path("assets", "Songs")
        candidates = []

        def add_candidate(path):
            if path not in candidates:
                candidates.append(path)

        explicit_audio = self.chart.get("audio")
        if explicit_audio:
            explicit_path = Path(explicit_audio)
            if explicit_path.is_absolute():
                user_logger.warning("Chemin audio absolu ignore dans le chart.")
                debug_logger.warning(
                    "Chemin audio absolu ignore pour '%s': %s",
                    song_name,
                    explicit_audio,
                )
            elif explicit_path.suffix:
                add_candidate(get_resource_path(*explicit_path.parts))
                if len(explicit_path.parts) == 1:
                    add_candidate(song_dir / explicit_path.name)
            else:
                relative_base = get_resource_path(*explicit_path.parts)
                for extension in SUPPORTED_AUDIO_EXTENSIONS:
                    add_candidate(relative_base.with_suffix(extension))
                    if len(explicit_path.parts) == 1:
                        add_candidate(song_dir / f"{explicit_audio}{extension}")

        chart_names = [song_name, self.chart.get("name")]
        for chart_name in chart_names:
            if not chart_name:
                continue
            for extension in SUPPORTED_AUDIO_EXTENSIONS:
                add_candidate(song_dir / f"{chart_name}{extension}")

        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    def load_song_audio(self, song_name):
        """Load the audio file for the current chart when available."""
        self.stop_song_playback()
        self.current_audio_path = self.find_song_audio_path(song_name)
        self.audio_loaded = False
        self.audio_started = False

        if not self.current_audio_path:
            user_logger.warning("Aucun fichier audio trouve pour le chart '%s'.", song_name)
            debug_logger.warning(
                "Audio introuvable pour '%s' dans assets/Songs ou via le champ audio.",
                song_name,
            )
            return

        if not self.ensure_mixer_ready():
            return

        try:
            pygame.mixer.music.load(str(self.current_audio_path))
            pygame.mixer.music.set_volume(self.get_music_volume())
            self.audio_loaded = True
            user_logger.info("Audio charge: %s", self.current_audio_path.name)
            debug_logger.info("Audio charge depuis %s", self.current_audio_path)
        except pygame.error as error:
            user_logger.warning("Impossible de charger l'audio du chart '%s'.", song_name)
            debug_logger.warning(
                "Chargement audio echoue pour %s: %s",
                self.current_audio_path,
                error,
            )
            self.current_audio_path = None

    def start_song_playback(self):
        """Start or resume chart timing and music playback."""
        if self.audio_loaded:
            try:
                pygame.mixer.music.set_volume(self.get_music_volume())
                if self.audio_started and self.paused:
                    pygame.mixer.music.unpause()
                elif not self.audio_started:
                    pygame.mixer.music.play()
                    self.audio_started = True
            except pygame.error as error:
                user_logger.warning("Audio coupe, le chart continue en mode muet.")
                debug_logger.warning("Lecture audio interrompue: %s", error)
                self.audio_loaded = False

        self.playing = True
        self.paused = False

    def pause_song_playback(self):
        """Pause chart timing and music playback."""
        if self.audio_loaded and self.audio_started:
            try:
                pygame.mixer.music.pause()
            except pygame.error as error:
                debug_logger.warning("Pause audio impossible: %s", error)
        self.playing = False
        self.paused = True

    def stop_song_playback(self):
        """Stop music playback and leave gameplay state cleanly."""
        if self.audio_loaded and pygame.mixer.get_init():
            try:
                pygame.mixer.music.stop()
            except pygame.error as error:
                debug_logger.warning("Arret audio impossible: %s", error)
        self.playing = False
        self.paused = False
        self.audio_loaded = False
        self.audio_started = False
        self.current_audio_path = None
    
    def show_play_menu(self):
        """Show the play menu (Free Play / Story Mode)"""
        self.play_menu = PlayMenu(
            on_free_play=self.show_free_play,
            on_story_mode=self.show_story_mode,
            on_back=self.back_to_menu
        )
        self.game_state = GameState.PLAY_MENU
    
    def show_free_play(self):
        """Show free play song selection"""
        songs = self.chart_manager.get_chart_names()
        self.free_play_menu = SongListMenu(
            songs=songs,
            on_song_select=lambda s: self.play_song(self.chart_manager.get_chart_file(s)),
            on_back=self.show_play_menu
        )
        self.game_state = GameState.FREE_PLAY
    
    def show_story_mode(self):
        """Show story mode week selection"""
        weeks = self.week_manager.get_week_names()
        self.story_mode_menu = WeekListMenu(
            weeks=weeks,
            on_week_select=self.play_week,
            on_back=self.show_play_menu
        )
        self.game_state = GameState.STORY_MODE
    
    def play_week(self, week_name):
        """Play a week from story mode"""
        week = self.week_manager.get_week(week_name)
        if week and week.songs:
            self.current_week = week
            # Play the first song in the week
            debug_logger.info("Lecture de la week '%s'", week_name)
            self.play_song(self.chart_manager.get_chart_file(week.songs[0]))
    
    def show_options(self):
        """Show options menu"""
        self.options_screen = OptionsScreen(
            on_back=self.back_to_menu,
            settings=self.settings
        )
        self.game_state = GameState.OPTIONS
    
    def back_to_menu(self):
        """Go back to main menu"""
        if self.options_screen:
            self.options_screen.save_settings()
        self.apply_keybinds()  # Reapply keybinds after options
        self.game_state = GameState.MENU
    
    def quit_game(self):
        """Quit the game"""
        self.stop_song_playback()
        self.running = False
        self.game_state = GameState.QUIT
        
    def load_chart(self):
        """Load song chart"""
        chart_path = get_resource_path("data", "charts", "test_song.json")
        
        if not chart_path.exists():
            # Create default chart
            self.chart = {
                "name": "Test Song",
                "bpm": 120,
                "offset": 0,
                "notes": [
                    {"time": 1000, "lane": 0},
                    {"time": 1500, "lane": 1},
                    {"time": 2000, "lane": 2},
                    {"time": 2500, "lane": 3},
                    {"time": 3000, "lane": 0},
                    {"time": 3500, "lane": 1},
                ]
            }
            self.save_chart(chart_path, self.chart)
        else:
            with open(chart_path, 'r', encoding="utf-8") as f:
                self.chart = json.load(f)
            debug_logger.debug("Chart par defaut charge depuis %s", chart_path)
                
    def save_chart(self, path, chart):
        """Save chart to file"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding="utf-8") as f:
            json.dump(chart, f, indent=2)
        debug_logger.info("Chart sauvegarde: %s", path)
    
    def setup_sprites(self):
        """Setup sprite groups and characters"""
        self.all_sprites = pygame.sprite.Group()
        self.notes_group = pygame.sprite.Group()
        self.hit_zones_group = pygame.sprite.Group()
        self.ui_group = pygame.sprite.Group()
        
        # Setup hit zones (where player hits notes)
        self.lane_width = self.config['window']['width'] / self.config['lanes']
        self.hit_zone_y = self.config['window']['height'] - 150
        
        self.hit_zones = []
        for lane in range(self.config['lanes']):
            x = (lane + 0.5) * self.lane_width
            zone = HitZone(x, self.hit_zone_y, self.config['note_size'])
            self.hit_zones.append((x, zone))
            self.all_sprites.add(zone)
            self.hit_zones_group.add(zone)
        
        # Setup player and opponent
        self.player = Character(self.config['window']['width'] * 0.75, 300, "player")
        self.opponent = Character(self.config['window']['width'] * 0.25, 300, "enemy")
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.opponent)
        
        self.floating_scores = pygame.sprite.Group()
        
    def handle_events(self):
        """Handle user input and window events"""
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
        
        if self.game_state == GameState.MENU:
            self.menu_screen.handle_events(events)
        elif self.game_state == GameState.OPTIONS:
            self.options_screen.handle_events(events)
        elif self.game_state == GameState.PLAY_MENU:
            self.play_menu.handle_events(events)
        elif self.game_state == GameState.FREE_PLAY:
            self.free_play_menu.handle_events(events)
        elif self.game_state == GameState.STORY_MODE:
            self.story_mode_menu.handle_events(events)
        elif self.game_state == GameState.PLAYING:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.stop_song_playback()
                        self.game_state = GameState.MENU
                    elif event.key == pygame.K_SPACE:
                        if self.playing:
                            self.pause_song_playback()
                        else:
                            self.start_song_playback()
                    elif event.key in self.key_map:
                        lane = self.key_map[event.key]
                        self.keys_pressed[lane] = True
                        self.try_hit_notes(lane)
                        
                elif event.type == pygame.KEYUP:
                    if event.key in self.key_map:
                        lane = self.key_map[event.key]
                        self.keys_pressed[lane] = False
    
    def try_hit_notes(self, lane):
        """Check if player hit any notes in the given lane"""
        perfect_range = self.config['gameplay']['perfect_range']
        great_range = self.config['gameplay']['great_range']
        good_range = self.config['gameplay']['good_range']
        bad_range = self.config['gameplay']['bad_range']
        
        best_note = None
        best_offset = float('inf')
        
        for note in self.notes_group:
            if note.hit or note.missed or note.note_type.value != lane:
                continue
                
            offset = note.get_offset(self.current_song_time)
            
            if offset < best_offset and offset < bad_range:
                best_note = note
                best_offset = offset
        
        if best_note:
            best_note.hit = True
            
            # Determine hit quality
            if best_offset < perfect_range:
                quality = "perfect"
                points = self.config['scoring']['perfect']
                color = (0, 255, 0)
            elif best_offset < great_range:
                quality = "great"
                points = self.config['scoring']['great']
                color = (100, 255, 100)
            elif best_offset < good_range:
                quality = "good"
                points = self.config['scoring']['good']
                color = (255, 255, 0)
            else:
                quality = "bad"
                points = self.config['scoring']['bad']
                color = (255, 100, 0)
            
            self.hit_count[quality] += 1
            self.score += points
            self.combo += 1
            if self.combo > self.max_combo:
                self.max_combo = self.combo
            
            # Show floating score
            x, zone = self.hit_zones[lane]
            score_display = FloatingScore(x, self.hit_zone_y, quality.upper(), color)
            self.all_sprites.add(score_display)
            self.floating_scores.add(score_display)
            
            # Opponent animation
            self.opponent.play_animation(f"hit_{lane}")
    
    def spawn_notes(self):
        """Spawn notes based on chart and current time"""
        gameplay_config = self.config['gameplay']
        approach_time_ms = max(1, int(gameplay_config.get("note_approach_time_ms", 1500)))
        note_config = {
            **gameplay_config,
            "note_size": self.config["note_size"],
            "hit_zone_y": self.hit_zone_y,
        }
        
        for note_data in self.chart['notes']:
            try:
                note_time = int(note_data['time'])
                lane = int(note_data['lane'])
            except (KeyError, TypeError, ValueError):
                debug_logger.warning("Note invalide ignoree: %s", note_data)
                continue

            if lane < 0 or lane >= self.config['lanes']:
                debug_logger.warning("Lane invalide ignoree pour la note: %s", note_data)
                continue
            
            # Check if this note should be spawned
            time_until_hit = note_time - self.current_song_time
            
            note_id = (note_time, lane)
            if note_id not in self.spawned_notes and 0 <= time_until_hit <= approach_time_ms:
                note = Note(
                    self.hit_zones[lane][0],
                    self.hit_zone_y - gameplay_config['spawn_distance'],
                    NoteType(lane),
                    note_time,
                    note_config
                )
                self.all_sprites.add(note)
                self.notes_group.add(note)
                self.spawned_notes.add(note_id)
    
    def update(self):
        """Update game logic"""
        if self.game_state == GameState.MENU:
            self.menu_screen.update()
        elif self.game_state == GameState.OPTIONS:
            self.options_screen.update()
        elif self.game_state == GameState.PLAY_MENU:
            self.play_menu.update()
        elif self.game_state == GameState.FREE_PLAY:
            self.free_play_menu.update()
        elif self.game_state == GameState.STORY_MODE:
            self.story_mode_menu.update()
        elif self.game_state == GameState.PLAYING:
            if self.playing:
                self.current_song_time += self.clock.get_time()
            
            # Spawn notes
            self.spawn_notes()
            
            # Update all sprites
            self.all_sprites.update(self.current_song_time)
            
            # Check for missed notes
            for note in self.notes_group:
                if note.missed and not note.hit and not note.miss_counted:
                    note.miss_counted = True
                    self.hit_count['miss'] += 1
                    self.combo = 0
            
            # Remove dead notes
            for note in self.notes_group.copy():
                if note.rect.y > self.config['window']['height']:
                    note.kill()
            
            # Calculate accuracy
            total_hits = sum(self.hit_count.values())
            if total_hits > 0:
                self.accuracy = (self.hit_count['perfect'] * 100 + 
                               self.hit_count['great'] * 75 + 
                               self.hit_count['good'] * 50) / (total_hits * 100) * 100
    
    def draw(self):
        """Draw all game elements"""
        if self.game_state == GameState.MENU:
            self.menu_screen.draw(self.screen)
        elif self.game_state == GameState.OPTIONS:
            self.options_screen.draw(self.screen)
        elif self.game_state == GameState.PLAY_MENU:
            self.play_menu.draw(self.screen)
        elif self.game_state == GameState.FREE_PLAY:
            self.free_play_menu.draw(self.screen)
        elif self.game_state == GameState.STORY_MODE:
            self.story_mode_menu.draw(self.screen)
        elif self.game_state == GameState.PLAYING:
            self.screen.fill((30, 30, 30))
            
            # Draw sprites
            self.all_sprites.draw(self.screen)
            
            # Draw UI
            self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self):
        """Draw UI elements (score, combo, etc)"""
        font_large = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 36)
        
        # Score
        score_text = font_large.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Combo
        combo_color = (255, 255, 0) if self.combo > 0 else (255, 0, 0)
        combo_text = font_large.render(f"Combo: {self.combo}", True, combo_color)
        self.screen.blit(combo_text, (10, 60))
        
        # Accuracy
        accuracy_text = font_small.render(f"Accuracy: {self.accuracy:.1f}%", True, (200, 200, 255))
        self.screen.blit(accuracy_text, (10, 110))
        
        # Song time
        time_text = font_small.render(
            f"Time: {self.current_song_time / 1000:.1f}s",
            True,
            (200, 200, 200)
        )
        self.screen.blit(time_text, (self.config['window']['width'] - 250, 10))
        
        # Controls hint
        if not self.playing:
            hint_text = pygame.font.Font(None, 32).render(
                "Press SPACE to start | w/a/s/d to play | ESC to quit",
                True,
                (150, 150, 150)
            )
            hint_rect = hint_text.get_rect(center=(
                self.config['window']['width'] / 2,
                self.config['window']['height'] - 30
            ))
            self.screen.blit(hint_text, hint_rect)
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.config['window']['fps'])
