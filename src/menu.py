"""
Menu UI components and menu screens for FNF
"""
import math
import pygame
from src.keybinds import binding_label, bindings_conflict, build_keybind_from_event, clone_keybind, default_keybind, normalize_keybind
from src.logging_utils import get_debug_logger
from src.resources import get_resource_path


debug_logger = get_debug_logger("menu")

AVRIL_SEQUENCE = "AVRIL"

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
        self.binding = None
        self.listening = False
        self.font = pygame.font.Font(None, 28)

    def set_binding(self, binding):
        self.binding = clone_keybind(binding)
        
    def draw(self, surface):
        """Draw the keybind selector"""
        color = (150, 100, 200) if self.listening else (50, 100, 150)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)
        
        key_text = binding_label(self.binding)
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
    
    def handle_key(self, event):
        """Handle key press"""
        if self.listening:
            self.binding = build_keybind_from_event(event)
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
    def __init__(self, on_play, on_options, on_quit, config=None):
        self.on_play = on_play
        self.on_options = on_options
        self.on_quit = on_quit
        self.config = config or {}
        self.title_animation_amplitude = float(self.config.get("title_animation_amplitude_px", 10))
        self.title_animation_speed = float(self.config.get("title_animation_speed", 0.003))
        self.title_rotation_degrees = float(self.config.get("title_rotation_degrees", 2.0))
        self.title_scale_amplitude = float(self.config.get("title_scale_amplitude", 0.025))
        self.exit_evasion_active = False
        self.exit_evasion_index = 0
        self.exit_evasion_radius = float(self.config.get("exit_evasion_radius_px", 170))
        self.exit_evasion_max_speed = float(self.config.get("exit_evasion_max_speed_px", 520))
        self.exit_evasion_smoothness = float(self.config.get("exit_evasion_smoothness", 0.18))
        self.last_mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())
        self.last_mouse_ticks = pygame.time.get_ticks()
        self.mouse_velocity = pygame.math.Vector2()
        
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
        self.quit_button = self.buttons[-1]
        
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
                self.update_mouse_velocity(event.pos)
                for button in self.buttons:
                    button.update(mouse_pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.exit_evasion_active:
                    self.update_exit_evasion(force=True)
                    mouse_pos = pygame.mouse.get_pos()
                for button in self.buttons:
                    button.handle_click(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.on_quit()
                else:
                    self.observe_avril_key(event)

    def update_mouse_velocity(self, mouse_pos):
        """Track mouse speed for the evasive quit button."""
        now = pygame.time.get_ticks()
        elapsed = max(1, now - self.last_mouse_ticks)
        current_pos = pygame.math.Vector2(mouse_pos)
        self.mouse_velocity = (current_pos - self.last_mouse_pos) * (1000 / elapsed)
        self.last_mouse_pos = current_pos
        self.last_mouse_ticks = now

    def observe_avril_key(self, event):
        """Enable the main-menu easter egg after typing AVRIL."""
        key_name = pygame.key.name(event.key).upper()
        if len(key_name) != 1:
            self.exit_evasion_index = 0
            return

        expected = AVRIL_SEQUENCE[self.exit_evasion_index]
        if key_name == expected:
            self.exit_evasion_index += 1
            if self.exit_evasion_index == len(AVRIL_SEQUENCE):
                self.exit_evasion_index = 0
                self.exit_evasion_active = True
                debug_logger.info("Easter egg AVRIL active: bouton QUIT evasif.")
            return

        self.exit_evasion_index = 1 if key_name == AVRIL_SEQUENCE[0] else 0

    def update_exit_evasion(self, force=False):
        """Move the quit button away from the mouse while keeping it onscreen."""
        if not self.exit_evasion_active:
            return

        mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())
        button_center = pygame.math.Vector2(self.quit_button.rect.center)
        away = button_center - mouse_pos
        distance = away.length()
        if distance > self.exit_evasion_radius and not force:
            return

        if distance == 0:
            away = pygame.math.Vector2(1, 0)
        else:
            away = away.normalize()

        speed_factor = min(1.0, self.mouse_velocity.length() / 900)
        move_distance = 18 + self.exit_evasion_max_speed * speed_factor / 60
        target_center = button_center + away * move_distance
        new_center = button_center.lerp(target_center, self.exit_evasion_smoothness)

        half_width = self.quit_button.rect.width / 2
        half_height = self.quit_button.rect.height / 2
        new_center.x = max(half_width, min(1280 - half_width, new_center.x))
        new_center.y = max(half_height, min(720 - half_height, new_center.y))
        self.quit_button.rect.center = (round(new_center.x), round(new_center.y))
    
    def draw(self, surface):
        """Draw the menu"""
        surface.blit(self.background, (0, 0))

        # Draw menu logo
        if self.logo:
            ticks = pygame.time.get_ticks()
            sway_x = math.sin(ticks * self.title_animation_speed * 0.6) * (self.title_animation_amplitude * 0.5)
            bob_y = math.sin(ticks * self.title_animation_speed) * self.title_animation_amplitude
            rotation = math.sin(ticks * self.title_animation_speed * 0.75) * self.title_rotation_degrees
            scale = 1.0 + math.sin(ticks * self.title_animation_speed * 1.1) * self.title_scale_amplitude
            logo_image = pygame.transform.rotozoom(self.logo, rotation, scale)
            logo_rect = logo_image.get_rect(center=(640 + sway_x, 90 + bob_y))
            surface.blit(logo_image, logo_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(surface)
    
    def update(self):
        """Update menu state"""
        self.update_exit_evasion()


class IntroScreen:
    """Startup intro screen with a stylized furry lama."""
    def __init__(self, on_complete, config=None):
        self.on_complete = on_complete
        self.config = config or {}
        self.duration_ms = int(self.config.get("intro_duration_ms", 2400))
        self.start_tick = pygame.time.get_ticks()
        self.completed = False
        self.font_title = pygame.font.Font(None, 74)
        self.font_subtitle = pygame.font.Font(None, 34)
        self.font_hint = pygame.font.Font(None, 28)

    def complete(self):
        """Exit the intro screen once."""
        if self.completed:
            return
        self.completed = True
        self.on_complete()

    def handle_events(self, events):
        """Allow the player to skip the intro."""
        for event in events:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.complete()

    def update(self):
        """Advance automatically after the configured intro duration."""
        if pygame.time.get_ticks() - self.start_tick >= self.duration_ms:
            self.complete()

    def draw(self, surface):
        """Draw the animated intro artwork."""
        width, height = surface.get_size()
        ticks = pygame.time.get_ticks()
        drift = math.sin(ticks * 0.003) * 8
        wool = math.sin(ticks * 0.004) * 6

        surface.fill((18, 14, 28))

        glow = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.circle(glow, (245, 160, 90, 70), (width // 2, 180), 170)
        pygame.draw.circle(glow, (130, 90, 200, 55), (width // 2 + 160, 250), 220)
        pygame.draw.circle(glow, (80, 180, 230, 45), (width // 2 - 170, 260), 200)
        surface.blit(glow, (0, 0))

        body_color = (224, 208, 180)
        wool_color = (244, 236, 220)
        accent_color = (120, 72, 44)
        center_x = width // 2
        center_y = int(height * 0.5 + drift)

        pygame.draw.ellipse(surface, body_color, (center_x - 180, center_y - 10, 360, 180))
        pygame.draw.rect(surface, accent_color, (center_x - 120, center_y + 130, 28, 105), border_radius=10)
        pygame.draw.rect(surface, accent_color, (center_x - 40, center_y + 140, 28, 105), border_radius=10)
        pygame.draw.rect(surface, accent_color, (center_x + 35, center_y + 138, 28, 105), border_radius=10)
        pygame.draw.rect(surface, accent_color, (center_x + 110, center_y + 126, 28, 105), border_radius=10)
        pygame.draw.rect(surface, body_color, (center_x + 78, center_y - 82, 66, 145), border_radius=22)
        pygame.draw.ellipse(surface, accent_color, (center_x + 58, center_y - 175, 115, 125))
        pygame.draw.ellipse(surface, wool_color, (center_x + 36, center_y - 196, 150, 110))
        pygame.draw.polygon(surface, accent_color, [(center_x + 92, center_y - 178), (center_x + 116, center_y - 248), (center_x + 138, center_y - 182)])
        pygame.draw.polygon(surface, accent_color, [(center_x + 146, center_y - 176), (center_x + 170, center_y - 248), (center_x + 191, center_y - 184)])
        pygame.draw.circle(surface, (20, 20, 24), (center_x + 96, center_y - 126), 7)
        pygame.draw.circle(surface, (20, 20, 24), (center_x + 142, center_y - 124), 7)
        pygame.draw.line(surface, (70, 30, 30), (center_x + 105, center_y - 90), (center_x + 142, center_y - 90), 3)

        for index, offset in enumerate(range(-110, 130, 40)):
            radius = 33 + (index % 2) * 4
            pygame.draw.circle(
                surface,
                wool_color,
                (center_x + offset, int(center_y + (math.sin(ticks * 0.004 + index) * wool))),
                radius,
            )

        title = self.font_title.render("GRAND LAMA COSMIQUE VELU", True, (255, 240, 214))
        title_rect = title.get_rect(center=(width // 2, 92))
        surface.blit(title, title_rect)

        subtitle = self.font_subtitle.render("Un souffle laineux avant le menu principal", True, (214, 214, 230))
        subtitle_rect = subtitle.get_rect(center=(width // 2, 142))
        surface.blit(subtitle, subtitle_rect)

        hint = self.font_hint.render("Press any key or click to skip", True, (210, 210, 210))
        hint_rect = hint.get_rect(center=(width // 2, height - 52))
        surface.blit(hint, hint_rect)


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
            selector.set_binding(normalize_keybind(action, settings.get(f"keybinds.{action}")))
        
        # Scroll mode buttons
        self.scroll_modes = ["downscroll", "upscroll", "sidescroll"]
        self.current_scroll_mode = settings.get("scroll_mode", "downscroll")
        
        self.scroll_mode_buttons = {}
        for i, mode in enumerate(self.scroll_modes):
            self.scroll_mode_buttons[mode] = ScrollModeButton(150 + i * 120, 415, mode)
            self.scroll_mode_buttons[mode].selected = (mode == self.current_scroll_mode)

        self.display_modes = ["windowed", "fullscreen"]
        self.current_display_mode = settings.get("display.mode", "windowed")

        self.display_mode_buttons = {}
        for i, mode in enumerate(self.display_modes):
            self.display_mode_buttons[mode] = ScrollModeButton(150 + i * 170, 505, mode)
            self.display_mode_buttons[mode].selected = (mode == self.current_display_mode)
        
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
                for action, selector in self.keybind_selectors.items():
                    if selector.handle_click(mouse_pos):
                        for other_action, other_selector in self.keybind_selectors.items():
                            if other_action != action:
                                other_selector.listening = False
                
                # Check scroll mode buttons
                for mode, button in self.scroll_mode_buttons.items():
                    if button.handle_click(mouse_pos):
                        self.current_scroll_mode = mode
                        for b in self.scroll_mode_buttons.values():
                            b.selected = False
                        button.selected = True
                        self.save_settings()  # Auto-save when scroll mode changes

                for mode, button in self.display_mode_buttons.items():
                    if button.handle_click(mouse_pos):
                        self.current_display_mode = mode
                        for b in self.display_mode_buttons.values():
                            b.selected = False
                        button.selected = True
                        self.save_settings()
                
                # Check buttons
                self.back_button.handle_click(mouse_pos)
                self.reset_button.handle_click(mouse_pos)
                
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.dragging_slider:
                    self.dragging_slider.handle_release()
                    self.dragging_slider = None
                    self.save_settings()  # Auto-save when slider is released
                
            elif event.type == pygame.KEYDOWN:
                listening_action = self.get_listening_action()
                if listening_action:
                    if event.key == pygame.K_ESCAPE:
                        self.keybind_selectors[listening_action].listening = False
                    else:
                        selector = self.keybind_selectors[listening_action]
                        previous_binding = clone_keybind(selector.binding)
                        if selector.handle_key(event):
                            self.resolve_duplicate_keybinds(listening_action, previous_binding)
                            self.save_settings()
                elif event.key == pygame.K_ESCAPE:
                    self.save_settings()
                    self.on_back()
                
            elif event.type == pygame.KEYUP:
                pass  # Scroll mode button clicks
                pass
    
    def handle_scroll_mode_click(self, mode):
        """Handle scroll mode button click"""
        self.current_scroll_mode = mode

    def get_listening_action(self):
        """Return the currently armed keybind selector."""
        for action, selector in self.keybind_selectors.items():
            if selector.listening:
                return action
        return None

    def resolve_duplicate_keybinds(self, changed_action, previous_binding):
        """Keep one unique keybind per lane by swapping duplicate captures."""
        changed_selector = self.keybind_selectors[changed_action]
        for action, selector in self.keybind_selectors.items():
            if action == changed_action:
                continue
            if bindings_conflict(changed_selector.binding, selector.binding):
                replacement = previous_binding or default_keybind(action)
                selector.set_binding(replacement)
                selector.listening = False
                break
    
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
                self.settings.set("volume.master", slider.value, autosave=False)
            elif i == 1:
                self.settings.set("volume.music", slider.value, autosave=False)
            elif i == 2:
                self.settings.set("volume.effects", slider.value, autosave=False)
        
        # Save keybinds
        for action, selector in self.keybind_selectors.items():
            self.settings.set(
                f"keybinds.{action}",
                clone_keybind(selector.binding) or default_keybind(action),
                autosave=False,
            )
        
        # Save scroll mode
        self.settings.set("scroll_mode", self.current_scroll_mode, autosave=False)

        # Save display mode
        self.settings.set("display.mode", self.current_display_mode, autosave=False)
        self.settings.save_settings()
    
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

        keybind_hint = self.font_small.render(
            "AZERTY/QWERTY: binds follow the physical key position.",
            True,
            (200, 210, 230),
        )
        surface.blit(keybind_hint, (800, 345))

        capture_hint = self.font_small.render(
            "Click a lane, press a key, ESC cancels capture.",
            True,
            (180, 190, 210),
        )
        surface.blit(capture_hint, (800, 368))
        
        # Draw scroll mode section
        scroll_title = self.font_small.render("SCROLL MODE", True, (150, 200, 255))
        surface.blit(scroll_title, (150, 380))
        
        # Draw scroll mode buttons
        for button in self.scroll_mode_buttons.values():
            button.draw(surface)

        display_title = self.font_small.render("DISPLAY MODE", True, (150, 200, 255))
        surface.blit(display_title, (150, 470))

        for button in self.display_mode_buttons.values():
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


class PauseMenu:
    """In-game pause menu."""
    def __init__(self, on_resume, on_options, on_restart, on_quit):
        self.on_resume = on_resume
        self.on_options = on_options
        self.on_restart = on_restart
        self.on_quit = on_quit

        width, height = 300, 55
        center_x = 640 - width // 2
        self.buttons = [
            Button(center_x, 225, width, height, "RESUME", self.on_resume),
            Button(center_x, 295, width, height, "OPTIONS", self.on_options),
            Button(center_x, 365, width, height, "RESTART", self.on_restart),
            Button(center_x, 435, width, height, "QUIT", self.on_quit),
        ]
        self.font_title = pygame.font.Font(None, 64)
        self.font_hint = pygame.font.Font(None, 28)

    def handle_events(self, events):
        """Handle pause menu input."""
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
                    self.on_resume()

    def draw(self, surface):
        """Draw the pause overlay."""
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surface.blit(overlay, (0, 0))

        title = self.font_title.render("PAUSED", True, (255, 255, 255))
        title_rect = title.get_rect(center=(640, 150))
        surface.blit(title, title_rect)

        for button in self.buttons:
            button.draw(surface)

        hint = self.font_hint.render("ESC: Resume", True, (200, 200, 200))
        hint_rect = hint.get_rect(center=(640, 520))
        surface.blit(hint, hint_rect)

    def update(self):
        """Update pause menu state."""
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
            btn = Button(100, y, 800, 60, f"* {song}",
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
            btn = Button(100, y, 800, 60, f"Week: {week}",
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
