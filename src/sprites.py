"""
Sprite classes for FNF game - Notes, Players, UI elements
"""
import pygame
from enum import Enum
from src.logging_utils import get_debug_logger
from src.resources import get_resource_path


debug_logger = get_debug_logger("sprites")

class NoteType(Enum):
    LEFT = 0
    DOWN = 1
    UP = 2
    RIGHT = 3

class Note(pygame.sprite.Sprite):
    """Falling note sprite"""
    def __init__(self, x, y, note_type, spawn_time, config):
        super().__init__()
        self.note_type = note_type
        self.spawn_time = spawn_time
        self.config = config
        
        # Create simple colored rectangle (placeholder for sprite)
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        color = colors[note_type.value]
        self.image = pygame.Surface((config['note_size'], config['note_size']))
        self.image.fill(color)
        pygame.draw.rect(self.image, (200, 200, 200), self.image.get_rect(), 3)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.hit = False
        self.missed = False
        self.miss_counted = False
        
    def update(self, current_time):
        """Update note position based on time"""
        spawn_distance = self.config['spawn_distance']
        hit_window = self.config['hit_window']
        approach_time_ms = max(1, int(self.config.get('note_approach_time_ms', 1500)))
        hit_zone_y = self.config.get('hit_zone_y', self.rect.centery + spawn_distance)
        
        # spawn_time is the target hit time stored in the chart.
        time_until_hit = self.spawn_time - current_time
        progress = 1 - (time_until_hit / approach_time_ms)
        
        # Place the note above the hit zone, then land on it at the chart time.
        self.rect.centery = hit_zone_y - spawn_distance + (progress * spawn_distance)
        
        # Mark as missed if it passed the hit zone
        if current_time - self.spawn_time > hit_window and not self.hit:
            self.missed = True
    
    def get_offset(self, current_time):
        """Get how far off the player is from hitting the note (in ms)"""
        return abs(current_time - self.spawn_time)

class HitZone(pygame.sprite.Sprite):
    """Visual indicator of where to hit notes"""
    def __init__(self, x, y, size):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.set_colorkey((0, 0, 0))
        pygame.draw.rect(self.image, (100, 100, 100), self.image.get_rect(), 2)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Character(pygame.sprite.Sprite):
    """Player or opponent character"""
    def __init__(self, x, y, character_type="player", size=350):
        super().__init__()
        self.character_type = character_type  # "player" or "enemy"
        self.target_height = size  # Target height in pixels, maintains aspect ratio
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.current_animation = "idle"
        self.idle = True
        
        # Load sprite images
        self.sprites = {}
        self.load_sprites()
        
        # Set initial image
        self.image = self.sprites["idle"]
        if character_type == "enemy":
            self.image = pygame.transform.flip(self.image, True, False)  # Flip horizontally
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    
    def scale_sprite_to_height(self, image, target_height):
        """Scale sprite to target height while maintaining aspect ratio"""
        original_width = image.get_width()
        original_height = image.get_height()
        
        # Calculate scale factor based on target height
        scale_factor = target_height / original_height
        
        # Calculate new width maintaining aspect ratio
        new_width = int(original_width * scale_factor)
        new_height = target_height
        
        return pygame.transform.scale(image, (new_width, new_height))
        
    def load_sprites(self):
        """Load all sprite images for this character"""
        base_path = get_resource_path("assets", "sprites", "Characters")
        
        if self.character_type == "player":
            char_path = base_path / "Player"
        else:  # enemy
            char_path = base_path / "EnemyTest"
        
        # Load all animation sprites
        animations = ["Idle", "Up", "Down", "Left", "Right"]
        
        for anim in animations:
            sprite_path = char_path / f"{anim}.png"
            try:
                image = pygame.image.load(str(sprite_path)).convert_alpha()
                # Scale to target height while maintaining aspect ratio
                image = self.scale_sprite_to_height(image, self.target_height)
                self.sprites[anim.lower()] = image
            except pygame.error:
                # Fallback to placeholder if sprite not found
                debug_logger.warning(
                    "Sprite introuvable ou invalide %s, utilisation d'un placeholder.",
                    sprite_path,
                )
                surface = pygame.Surface((self.target_height, self.target_height))
                surface.fill((100, 150, 200))
                pygame.draw.circle(surface, (255, 255, 200), (self.target_height // 2, self.target_height // 3), self.target_height // 4)
                self.sprites[anim.lower()] = surface
        
    def play_animation(self, animation_name):
        """Play a character animation"""
        if animation_name.startswith("hit_"):
            # Extract direction from "hit_0", "hit_1", etc.
            lane = int(animation_name.split("_")[1])
            directions = ["left", "down", "up", "right"]
            self.current_animation = directions[lane]
        else:
            self.current_animation = animation_name
            
        self.idle = (animation_name == "idle")
        
    def update(self, current_time=None):
        """Update character animation"""
        # For now, just use the current animation sprite
        # In a full implementation, this would cycle through animation frames
        if self.current_animation in self.sprites:
            self.image = self.sprites[self.current_animation]
            if self.character_type == "enemy":
                self.image = pygame.transform.flip(self.image, True, False)  # Flip horizontally

class FloatingScore(pygame.sprite.Sprite):
    """Floating score indicator that fades out"""
    def __init__(self, x, y, text, color=(255, 255, 255), lifetime=1000):
        super().__init__()
        self.font = pygame.font.Font(None, 36)
        self.text = text
        self.color = color
        self.lifetime = lifetime
        self.start_time = pygame.time.get_ticks()
        self.x = x
        self.y = y
        
        self.update_image()
        
    def update_image(self):
        """Update the floating text display"""
        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        
    def update(self, *_):
        """Update position and lifetime"""
        elapsed = pygame.time.get_ticks() - self.start_time
        
        # Move upward
        self.y -= 1
        self.rect.y = self.y
        
        # Fade out
        if elapsed > self.lifetime:
            self.kill()
        else:
            # Reduce alpha for fade effect
            progress = elapsed / self.lifetime
            alpha = int(255 * (1 - progress))
            self.image.set_alpha(alpha)
