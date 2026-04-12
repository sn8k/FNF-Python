"""
FNF-Style Chart Editor for FNF Lightweight
Run: python -m src.chart_editor
"""
import json
import sys
import pygame
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.chart_compat import get_default_export_path, load_chart_file, serialize_chart
from src.logging_utils import configure_logging, get_debug_logger, get_user_logger
from src.resources import get_project_root, get_resource_path


configure_logging()
user_logger = get_user_logger("chart_editor")
debug_logger = get_debug_logger("chart_editor")

class ChartEditor:
    """FNF-style GUI chart editor with song preview and upscroll playback"""
    def __init__(self, chart_file=None):
        pygame.init()
        self.audio_available = self.init_audio()

        self.chart_file = Path(chart_file or get_resource_path("data", "charts", "test_song.json"))
        self.export_chart_file = self.chart_file

        self.config = {
            "width": 1400,
            "height": 800,
            "lanes": 4,
        }

        self.screen = pygame.display.set_mode(
            (self.config['width'], self.config['height'])
        )
        pygame.display.set_caption("FNF Chart Editor")
        self.clock = pygame.time.Clock()

        self.load_chart()

        self.song_files = self.find_song_files()
        self.character_folders = self.find_character_folders()
        self.selected_song_index = self.get_initial_song_index()
        self.selected_player_index = self.get_initial_character_index("player", "Player")
        self.selected_enemy_index = self.get_initial_character_index("enemy", "EnemyTest")
        self.loaded_song_path = None
        self.song_name = "No song loaded"

        # Editor state
        self.scroll_offset = 0  # Horizontal scroll in milliseconds
        self.bpm = self.chart.get('bpm', 120)
        self.pixels_per_ms = 0.2  # 0.2 pixels per millisecond (adjust for zoom)
        self.snap_grid = 1000 / (self.bpm / 60)  # Snap to beat by default
        self.playing = False
        self.paused = False
        self.current_time_ms = 0
        self.play_start_ticks = 0
        self.preview_mode = "upscroll"
        self.playback_speed = 0.25
        self.running = True

        # UI layout
        self.timeline_height = 60
        self.lane_height = self.config['height'] - self.timeline_height
        self.lane_width = self.config['width'] / self.config['lanes']
        self.lane_colors = [
            (255, 100, 100),  # Left - Red
            (100, 255, 100),  # Down - Green
            (100, 100, 255),  # Up - Blue
            (255, 255, 100),  # Right - Yellow
        ]

        if self.song_files:
            self.load_song(self.selected_song_index)

    def init_audio(self):
        """Initialize audio without blocking the editor if the mixer is unavailable."""
        try:
            pygame.mixer.init()
            return True
        except pygame.error as error:
            user_logger.warning("Audio indisponible, editeur lance sans preview sonore.")
            debug_logger.warning("Initialisation audio de l'editeur impossible: %s", error)
            return False

    def load_chart(self):
        """Load chart from file"""
        if self.chart_file.exists():
            self.chart = load_chart_file(self.chart_file)
            self.export_chart_file = get_default_export_path(self.chart_file, self.chart)
        else:
            self.chart = {
                "name": "New Song",
                "bpm": 120,
                "offset": 0,
                "notes": []
            }
            self.export_chart_file = self.chart_file

    def save_chart(self):
        """Save chart to file"""
        self.update_chart_characters()
        self.export_chart_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.export_chart_file, 'w', encoding="utf-8") as f:
            json.dump(serialize_chart(self.chart), f, indent=2)
        user_logger.info("Chart sauvegarde: %s", self.export_chart_file)

    def find_song_files(self):
        """Find songs in assets/Songs"""
        song_files = []
        search_roots = [
            get_resource_path("assets", "Songs"),
            get_resource_path("test-data", "music"),
        ]
        for song_dir in search_roots:
            if not song_dir.exists():
                continue
            for extension in ("*.mp3", "*.ogg", "*.wav"):
                song_files.extend(sorted(song_dir.rglob(extension)))
        return [str(path) for path in song_files]

    def find_character_folders(self):
        """Find available character folders."""
        character_root = get_resource_path("assets", "sprites", "Characters")
        if not character_root.exists():
            return []
        return [path.name for path in sorted(character_root.iterdir()) if path.is_dir()]

    def get_initial_song_index(self):
        """Prefer the audio declared by the loaded chart when available."""
        audio_path = self.chart.get("audio")
        if not audio_path:
            return 0

        candidate = get_project_root().joinpath(*Path(audio_path).parts)
        candidate_text = str(candidate)
        for index, song_file in enumerate(self.song_files):
            if Path(song_file) == candidate or song_file == candidate_text:
                return index
        return 0

    def get_initial_character_index(self, chart_key, default_name):
        """Return the selected character index for a chart role."""
        if not self.character_folders:
            return 0

        character_name = self.chart.get(chart_key) or default_name
        if character_name in self.character_folders:
            return self.character_folders.index(character_name)
        return 0

    def selected_character(self, index):
        """Return a character folder name by index."""
        if not self.character_folders:
            return None
        return self.character_folders[index % len(self.character_folders)]

    def update_chart_characters(self):
        """Persist selected player/enemy folders in the chart."""
        player = self.selected_character(self.selected_player_index)
        enemy = self.selected_character(self.selected_enemy_index)
        if player:
            self.chart["player"] = player
        if enemy:
            self.chart["enemy"] = enemy

    def set_chart_audio_from_loaded_song(self):
        """Persist the selected preview audio as a project-relative chart audio path."""
        if not self.loaded_song_path:
            return
        loaded_path = Path(self.loaded_song_path)
        try:
            self.chart["audio"] = loaded_path.resolve().relative_to(get_project_root()).as_posix()
        except ValueError:
            self.chart["audio"] = loaded_path.as_posix()

    def load_song(self, index):
        """Load a song from assets/Songs"""
        if index < 0 or index >= len(self.song_files):
            return
        self.loaded_song_path = self.song_files[index]
        self.song_name = Path(self.loaded_song_path).stem
        self.set_chart_audio_from_loaded_song()
        if not self.audio_available:
            self.song_name = f"{self.song_name} (audio disabled)"
            return

        try:
            pygame.mixer.music.load(self.loaded_song_path)
            pygame.mixer.music.set_volume(0.8)
        except pygame.error as e:
            user_logger.warning("Impossible de charger la chanson selectionnee.")
            debug_logger.warning("Chargement audio echoue pour %s: %s", self.loaded_song_path, e)
            self.loaded_song_path = None
            self.song_name = "Failed to load song"

    def start_playback(self):
        """Start or resume audio playback"""
        if not self.audio_available or not self.loaded_song_path:
            return

        if self.playing and not self.paused:
            return

        if self.paused:
            pygame.mixer.music.unpause()
            self.play_start_ticks = pygame.time.get_ticks() - self.current_time_ms
            self.paused = False
            self.playing = True
            return

        pygame.mixer.music.play()
        self.play_start_ticks = pygame.time.get_ticks() - self.current_time_ms
        self.playing = True
        self.paused = False

    def pause_playback(self):
        """Pause audio playback"""
        if self.audio_available and self.playing and not self.paused:
            pygame.mixer.music.pause()
            self.current_time_ms = pygame.time.get_ticks() - self.play_start_ticks
            self.playing = False
            self.paused = True

    def stop_playback(self):
        """Stop playback and reset"""
        if self.audio_available:
            pygame.mixer.music.stop()
        self.current_time_ms = 0
        self.playing = False
        self.paused = False

    def update_time(self):
        """Update current playback time for preview"""
        if self.playing and not self.paused:
            self.current_time_ms = pygame.time.get_ticks() - self.play_start_ticks
            if self.current_time_ms < 0:
                self.current_time_ms = 0

    def time_to_x(self, time_ms):
        """Convert time in milliseconds to X pixel position"""
        return (time_ms - self.scroll_offset) * self.pixels_per_ms

    def x_to_time(self, x_pixel):
        """Convert X pixel position to time in milliseconds"""
        return int(x_pixel / self.pixels_per_ms + self.scroll_offset)

    def handle_events(self):
        """Handle user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.save_chart()
                elif event.key == pygame.K_LEFT:
                    self.scroll_offset = max(0, self.scroll_offset - 500)
                elif event.key == pygame.K_RIGHT:
                    self.scroll_offset += 500
                elif event.key == pygame.K_UP:
                    self.pixels_per_ms = min(1.0, self.pixels_per_ms + 0.05)
                elif event.key == pygame.K_DOWN:
                    self.pixels_per_ms = max(0.05, self.pixels_per_ms - 0.05)
                elif event.key == pygame.K_SPACE:
                    if self.playing or self.paused:
                        self.pause_playback()
                    else:
                        self.start_playback()
                elif event.key == pygame.K_TAB:
                    if self.song_files:
                        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                            self.selected_song_index = (self.selected_song_index - 1) % len(self.song_files)
                        else:
                            self.selected_song_index = (self.selected_song_index + 1) % len(self.song_files)
                        self.load_song(self.selected_song_index)
                elif event.key == pygame.K_RETURN:
                    self.load_song(self.selected_song_index)
                elif event.key == pygame.K_p and self.character_folders:
                    self.selected_player_index = (self.selected_player_index + 1) % len(self.character_folders)
                    self.update_chart_characters()
                elif event.key == pygame.K_o and self.character_folders:
                    self.selected_enemy_index = (self.selected_enemy_index + 1) % len(self.character_folders)
                    self.update_chart_characters()
                elif event.key == pygame.K_c:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.chart['notes'] = []
                elif event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                    pass

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click - add note
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if mouse_y > self.timeline_height:
                        lane = int(mouse_x / self.lane_width)
                        if 0 <= lane < self.config['lanes']:
                            time_ms = self.x_to_time(mouse_x)
                            time_ms = round(time_ms / self.snap_grid) * self.snap_grid
                            note_exists = any(
                                n['time'] == time_ms and n['lane'] == lane
                                for n in self.chart['notes']
                            )
                            if not note_exists:
                                self.chart['notes'].append({
                                    "time": time_ms,
                                    "lane": lane
                                })
                                self.chart['notes'].sort(key=lambda x: x['time'])

                elif event.button == 3:  # Right click - delete note
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if mouse_y > self.timeline_height:
                        lane = int(mouse_x / self.lane_width)
                        time_ms = self.x_to_time(mouse_x)
                        for i, note in enumerate(self.chart['notes']):
                            note_x = self.time_to_x(note['time'])
                            if (note['lane'] == lane and abs(note_x - mouse_x) < 25):
                                self.chart['notes'].pop(i)
                                break

            elif event.type == pygame.MOUSEWHEEL:
                self.scroll_offset = max(0, self.scroll_offset - event.y * 300)

    def draw_song_panel(self):
        """Draw song selection and playback panel"""
        panel_height = 120
        panel_color = (25, 25, 35)
        pygame.draw.rect(self.screen, panel_color, (0, self.config['height'] - panel_height, self.config['width'], panel_height))

        font = pygame.font.Font(None, 28)

        song_text = f"Loaded song: {self.song_name}"
        status_text = "PLAYING" if self.playing and not self.paused else "PAUSED" if self.paused else "STOPPED"
        song_selection = (
            f"{self.selected_song_index + 1}/{len(self.song_files)}"
            if self.song_files else "0/0"
        )
        info_texts = [
            song_text,
            f"Status: {status_text} | Mode: {self.preview_mode}",
            f"Song selection: {song_selection}",
            "TAB: audio | ENTER: load | P: player | O: enemy | SPACE: play/pause",
        ]

        for i, text in enumerate(info_texts):
            surface = font.render(text, True, (220, 220, 220) if i < 3 else (180, 180, 180))
            self.screen.blit(surface, (10, self.config['height'] - panel_height + 10 + i * 28))

    def draw_preview(self):
        """Draw upscroll preview for current playback/time"""
        preview_top = self.timeline_height + 20
        preview_bottom = self.config['height'] - 140
        preview_height = preview_bottom - preview_top

        pygame.draw.rect(self.screen, (20, 20, 30), (0, preview_top, self.config['width'], preview_height))
        hit_y = preview_top + 40
        pygame.draw.line(self.screen, (255, 255, 255), (0, hit_y), (self.config['width'], hit_y), 2)
        font = pygame.font.Font(None, 24)
        label = font.render("UPSCROLL PREVIEW", True, (180, 180, 180))
        self.screen.blit(label, (10, preview_top + 10))

        current_time = self.current_time_ms if self.playing or self.paused else self.scroll_offset

        for note in self.chart['notes']:
            delta = note['time'] - current_time
            y = preview_bottom - delta * self.playback_speed
            x = note['lane'] * self.lane_width + self.lane_width * 0.1
            width = self.lane_width * 0.8
            height = 20

            if hit_y < y < preview_bottom:
                rect = pygame.Rect(x, y, width, height)
                color = self.lane_colors[note['lane']]
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)

    def draw_timeline(self):
        """Draw the timeline at the top"""
        pygame.draw.rect(self.screen, (40, 40, 40), (0, 0, self.config['width'], self.timeline_height))
        pygame.draw.line(self.screen, (100, 100, 100), (0, self.timeline_height),
                         (self.config['width'], self.timeline_height), 2)

        beat_duration = (60000 / self.bpm)
        if self.pixels_per_ms < 0.1:
            marker_interval = beat_duration * 4
        elif self.pixels_per_ms < 0.3:
            marker_interval = beat_duration
        else:
            marker_interval = beat_duration / 4

        time = int(self.scroll_offset / marker_interval) * marker_interval
        while time < self.scroll_offset + self.config['width'] / self.pixels_per_ms:
            x = self.time_to_x(time)
            if 0 <= x <= self.config['width']:
                pygame.draw.line(self.screen, (100, 100, 100), (x, self.timeline_height - 10),
                                 (x, self.timeline_height), 2)
                font = pygame.font.Font(None, 20)
                time_text = font.render(f"{int(time/1000)}s", True, (200, 200, 200))
                self.screen.blit(time_text, (x - 15, 5))
            time += marker_interval

    def draw_lanes(self):
        """Draw the 4 lanes for notes"""
        for lane in range(self.config['lanes'] + 1):
            x = lane * self.lane_width
            color = (60, 60, 60) if lane % 2 == 0 else (50, 50, 50)
            pygame.draw.rect(self.screen, color, (x, self.timeline_height, self.lane_width, self.lane_height))
            pygame.draw.line(self.screen, (100, 100, 100), (x, self.timeline_height),
                             (x, self.config['height']), 2)

        beat_duration = (60000 / self.bpm)
        time = int(self.scroll_offset / beat_duration) * beat_duration
        while time < self.scroll_offset + self.config['width'] / self.pixels_per_ms:
            x = self.time_to_x(time)
            if 0 <= x <= self.config['width']:
                color = (100, 100, 100) if int(time / beat_duration) % 4 == 0 else (80, 80, 80)
                pygame.draw.line(self.screen, color, (x, self.timeline_height),
                                 (x, self.config['height'] - 140), 1)
            time += beat_duration / 4

    def draw_notes(self):
        """Draw all notes on the timeline"""
        note_height = self.lane_height * 0.15
        note_width = self.lane_width * 0.8

        for note in self.chart['notes']:
            x = self.time_to_x(note['time'])
            lane = note['lane']
            if -note_width < x < self.config['width'] + note_width:
                y = self.timeline_height + self.lane_height * 0.45
                color = self.lane_colors[lane]
                rect = pygame.Rect(
                    x + (lane + 0.1) * self.lane_width,
                    y,
                    note_width,
                    note_height
                )
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)

    def draw_ui(self):
        """Draw UI information"""
        font = pygame.font.Font(None, 24)
        info_texts = [
            f"Scroll: {self.scroll_offset:.0f}ms | Zoom: {self.pixels_per_ms:.2f}px/ms | BPM: {self.bpm}",
            f"Notes: {len(self.chart['notes'])} | Song: {self.chart.get('name', 'New Song')}",
            f"Versus: {self.chart.get('player', 'Player')} vs {self.chart.get('enemy', 'EnemyTest')}",
            f"Left/Right: Scroll | Up/Down: Zoom | Click: Add | Right Click: Delete | CTRL+S: Save -> {self.export_chart_file.name}",
        ]
        for i, text in enumerate(info_texts):
            surface = font.render(text, True, (200, 200, 200))
            self.screen.blit(surface, (10, self.config['height'] - 110 + i * 25))

    def draw(self):
        """Draw the editor"""
        self.screen.fill((30, 30, 30))
        self.draw_lanes()
        self.draw_timeline()
        self.draw_notes()
        self.draw_preview()
        self.draw_song_panel()
        self.draw_ui()
        pygame.display.flip()

    def run(self):
        """Main editor loop"""
        while self.running:
            self.handle_events()
            self.update_time()
            self.draw()
            self.clock.tick(60)
        if self.audio_available:
            pygame.mixer.music.stop()


def main():
    chart_file = sys.argv[1] if len(sys.argv) > 1 else None
    editor = ChartEditor(chart_file)
    editor.run()


if __name__ == "__main__":
    main()
