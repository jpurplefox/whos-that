from enum import Enum
from pydantic import BaseModel


class EffectivenessRelation(Enum):
    WEAKNESS = "weakness"
    RESISTANCE = "resistance"
    IMMUNITY = "immunity"


class EffectivenessAttribute(BaseModel):
    relation: EffectivenessRelation
    element: str
    multiplier: float

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EffectivenessAttribute):
            return NotImplemented
        return (
            self.relation == other.relation
            and self.element == other.element
            and self.multiplier == other.multiplier
        )

    def __hash__(self) -> int:
        return hash((self.relation, self.element, self.multiplier))


# Gen 1 Type Effectiveness Chart
# Maps (attacking_type, defending_type) -> multiplier
TYPE_CHART: dict[tuple[str, str], float] = {
    # Normal
    ("normal", "rock"): 0.5,
    ("normal", "ghost"): 0.0,
    ("normal", "steel"): 0.5,
    
    # Fire
    ("fire", "fire"): 0.5,
    ("fire", "water"): 0.5,
    ("fire", "grass"): 2.0,
    ("fire", "ice"): 2.0,
    ("fire", "bug"): 2.0,
    ("fire", "rock"): 0.5,
    ("fire", "dragon"): 0.5,
    ("fire", "steel"): 2.0,
    
    # Water
    ("water", "fire"): 2.0,
    ("water", "water"): 0.5,
    ("water", "grass"): 0.5,
    ("water", "ground"): 2.0,
    ("water", "rock"): 2.0,
    ("water", "dragon"): 0.5,
    
    # Electric
    ("electric", "water"): 2.0,
    ("electric", "electric"): 0.5,
    ("electric", "grass"): 0.5,
    ("electric", "ground"): 0.0,
    ("electric", "flying"): 2.0,
    ("electric", "dragon"): 0.5,
    
    # Grass
    ("grass", "fire"): 0.5,
    ("grass", "water"): 2.0,
    ("grass", "grass"): 0.5,
    ("grass", "poison"): 0.5,
    ("grass", "ground"): 2.0,
    ("grass", "flying"): 0.5,
    ("grass", "bug"): 0.5,
    ("grass", "rock"): 2.0,
    ("grass", "dragon"): 0.5,
    ("grass", "steel"): 0.5,
    
    # Ice
    ("ice", "fire"): 0.5,
    ("ice", "water"): 0.5,
    ("ice", "grass"): 2.0,
    ("ice", "ice"): 0.5,
    ("ice", "ground"): 2.0,
    ("ice", "flying"): 2.0,
    ("ice", "dragon"): 2.0,
    ("ice", "steel"): 0.5,
    
    # Fighting
    ("fighting", "normal"): 2.0,
    ("fighting", "ice"): 2.0,
    ("fighting", "poison"): 0.5,
    ("fighting", "flying"): 0.5,
    ("fighting", "psychic"): 0.5,
    ("fighting", "bug"): 0.5,
    ("fighting", "rock"): 2.0,
    ("fighting", "ghost"): 0.0,
    ("fighting", "dark"): 2.0,
    ("fighting", "steel"): 2.0,
    ("fighting", "fairy"): 0.5,
    
    # Poison
    ("poison", "grass"): 2.0,
    ("poison", "poison"): 0.5,
    ("poison", "ground"): 0.5,
    ("poison", "rock"): 0.5,
    ("poison", "ghost"): 0.5,
    ("poison", "steel"): 0.0,
    ("poison", "fairy"): 2.0,
    
    # Ground
    ("ground", "fire"): 2.0,
    ("ground", "electric"): 2.0,
    ("ground", "grass"): 0.5,
    ("ground", "poison"): 2.0,
    ("ground", "flying"): 0.0,
    ("ground", "bug"): 0.5,
    ("ground", "rock"): 2.0,
    ("ground", "steel"): 2.0,
    
    # Flying
    ("flying", "electric"): 0.5,
    ("flying", "grass"): 2.0,
    ("flying", "fighting"): 2.0,
    ("flying", "bug"): 2.0,
    ("flying", "rock"): 0.5,
    ("flying", "steel"): 0.5,
    
    # Psychic
    ("psychic", "fighting"): 2.0,
    ("psychic", "poison"): 2.0,
    ("psychic", "psychic"): 0.5,
    ("psychic", "dark"): 0.0,
    ("psychic", "steel"): 0.5,
    
    # Bug
    ("bug", "fire"): 0.5,
    ("bug", "grass"): 2.0,
    ("bug", "fighting"): 0.5,
    ("bug", "poison"): 0.5,
    ("bug", "flying"): 0.5,
    ("bug", "psychic"): 2.0,
    ("bug", "ghost"): 0.5,
    ("bug", "dark"): 2.0,
    ("bug", "steel"): 0.5,
    ("bug", "fairy"): 0.5,
    
    # Rock
    ("rock", "fire"): 2.0,
    ("rock", "ice"): 2.0,
    ("rock", "fighting"): 0.5,
    ("rock", "ground"): 0.5,
    ("rock", "flying"): 2.0,
    ("rock", "bug"): 2.0,
    ("rock", "steel"): 0.5,
    
    # Ghost
    ("ghost", "normal"): 0.0,
    ("ghost", "psychic"): 2.0,
    ("ghost", "ghost"): 2.0,
    ("ghost", "dark"): 0.5,
    
    # Dragon
    ("dragon", "dragon"): 2.0,
    ("dragon", "steel"): 0.5,
    ("dragon", "fairy"): 0.0,
    
    # Dark
    ("dark", "fighting"): 0.5,
    ("dark", "psychic"): 2.0,
    ("dark", "ghost"): 2.0,
    ("dark", "dark"): 0.5,
    ("dark", "fairy"): 0.5,
    
    # Steel
    ("steel", "fire"): 0.5,
    ("steel", "water"): 0.5,
    ("steel", "electric"): 0.5,
    ("steel", "ice"): 2.0,
    ("steel", "rock"): 2.0,
    ("steel", "steel"): 0.5,
    ("steel", "fairy"): 2.0,
    
    # Fairy
    ("fairy", "fire"): 0.5,
    ("fairy", "fighting"): 2.0,
    ("fairy", "poison"): 0.5,
    ("fairy", "dragon"): 2.0,
    ("fairy", "dark"): 2.0,
    ("fairy", "steel"): 0.5,
}


class TypeEffectiveness:
    """Calculates type effectiveness for Pokemon based on their types."""

    @classmethod
    def calculate_effectiveness(
        cls, primary_type: str, secondary_type: str | None
    ) -> list[EffectivenessAttribute]:
        """Calculate all effectiveness attributes for a Pokemon.
        
        For dual-type Pokemon, multipliers stack multiplicatively.
        Example: Water/Flying takes 4x damage from Electric (2x * 2x)
        """
        # Collect all attacking types
        all_types = {
            "normal", "fire", "water", "electric", "grass", "ice",
            "fighting", "poison", "ground", "flying", "psychic", "bug",
            "rock", "ghost", "dragon", "dark", "steel", "fairy"
        }
        
        effectiveness_map: dict[str, float] = {}
        
        for attacking_type in all_types:
            # Calculate multiplier for primary type
            multiplier = TYPE_CHART.get((attacking_type, primary_type), 1.0)
            
            # If dual-type, multiply by secondary type multiplier
            if secondary_type:
                secondary_multiplier = TYPE_CHART.get(
                    (attacking_type, secondary_type), 1.0
                )
                multiplier *= secondary_multiplier
            
            effectiveness_map[attacking_type] = multiplier
        
        # Convert to list of EffectivenessAttribute
        attributes = []
        for element, multiplier in effectiveness_map.items():
            if multiplier == 0.0:
                relation = EffectivenessRelation.IMMUNITY
            elif multiplier < 1.0:
                relation = EffectivenessRelation.RESISTANCE
            elif multiplier > 1.0:
                relation = EffectivenessRelation.WEAKNESS
            else:
                # Normal effectiveness (1.0) - skip it
                continue
            
            attributes.append(
                EffectivenessAttribute(
                    relation=relation,
                    element=element,
                    multiplier=multiplier,
                )
            )
        
        return attributes
