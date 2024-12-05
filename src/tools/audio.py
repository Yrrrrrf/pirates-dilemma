# tools/audio.py
from enum import Enum
from typing import Dict, Optional
import pygame
from pydantic import BaseModel, Field

from tools import AssetManager

class AudioType(Enum):
    """Types of audio that can be played"""
    MUSIC = "bgm"       # Background music
    UI = "ui"            # UI sounds (clicks, hovers)
    EFFECT = "sfx"    # Game effects (explosions, hits)
    AMBIENT = "env"  # Ambient sounds (wind, waves)

class AudioConfig(BaseModel):
    """Configuration for audio volumes"""
    master_volume: float = Field(default=1.0, ge=0.0, le=1.0)
    music_volume: float = Field(default=0.7, ge=0.0, le=1.0)
    effects_volume: float = Field(default=0.8, ge=0.0, le=1.0)
    ui_volume: float = Field(default=0.5, ge=0.0, le=1.0)
    ambient_volume: float = Field(default=0.6, ge=0.0, le=1.0)

class AudioManager:
    """Manages all game audio including music, sound effects, and volume control"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AudioManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        pygame.mixer.init()
        self.config = AudioConfig()
        self.current_music: Optional[str] = None
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_paused: bool = False
        
        # Initialize default volumes
        pygame.mixer.music.set_volume(self.config.music_volume * self.config.master_volume)
        
        self._initialized = True

    def load_sound(self, name: str, sound_type: AudioType) -> None:
        """Load a sound file into memory"""
        try:
            sound_path = AssetManager.get_audio_abs(name)
            if sound_type == AudioType.MUSIC:
                # Music is streamed, not loaded into memory
                pass
            else:
                self.sounds[name] = pygame.mixer.Sound(sound_path)
                # Set initial volume based on type
                volume = self._get_type_volume(sound_type)
                self.sounds[name].set_volume(volume * self.config.master_volume)
        except Exception as e:
            print(f"Error loading sound {name}: {e}")

    def play_music(self, filename: str, loop: bool = True) -> None:
        """Play background music"""
        try:
            if self.current_music != filename:
                pygame.mixer.music.load(AssetManager.get_audio_abs(filename))
                pygame.mixer.music.play(-1 if loop else 0)
                pygame.mixer.music.set_volume(self.config.music_volume * self.config.master_volume)
                self.current_music = filename
                self.music_paused = False
            else:
                print(f"Music {filename} is already playing... (.____.)")
                if self.music_paused:
                    pygame.mixer.music.unpause()
                    self.music_paused = False
        except Exception as e:
            print(f"Error playing music {filename}: {e}")

    def play_sound(self, name: str, sound_type: AudioType) -> None:
        """Play a sound effect"""
        if name not in self.sounds:
            self.load_sound(name, sound_type)
        
        try:
            volume = self._get_type_volume(sound_type)
            self.sounds[name].set_volume(volume * self.config.master_volume)
            self.sounds[name].play()
        except Exception as e:
            print(f"Error playing sound {name}: {e}")

    def _get_type_volume(self, sound_type: AudioType) -> float:
        """Get volume for specific sound type"""
        return {
            AudioType.MUSIC: self.config.music_volume,
            AudioType.UI: self.config.ui_volume,
            AudioType.EFFECT: self.config.effects_volume,
            AudioType.AMBIENT: self.config.ambient_volume
        }[sound_type]

    def set_master_volume(self, volume: float) -> None:
        """Set master volume and update all sounds"""
        self.config.master_volume = max(0.0, min(1.0, volume))
        # Update music volume
        pygame.mixer.music.set_volume(self.config.music_volume * self.config.master_volume)
        # Update all sound effects
        for sound in self.sounds.values():
            sound.set_volume(sound.get_volume() * self.config.master_volume)

    def set_type_volume(self, sound_type: AudioType, volume: float) -> None:
        """Set volume for a specific type of sound"""
        volume = max(0.0, min(1.0, volume))

        match sound_type:
            case AudioType.MUSIC: 
                self.config.music_volume = volume
                pygame.mixer.music.set_volume(volume * self.config.master_volume)
            case AudioType.UI: self.config.ui_volume = volume
            case AudioType.EFFECT: self.config.effects_volume = volume
            case AudioType.AMBIENT: self.config.ambient_volume = volume
    


        # Update volumes for loaded sounds of this type
        self._update_type_volumes(sound_type)

    def _update_type_volumes(self, sound_type: AudioType) -> None:
        """Update volumes for all sounds of a specific type"""
        volume = self._get_type_volume(sound_type)
        for sound in self.sounds.values():
            sound.set_volume(volume * self.config.master_volume)

    def toggle_music(self) -> None:
        """Toggle music pause state"""
        match self.music_paused:
            case True: pygame.mixer.music.unpause()
            case False: pygame.mixer.music.pause()
        # self.music_paused ^= True  # Toggle pause state
        self.music_paused = not self.music_paused

    def stop_music(self) -> None:
        """Stop currently playing music"""
        pygame.mixer.music.stop()
        self.current_music = None
        self.music_paused = False

    def cleanup(self) -> None:
        """Clean up audio resources"""
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        pygame.mixer.init()

# In your main.py or app initialization
audio_manager = AudioManager()
# audio_manager.play_music("8-bit-arcade.mp3", loop=True)
audio_manager.set_master_volume(0.2)
# audio_manager.set_master_volume(1)