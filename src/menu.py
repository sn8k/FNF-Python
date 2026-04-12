"""
Menu UI components and menu screens for FNF
"""
import pygame
from pathlib import Path
from src.settings import Settings
from src.logging_utils import get_debug_logger
from src.resources import get_resource_path


debug_logger = get_debug_logger("menu")

class Button:
    """UI Button for menus"""
    def __init__(self, x, y, width, height, text, callback=None, texture_path=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.hovered = False
        self.font = pygame.font.Font(None, 36)
        self.image = None
        self.image_hovered = None
        
        # Load texture if provided
        if texture_path:
            self.load_texture(texture_path, width, height)
    
    def load_texture(self, texture_path, width, height):
        """Load and scale button texture"""
        try:
            img = pygame.image.load(texture_path).convert_alpha()
            self.image = pygame.transform.scale(img, (width, height))
            # Create brightened version for hover effect
            self.image_hovered = self.image.copy()
            # Create a surface with brightness overlay
            highlight = pygame.Surface((width, height))
            highlight.fill((255, 255, 255))
            highlight.set_alpha(60)
            self.image_hovered.blit(highlight, (0, 0))
        except pygame.error as e:
            debug_logger.warning(
                "Impossible de charger la texture de bouton %s: %s", texture_path, e
            )
        
    def draw(self, surface):
        """Draw the button"""
        if self.image:
            # Draw textured button (texture already has text)
            button_image = self.image_hovered if self.hovered else self.image
            surface.blit(button_image, self.rect.topleft)
        else:
            # Fallback to colored rectangle with text
            color = (100, 200, 255) if self.hovered else (50, 100, 150)
            pygame.draw.rect(surface, color, self.rect)
            pygame.draw.rect(surface, (200, 200, 200), self.rect, 3)
            
            # Draw text overlay only for fallback
            text_surface = self.font.render(self.text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)
    
    def update(self, mouse_pos):
        """Update button hover state"""
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def handle_click(self, mouse_pos):
        """Handle mouse click"""
        if self.rect.collidepoint(mouse_pos) and self.callback:
            self.callback()
            return True
        return False


class Slider:
    """UI Slider for value adjustment"""
    def __init__(self, x, y, width, label, min_val=0, max_val=100, initial=50):
        self.x = x
        self.y = y
        self.width = width
        self.height = 30
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial
        self.dragging = False
        self.font = pygame.font.Font(None, 24)
        
    def draw(self, surface):
        """Draw the slider"""
        # Draw label
        label_text = self.font.render(f"{self.label}: {self.value}", True, (255, 255, 255))
        surface.blit(label_text, (self.x, self.y))
        
        # Draw track
        track_rect = pygame.Rect(self.x, self.y + 25, self.width, 10)
        pygame.draw.rect(surface, (50, 50, 50), track_rect)
        pygame.draw.rect(surface, (100, 100, 100), track_rect, 2)
        
        # Draw knob
        knob_x = self.x + (self.value - self.min_val) / (self.max_val - self.min_val) * self.width
        pygame.draw.circle(surface, (100, 200, 255), (int(knob_x), self.y + 30), 10)
    
    def update(self, mouse_pos):
        """Update slider with mouse position"""
        if self.dragging:
            relative_x = max(0, min(mouse_pos[0] - self.x, self.width))
            self.value = int(self.min_val + (relative_x / self.width) * (self.max_val - self.min_val))
    
    def handle_click(self, mouse_pos):
        """Handle mouse click"""
        knob_x = self.x + (self.value - self.min_val) / (self.max_val - self.min_val) * self.width
        knob_rect = pygame.Rect(knob_x - 15, self.y + 15, 30, 30)
        if knob_rect.collidepoint(mouse_pos):
            self.dragging = True
            return True
        return False
    
    def handle_release(self):
        """Handle mouse release"""
        self.dragging = False


class KeybindSelector:
    """UI Component for selecting keybinds"""
    def __init__(self, x, y, action_name):
        self.rect = pygame.Rect(x, y, 150, 40)
        self.action_name = action_name
        self.key = None
        self.listening = False
        self.font = pygame.font.Font(None, 28)
        
    def draw(self, surface):
        """Draw the keybind selector"""
        color = (150, 100, 200) if self.listening else (50, 100, 150)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)
        
        key_text = pygame.key.name(self.key) if self.key else "..."
        text = f"{self.action_name}: {key_text}"
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def handle_click(self, mouse_pos):
        """Handle mouse click"""
        if self.rect.collidepoint(mouse_pos):
            self.listening = not self.listening
            return True
        return False
    
    def handle_key(self, key):
        """Handle key press"""
        if self.listening:
            self.key = key
            self.listening = False
            return True
        return False


class ScrollModeButton:
    """UI Button for scroll mode selection"""
    def __init__(self, x, y, mode_name):
        self.x = x
        self.y = y
        self.mode_name = mode_name
        self.selected = False
        self.font = pygame.font.Font(None, 24)
    
    def draw(self, surface):
        """Draw the scroll mode button"""
        color = (100, 200, 255) if self.selected else (50, 100, 150)
        text_surface = self.font.render(f"[{self.mode_name.upper()}]", True, color)
        surface.blit(text_surface, (self.x, self.y))
        
        if self.selected:
            pygame.draw.rect(surface, (100, 200, 255),
                           (self.x - 5, self.y - 5,
                            text_surface.get_width() + 10, text_surface.get_height() + 10), 2)
    
    def get_rect(self):
        """Get the button rectangle for click detection"""
        text_surface = self.font.render(f"[{self.mode_name.upper()}]", True, (255, 255, 255))
        return pygame.Rect(self.x - 5, self.y - 5, text_surface.get_width() + 10, text_surface.get_height() + 10)
    
    def handle_click(self, mouse_pos):
        """Handle mouse click"""
        return self.get_rect().collidepoint(mouse_pos)


class MenuScreen:
    """Main menu screen"""
    def __init__(self, on_play, on_options, on_quit):
        self.on_play = on_play
        self.on_options = on_options
        self.on_quit = on_quit
        
        # Load background
        self.background = self.load_background(get_resource_path("assets", "sprites", "MenuBackGrounds", "Sticky.png"))
        
        # Load logo texture for title
        self.logo = self.load_logo(get_resource_path("assets", "sprites", "Misc", "MenuButtons", "Text.png"))
        
        # Create buttons with textures
        width, height = 400, 80
        center_x = 640 - width // 2
        self.buttons = [
            Button(center_x, 150, width, height, "PLAY", self.on_play, get_resource_path("assets", "sprites", "Misc", "MenuButtons", "Play.png")),
            Button(center_x, 290, width, height, "OPTIONS", self.on_options, get_resource_path("assets", "sprites", "Misc", "MenuButtons", "Options.png")),
            Button(center_x, 430, width, height, "QUIT", self.on_quit, get_resource_path("assets", "sprites", "Misc", "MenuButtons", "Quit.png")),
        ]
        
        self.font_title = pygame.font.Font(None, 72)
        
    def load_background(self, path):
        """Load menu background"""
        try:
            bg = pygame.image.load(path)
            bg = pygame.transform.scale(bg, (1280, 720))
            return bg
        except pygame.error:
            # Fallback gradient background
            default = pygame.Surface((1280, 720))
            default.fill((20, 20, 40))
            return default

    def load_logo(self, path):
        """Load menu logo texture"""
        try:
            logo = pygame.image.load(path).convert_alpha()
            logo_width = min(760, logo.get_width())
            scale = logo_width / logo.get_width()
            logo_height = int(logo.get_height() * scale)
            return pygame.transform.scale(logo, (logo_width, logo_height))
        except pygame.error:
            return None
    
    def handle_events(self, events):
        """Handle input events"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                for button in self.buttons:
                    button.update(mouse_pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    button.handle_click(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.on_quit()
    
    def draw(self, surface):
        """Draw the menu"""
        surface.blit(self.background, (0, 0))

        # Draw menu logo
        if self.logo:
            logo_rect = self.logo.get_rect(center=(640, 90))
            surface.blit(self.logo, logo_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(surface)
    
    def update(self):
        """Update menu state"""
        pass


class OptionsScreen:
    """Options/Settings menu screen"""
    def __init__(self, on_back, settings):
        self.on_back = on_back
        self.settings = settings
        
        # Load background
        self.background = self.load_background(get_resource_path("assets", "sprites", "MenuBackGrounds", "Options.png"))
        
        # Create UI components
        self.sliders = [
            Slider(150, 150, 300, "Master Volume", 0, 100, settings.get("volume.master", 70)),
            Slider(150, 220, 300, "Music Volume", 0, 100, settings.get("volume.music", 70)),
            Slider(150, 290, 300, "Effects Volume", 0, 100, settings.get("volume.effects", 70)),
        ]
        
        # Keybind selectors
        self.keybind_selectors = {
            "left": KeybindSelector(800, 150, "Left"),
            "down": KeybindSelector(800, 200, "Down"),
            "up": KeybindSelector(800, 250, "Up"),
            "right": KeybindSelector(800, 300, "Right"),
        }
        
        # Load current keybinds
        for action, selector in self.keybind_selectors.items():
            key_str = settings.get(f"keybinds.{action}", action)
            try:
                selector.key = pygame.key.key_code(key_str)
            except ValueError:
                selector.key = pygame.K_a
        
        # Scroll mode buttons
        self.scroll_modes = ["downscroll", "upscroll", "sidescroll"]
        self.current_scroll_mode = settings.get("scroll_mode", "downscroll")
        
        self.scroll_mode_buttons = {}
        for i, mode in enumerate(self.scroll_modes):
            self.scroll_mode_buttons[mode] = ScrollModeButton(150 + i * 120, 415, mode)
            self.scroll_mode_buttons[mode].selected = (mode == self.current_scroll_mode)
        
        # Back button
        self.back_button = Button(50, 650, 200, 50, "BACK", self.on_back)
        self.reset_button = Button(300, 650, 200, 50, "RESET", self.reset_settings)
        
        self.font_title = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 24)
        self.dragging_slider = None
        
    def load_background(self, path):
        """Load menu background"""
        try:
            bg = pygame.image.load(path)
            bg = pygame.transform.scale(bg, (1280, 720))
            return bg
        except pygame.error:
            # Fallback gradient background
            default = pygame.Surface((1280, 720))
            default.fill((20, 30, 50))
            return default
    
    def handle_events(self, events):
        """Handle input events"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                for slider in self.sliders:
                    slider.update(mouse_pos)
                self.back_button.update(mouse_pos)
                self.reset_button.update(mouse_pos)
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check sliders
                for slider in self.sliders:
                    if slider.handle_click(mouse_pos):
                        self.dragging_slider = slider
                        break
                
                # Check keybind selectors
                for selector in self.keybind_selectors.values():
                    selector.handle_click(mouse_pos)
                
                # Check scroll mode buttons
                for mode, button in self.scroll_mode_buttons.items():
                    if button.handle_click(mouse_pos):
                        self.current_scroll_mode = mode
                        for b in self.scroll_mode_buttons.values():
                            b.selected = False
                        button.selected = True
                        self.save_settings()  # Auto-save when scroll mode changes
                
                # Check buttons
                self.back_button.handle_click(mouse_pos)
                self.reset_button.handle_click(mouse_pos)
                
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.dragging_slider:
                    self.dragging_slider.handle_release()
                    self.dragging_slider = None
                    self.save_settings()  # Auto-save when slider is released
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.save_settings()
                    self.on_back()
                else:
                    # Pass key to keybind selectors
                    for selector in self.keybind_selectors.values():
                        if selector.listening:
                            old_key = selector.key
                            selector.handle_key(event.key)
                            if old_key != selector.key:
                                self.save_settings()  # Auto-save when keybind changes
                            break
                
            elif event.type == pygame.KEYUP:
                pass  # Scroll mode button clicks
                pass
    
    def handle_scroll_mode_click(self, mode):
        """Handle scroll mode button click"""
        self.current_scroll_mode = mode
    
    def reset_settings(self):
        """Reset settings to defaults"""
        self.settings.reset_to_defaults()
        # Reload UI
        self.__init__(self.on_back, self.settings)
    
    def save_settings(self):
        """Save current settings"""
        # Save volume
        for i, slider in enumerate(self.sliders):
            if i == 0:
                self.settings.set("volume.master", slider.value)
            elif i == 1:
                self.settings.set("volume.music", slider.value)
            elif i == 2:
                self.settings.set("volume.effects", slider.value)
        
        # Save keybinds
        for action, selector in self.keybind_selectors.items():
            if selector.key:
                key_name = pygame.key.name(selector.key)
                self.settings.set(f"keybinds.{action}", key_name)
        
        # Save scroll mode
        self.settings.set("scroll_mode", self.current_scroll_mode)
    
    def draw(self, surface):
        """Draw the options menu"""
        surface.blit(self.background, (0, 0))
        
        # Draw title
        title = self.font_title.render("OPTIONS", True, (100, 200, 255))
        surface.blit(title, (50, 50))
        
        # Draw volume section title
        vol_title = self.font_small.render("VOLUME", True, (150, 200, 255))
        surface.blit(vol_title, (150, 120))
        
        # Draw sliders
        for slider in self.sliders:
            slider.draw(surface)
        
        # Draw keybinds section title
        kb_title = self.font_small.render("KEYBINDS", True, (150, 200, 255))
        surface.blit(kb_title, (800, 120))
        
        # Draw keybind selectors
        for selector in self.keybind_selectors.values():
            selector.draw(surface)
        
        # Draw scroll mode section
        scroll_title = self.font_small.render("SCROLL MODE", True, (150, 200, 255))
        surface.blit(scroll_title, (150, 380))
        
        # Draw scroll mode buttons
        for button in self.scroll_mode_buttons.values():
            button.draw(surface)
        
        # Draw buttons
        self.back_button.draw(surface)
        self.reset_button.draw(surface)
    
    def update(self):
        """Update options"""
        pass


class PlayMenu:
    """Menu to select Free Play or Story Mode"""
    def __init__(self, on_free_play, on_story_mode, on_back):
        self.on_free_play = on_free_play
        self.on_story_mode = on_story_mode
        self.on_back = on_back
        
        # Load background
        self.background = self.load_background(get_resource_path("assets", "sprites", "MenuBackGrounds", "Drako.png"))
        
        # Create buttons
        width, height = 300, 60
        center_x = 640 - width // 2
        self.buttons = [
            Button(center_x, 200, width, height, "FREE PLAY", self.on_free_play),
            Button(center_x, 290, width, height, "STORY MODE", self.on_story_mode),
            Button(center_x, 380, width, height, "BACK", self.on_back),
        ]
        
        self.font_title = pygame.font.Font(None, 72)
    
    def load_background(self, path):
        """Load background"""
        try:
            bg = pygame.image.load(path)
            bg = pygame.transform.scale(bg, (1280, 720))
            return bg
        except pygame.error:
            default = pygame.Surface((1280, 720))
            default.fill((20, 20, 40))
            return default
    
    def handle_events(self, events):
        """Handle input events"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                for button in self.buttons:
                    button.update(mouse_pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    button.handle_click(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.on_back()
    
    def draw(self, surface):
        """Draw the menu"""
        surface.blit(self.background, (0, 0))
        
        # Draw title
        title_text = self.font_title.render("PLAY", True, (100, 200, 255))
        title_rect = title_text.get_rect(center=(640, 100))
        surface.blit(title_text, title_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(surface)
    
    def update(self):
        """Update menu state"""
        pass


class SongListMenu:
    """Menu to select a song for Free Play"""
    def __init__(self, songs, on_song_select, on_back):
        self.songs = songs
        self.on_song_select = on_song_select
        self.on_back = on_back
        
        self.background = self.load_background(get_resource_path("assets", "sprites", "MenuBackGrounds", "Drako.png"))
        
        # Create song buttons
        self.song_buttons = []
        for i, song in enumerate(songs):
            y = 100 + i * 80
            btn = Button(100, y, 800, 60, f"♪ {song}", 
                        lambda s=song: self.on_song_select(s))
            self.song_buttons.append(btn)
        
        # Back button
        self.back_button = Button(50, 650, 200, 50, "BACK", self.on_back)
        
        self.font_title = pygame.font.Font(None, 48)
    
    def load_background(self, path):
        """Load background"""
        try:
            bg = pygame.image.load(path)
            bg = pygame.transform.scale(bg, (1280, 720))
            return bg
        except pygame.error:
            default = pygame.Surface((1280, 720))
            default.fill((20, 20, 40))
            return default
    
    def handle_events(self, events):
        """Handle input events"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                for button in self.song_buttons:
                    button.update(mouse_pos)
                self.back_button.update(mouse_pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.song_buttons:
                    button.handle_click(mouse_pos)
                self.back_button.handle_click(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.on_back()
    
    def draw(self, surface):
        """Draw the menu"""
        surface.blit(self.background, (0, 0))
        
        # Draw title
        title = self.font_title.render("SELECT SONG", True, (100, 200, 255))
        surface.blit(title, (50, 30))
        
        # Draw song buttons
        for button in self.song_buttons:
            button.draw(surface)
        
        self.back_button.draw(surface)
    
    def update(self):
        """Update menu"""
        pass


class WeekListMenu:
    """Menu to select a week for Story Mode"""
    def __init__(self, weeks, on_week_select, on_back):
        self.weeks = weeks
        self.on_week_select = on_week_select
        self.on_back = on_back
        
        self.background = self.load_background(get_resource_path("assets", "sprites", "MenuBackGrounds", "Drako.png"))
        
        # Create week buttons
        self.week_buttons = []
        for i, week in enumerate(weeks):
            y = 100 + i * 80
            btn = Button(100, y, 800, 60, f"📅 {week}", 
                        lambda w=week: self.on_week_select(w))
            self.week_buttons.append(btn)
        
        # Back button
        self.back_button = Button(50, 650, 200, 50, "BACK", self.on_back)
        
        self.font_title = pygame.font.Font(None, 48)
    
    def load_background(self, path):
        """Load background"""
        try:
            bg = pygame.image.load(path)
            bg = pygame.transform.scale(bg, (1280, 720))
            return bg
        except pygame.error:
            default = pygame.Surface((1280, 720))
            default.fill((20, 20, 40))
            return default
    
    def handle_events(self, events):
        """Handle input events"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                for button in self.week_buttons:
                    button.update(mouse_pos)
                self.back_button.update(mouse_pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.week_buttons:
                    button.handle_click(mouse_pos)
                self.back_button.handle_click(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.on_back()
    
    def draw(self, surface):
        """Draw the menu"""
        surface.blit(self.background, (0, 0))
        
        # Draw title
        title = self.font_title.render("SELECT WEEK", True, (100, 200, 255))
        surface.blit(title, (50, 30))
        
        # Draw week buttons
        for button in self.week_buttons:
            button.draw(surface)
        
        self.back_button.draw(surface)
    
    def update(self):
        """Update menu"""
        pass
