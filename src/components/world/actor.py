from enum import Enum, auto


# class REPUTATION(Enum):
#     """
#     Represents the different perceptions that other characters may have of the player.
#     This enum affects how NPCs and other game elements interact with the player.
#     """
#     UNKNOWN = auto()        # Default state, neutral perception
#     RELIABLE = auto()       # Consistently fulfills promises and commitments
#     TRUSTWORTHY = auto()    # Generally honest and dependable
#     RESPECTABLE = auto()    # Held in high regard due to actions or status
#     NOTORIOUS = auto()      # Well-known, but for negative reasons
#     UNDESIRABLE = auto()    # Actively avoided or disliked
#     FEARED = auto()         # Inspires fear or intimidation
#     REVERED = auto()        # Highly respected or worshipped
#     INFAMOUS = auto()       # Famous for negative deeds or qualities
#     HEROIC = auto()         # Known for brave or noble actions
#     SUSPICIOUS = auto()     # Not trusted, viewed with doubt

#     def __str__(self):
#         return self.name.lower().replace('_', ' ').capitalize()

#     @classmethod
#     def get_reputation(cls, value):
#         """
#         Get a REPUTATION enum value from a string.
#         Allows for case-insensitive matching and spaces in the input.
#         """
#         try:
#             return cls[value.upper().replace(' ', '_')]
#         except KeyError:
#             raise ValueError(f"'{value}' is not a valid REPUTATION")

# todo: Also define the 'npc' & 'player' classes here
