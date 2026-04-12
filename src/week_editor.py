"""
Week Editor for creating and managing story mode weeks
"""
import sys
from pathlib import Path

import pygame

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.logging_utils import configure_logging, get_user_logger
from src.resources import get_resource_path
from src.week_manager import Week, WeekManager, ChartManager


configure_logging()
user_logger = get_user_logger("week_editor")

class WeekEditor:
    """Simple GUI for editing weeks/level packs"""
    def __init__(self, week_name=None):
        pygame.init()
        
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("FNF Week Editor")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.week_manager = WeekManager()
        self.chart_manager = ChartManager()
        
        self.font = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.font_title = pygame.font.Font(None, 48)
        
        # Current week being edited
        if week_name and week_name in self.week_manager.weeks:
            self.current_week = self.week_manager.weeks[week_name]
        else:
            self.current_week = Week(name="New Week")
        
        self.editing_name = False
        self.name_input = self.current_week.name
        
        # Available charts and backgrounds
        self.available_charts = self.chart_manager.get_chart_names()
        self.available_backgrounds = self.get_available_backgrounds()
        
        self.selected_song_index = 0
        self.selected_bg_index = 0
        
    def get_available_backgrounds(self):
        """Get list of available background images"""
        bg_path = get_resource_path("assets", "sprites", "MenuBackGrounds")
        backgrounds = []
        if bg_path.exists():
            for bg_file in bg_path.glob("*.png"):
                backgrounds.append(bg_file.name)
        return sorted(backgrounds)
    
    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                elif self.editing_name:
                    if event.key == pygame.K_RETURN:
                        self.current_week.name = self.name_input
                        self.editing_name = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.name_input = self.name_input[:-1]
                    else:
                        if len(self.name_input) < 30:
                            self.name_input += event.unicode
                
                # Song management
                elif event.key == pygame.K_UP:
                    if self.available_charts:
                        self.selected_song_index = max(0, self.selected_song_index - 1)
                elif event.key == pygame.K_DOWN:
                    if self.available_charts:
                        self.selected_song_index = min(
                            len(self.available_charts) - 1,
                            self.selected_song_index + 1
                        )
                elif event.key == pygame.K_a:
                    if self.available_charts:
                        song = self.available_charts[self.selected_song_index]
                        if song not in self.current_week.songs:
                            self.current_week.songs.append(song)
                
                elif event.key == pygame.K_r:
                    if self.current_week.songs:
                        self.current_week.songs.pop()
                
                # Background selection
                elif event.key == pygame.K_LEFT:
                    if self.available_backgrounds:
                        self.selected_bg_index = max(0, self.selected_bg_index - 1)
                        self.current_week.background = self.available_backgrounds[self.selected_bg_index]
                
                elif event.key == pygame.K_RIGHT:
                    if self.available_backgrounds:
                        self.selected_bg_index = min(
                            len(self.available_backgrounds) - 1,
                            self.selected_bg_index + 1
                        )
                        self.current_week.background = self.available_backgrounds[self.selected_bg_index]
                
                # Save
                elif event.key == pygame.K_s:
                    self.week_manager.save_week(self.current_week)
                    user_logger.info("Week sauvegardee: %s", self.current_week.name)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Click on name to edit
                name_rect = pygame.Rect(150, 70, 500, 40)
                if name_rect.collidepoint(event.pos):
                    self.editing_name = True
    
    def draw(self):
        """Draw the editor"""
        self.screen.fill((30, 30, 50))
        
        # Title
        title = self.font_title.render("WEEK EDITOR", True, (100, 200, 255))
        self.screen.blit(title, (50, 20))
        
        # Week name
        name_label = self.font.render("Week Name:", True, (150, 200, 255))
        self.screen.blit(name_label, (50, 75))
        
        name_color = (100, 200, 255) if self.editing_name else (50, 100, 150)
        pygame.draw.rect(self.screen, name_color, (150, 70, 500, 40), 2)
        name_text = self.font.render(self.name_input, True, (255, 255, 255))
        self.screen.blit(name_text, (160, 80))
        
        # Available songs
        y = 130
        songs_label = self.font.render("Available Songs (UP/DOWN to select, A to add, R to remove):", True, (150, 200, 255))
        self.screen.blit(songs_label, (50, y))
        
        y = 170
        for i, song in enumerate(self.available_charts[:5]):
            color = (100, 200, 255) if i == self.selected_song_index else (100, 100, 100)
            song_text = self.font_small.render(f"{'>' if i == self.selected_song_index else ' '} {song}",
                                               True, color)
            self.screen.blit(song_text, (70, y))
            y += 30
        
        # Selected songs
        y = 130
        selected_label = self.font.render("Selected Songs for Week:", True, (150, 200, 255))
        self.screen.blit(selected_label, (700, y))
        
        y = 170
        for song in self.current_week.songs:
            song_text = self.font_small.render(f"* {song}", True, (100, 200, 255))
            self.screen.blit(song_text, (720, y))
            y += 30
        
        # Background selection
        y = 400
        bg_label = self.font.render("Background (LEFT/RIGHT to select):", True, (150, 200, 255))
        self.screen.blit(bg_label, (50, y))
        
        y = 450
        for i, bg in enumerate(self.available_backgrounds):
            color = (100, 200, 255) if i == self.selected_bg_index else (100, 100, 100)
            bg_text = self.font_small.render(f"{'>' if i == self.selected_bg_index else ' '} {bg}",
                                             True, color)
            self.screen.blit(bg_text, (70, y))
            if i > 4:
                break
            y += 30
        
        # Instructions
        y = 650
        inst1 = self.font_small.render("S: Save  |  ESC: Exit", True, (150, 150, 150))
        self.screen.blit(inst1, (50, y))
        
        pygame.display.flip()
    
    def update(self):
        """Update editor"""
        pass
    
    def run(self):
        """Main editor loop"""
        while self.running:
            self.handle_events()
            self.draw()
            self.update()
            self.clock.tick(60)
        
        pygame.quit()


def main():
    editor = WeekEditor()
    editor.run()


if __name__ == "__main__":
    main()
