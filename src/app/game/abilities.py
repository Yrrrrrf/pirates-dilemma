from pydantic import BaseModel, Field
from app.core.entities.sprites import AnimationState

class Ability(BaseModel):
    """Represents a player ability with cooldown management"""
    name: str
    cooldown: float = Field(default=1.0, ge=0.0)
    current_cooldown: float = Field(default=0.0, ge=0.0)
    
    def update(self, dt: float) -> None:
        """Update ability cooldown"""
        if self.current_cooldown > 0:
            self.current_cooldown = max(0, self.current_cooldown - dt)
    
    def is_ready(self) -> bool:
        """Check if ability is ready to use"""
        return self.current_cooldown <= 0
    
    def trigger(self) -> None:
        """Trigger the ability and start cooldown"""
        self.current_cooldown = self.cooldown
