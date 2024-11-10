# Nihilis - Design Document

_Version 1.0_

## Game Overview

Nihilis is an ASCII-based fantasy role-playing game featuring a procedurally generated living world. Drawing inspiration from Dwarf Fortress, Moonring, and ASCII Sector, it combines deep simulation with accessible gameplay mechanics.

### Core Design Pillars

1. **Living World**: A reactive environment where player actions have lasting consequences
2. **Multiple Paths**: Various progression systems supporting different playstyles
3. **Emergent Storytelling**: Stories arise from the interaction of systems rather than scripted events
4. **Accessibility**: Complex systems presented through simple interfaces
5. **Historical Depth**: World evolution through distinct epochs

## Technical Architecture

### Display System
```
Primary: ASCII-based terminal display
Alternative: Pyxel-based tile system (configurable at build)

Core Display Components:
- Main view window
- Status bar
- Message log
- Context-sensitive command list
- Mini-map (when applicable)
```

## Core Systems

### 1. World Generation Engine

```python
class WorldGeneration:
    def __init__(self, settings: WorldGenSettings):
        self.chaos_level = settings.chaos  # Violence between factions
        self.wildness = settings.wildness  # Monster/threat density
        self.climate_model = ClimateModel()
        self.terrain_generator = TerrainGenerator()
        self.epoch_manager = EpochManager
        
    def generate_world(self) -> World:
        # 1. Generate physical geography
        # 2. Simulate initial climate patterns
        # 3. Generate initial civilizations
        # 4. Run age of myth simulation to create notable landmarks
        pass
```

**Key Components:**

- Terrain generation (heightmap-based)
- Climate system (temperature, rainfall, biomes)
- Historical event generator
- Settlement placer
- Trade route calculator

### 2. Region Management System

```
pythonCopyclass RegionSystem:
    def __init__(self):
        self.region_map = RegionalMap()
        self.address_resolver = RegionAddressResolver()
        
    def calculate_travel_path(self, start_region, end_region):
        if self.is_local_movement(start_region, end_region):
            return self.a_star_pathfinding(start_region, end_region)
        return self.regional_path_resolution(start_region, end_region)
```

### 3. Time Management

```
pythonCopyclass TimeManager:
    def __init__(self):
        self.current_tick = 0
        self.scale_factors = {
            'regional': 3600,    # 1 hour per tick
            'local': 60,         # 1 minute per tick
            'combat': 10         # 10 seconds per tick
        }
```

### 4. Entity Component System (ECS)

```python
class Entity:
    def __init__(self):
        self.components = {}
        self.id = generate_unique_id()

class World:
    def __init__(self):
        self.entities = {}
        self.systems = []
```

**Core Components:**
- Position
- Physical (size, weight, material)
- Actor (for NPCs and player)
- Inventory
- Skills
- Knowledge
- Relationships
- Personality

### 5. NPC Intelligence System

```python
class NPCMind:
    def __init__(self):
        self.personality = PersonalityTraits()
        self.memory = MemorySystem()
        self.relationships = RelationshipGraph()
        self.goals = GoalPlanner()
        
    def process_event(self, event: Event):
        impact = self.evaluate_impact(event)
        moral_reaction = self.evaluate_morality(event)
        self.plan_response(event, impact, moral_reaction)
```

**Key Features:**
- Personality matrix (based on Big Five + moral foundations)
- Memory system with emotion tagging
- Social network modeling
- Goal-oriented action planning
- Knowledge propagation system

### 6. Economic System

```python
class EconomicSimulator:
    def __init__(self):
        self.trade_routes = Graph()
        self.markets = {}
        self.resources = ResourceManager()
        
    def update(self):
        self.update_prices()
        self.process_trade()
        self.update_production()
```

**Tracked Metrics:**
- Resource availability
- Trade volume
- Market prices
- Production capacity
- Transportation costs

### 7. Environmental System

```python
class Environment:
    def __init__(self):
        self.ecosystem_health = {}
        self.climate_state = {}
        self.disaster_risk = {}
        
    def process_change(self, change: WorldChange):
        self.update_ecosystem(change)
        self.calculate_risks()
        self.trigger_events()
```

**Monitoring:**
- Ecosystem health indices
- Climate patterns
- Natural disaster risks
- Resource depletion
- Population dynamics

## Gameplay Systems

### Epoch System

#### Overview

The world progresses through seven distinct epochs, each with unique characteristics and gameplay opportunities:

#### 1. Age of Myth

- Gods compete for Bailiwicks (domains of power)
- World formation and divine conflicts
- Epoch ends when all Bailiwicks are claimed or lost to Chaos

#### 2. Age of Dreams

```python
Copyclass AgeOfDreams:
    def __init__(self):
        self.tribes = []
        self.beasts_of_legend = []
        self.promised_lands = {}
    
    def evaluate_settlement_conditions(self, tribe, region):
        return region.matches_promised_land_criteria(tribe.criteria)
```

- Tribal/Nomadic societies only, moving slowly on a regular basis
- Beasts of Legend roam freely
- Focus on survival, exploration, combat
- Ends when 80% of tribes find their promised lands

#### 3. Age of Kings

- Settlement growth and expansion
- Development of agriculture and fortifications
- Kingdom formation and territorial disputes
- Monster incursions led by surviving Beasts of Legend
- Ends at 80% land mass claimed

#### 4. Age of Empire

- Kingdom consolidation
- Emergence of dominant power
- Vassalage and conquest
- Ends at 80% unified territory

#### 5. Age of Corruption

- Imperial decline
- Political intrigue and betrayal
- Technological and magical experimentation
- Ends at 80% territory loss

#### 6. Age of Collapse

- Mass conflict between city-states
- Assassination and warfare
- Societal retreat
- Ends when 80% of nations fall

#### 7. Age of Shadow

- Survival in ruins
- Monster dominance
- Nomadic existence
- Final playable epoch

### Character System

#### Attributes

```
pythonCopyclass Attributes:
    def __init__(self):
        self.strength = RandomRange(3, 18)
        self.dexterity = RandomRange(3, 18)
        self.constitution = RandomRange(3, 18)
        self.intelligence = RandomRange(3, 18)
        self.wisdom = RandomRange(3, 18)
        self.charisma = RandomRange(3, 18)
        
    @property
    def max_value(self):
        return 25  # Maximum attainable through gameplay
```

#### Races

```
pythonCopyclass Race:
    races = {
        'human': {'attribute_mods': {}, 'abilities': ['adaptable']},
        'dwarf': {'attribute_mods': {'con': 2}, 'abilities': ['darkvision']},
        'elf': {'attribute_mods': {'dex': 2}, 'abilities': ['keen_senses']},
        'gnome': {'attribute_mods': {'int': 2}, 'abilities': ['arcane_affinity']},
        'halfling': {'attribute_mods': {'dex': 2}, 'abilities': ['lucky']},
        'half_elf': {'attribute_mods': {'cha': 2}, 'abilities': ['versatile']},
        'half_orc': {'attribute_mods': {'str': 2}, 'abilities': ['enduring']}
    }
```

#### Skills System

```
pythonCopyclass SkillSystem:
    categories = {
        'combat': ['melee', 'ranged', 'tactics', 'defense'],
        'social': ['persuasion', 'intimidation', 'etiquette', 'deception'],
        'exploration': ['survival', 'navigation', 'perception', 'stealth'],
        'trade': ['bargaining', 'appraisal', 'networking', 'logistics'],
        'civic': ['leadership', 'administration', 'engineering', 'law'],
        'sagecraft': ['history', 'nature', 'medicine', 'investigation'],
        'arcane': ['spellcraft', 'ritual', 'leyline_sensing', 'artifact_lore'],
        'politics': ['intrigue', 'diplomacy', 'manipulation', 'statecraft']
    }
```

#### Class Structure

```python
class CharacterCreation:
    backgrounds = {
        'war_refugee': {
            'skills': ['survival', 'stealth'],
            'equipment': ['worn_clothes', 'knife'],
            'starting_resources': 'minimal'
        },
        'noble_child': {
            'skills': ['etiquette', 'literacy'],
            'equipment': ['fine_clothes', 'signet_ring'],
            'starting_resources': 'wealthy'
        }
        # ... more backgrounds
    }
```

### Progression Systems

#### **1. Combat Skills**

- Weapon proficiencies
- Tactical abilities
- Combat maneuvers

#### **2. Social Skills**

- Reputation system
- Influence points
- Relationship networks

#### **3. Exploration**

- Territory mapping
- Resource discovery
- Ruins investigation
- Survival & resource management
- Environmental adaptation

#### **4. Trade Skills**

- Trade proficiencies
- Market manipulation
- Route establishment
- Resource management
- Merchant networks
- Business ventures

#### **5. Political Skills**

- Faction standings, influence, & intrigue
- Political capital & leverage
- Leadership abilities & consensus building
- Diplomatic relations
- Power brokering
- Strategic alliances

#### **6. Civic Skills**

- Property management
- Infrastructure development
- Community leadership
- Resource allocation

#### **7. Sagecraft**

- Knowledge accumulation
- Research capabilities
- Artifact study
- Historical investigation

#### **8. Arcanistry**

- Leyline manipulation
- Spell mastery
- Ritual crafting
- Magical theory

### Quest Generation System

```python
class QuestGenerator:
    def __init__(self):
        self.templates = QuestTemplates()
        self.conflict_generator = ConflictGenerator()
        
    def generate_quest(self, context: WorldContext) -> Quest:
        conflicts = self.conflict_generator.get_active_conflicts(context)
        template = self.templates.select_appropriate(conflicts)
        return self.populate_quest(template, context)
```

### Interaction Systems

1. **Dialog System**
```python
class DialogSystem:
    def __init__(self):
        self.conversation_state = None
        self.npc_memory = None
        
    def start_conversation(self, player: Entity, npc: Entity):
        context = self.gather_context(player, npc)
        self.conversation_state = ConversationState(context)
```

2. **Action System**
```python
class ActionSystem:
    def __init__(self):
        self.available_actions = {}
        self.action_consequences = ActionConsequenceCalculator()
        
    def get_available_actions(self, actor: Entity, context: Context) -> List[Action]:
        return [action for action in self.available_actions
                if action.requirements_met(actor, context)]
```

## Technical Implementation Notes

### Data Structures
1. **World State**
   - Chunked map storage
   - Entity component system
   - Relationship graphs
   - Event history trees

2. **AI Systems**
   - Behavior trees for NPCs
   - A* pathfinding
   - Knowledge graphs
   - Goal-oriented action planning

### Performance Considerations
1. **Optimizations**
   - Lazy loading of distant chunks
   - Event aggregation for distant events
   - Simplified simulation for non-focal areas
   - Memory pooling for frequently created/destroyed objects

2. **Memory Management**
   - Cached procedural generation
   - Component pooling
   - Event cleanup policies
   - History compression

### Save System
```python
class SaveSystem:
    def save_game(self, world_state: WorldState):
        compressed_state = self.compress_state(world_state)
        serialized_state = self.serialize_state(compressed_state)
        self.write_to_disk(serialized_state)
```

## Development Roadmap

### Phase 1: Core Systems

#### Milestone 1: Basic Engine

1. Initialize TCOD window with correct dimensions
2. Implement basic input handling system
3. Create main game loop
4. Set up multiple console layers for UI
5. Implement basic logging system
6. Game State Management
7. UI Management
8. Component Integration
9. Performance Monitoring
10. Configuration Management
11. Testing Framework

#### Milestone 2: Basic world generation

1. Heightmap Generation system
2. Biome Assignment system
3. Region Partitioning system
4. World State serialization
5. World Visualization system
6. Testing Framework

#### Milestone 3: Epoch & Historical system framework

1. Mythic epoch generation (gods, powers, notable landmarks, beasts of legend born). Ends when all Bailiwicks are assigned to Gods.
2. Age of Dreams generation (beasts of legends, tribes searching for promised land). Ends when 80% of remaining tribes have Settled.
3. Age of Kings generation (settled tribes expanding, defending against beasts of legends, their monstrous followers, and each other). Ends when 80% of game map is populated by Kingdoms.
4. Age of Empire generation (one great Kingdom expands and becomes dominant, surviving beasts of legend go dormant). Ends when 80% of claimed territory is owned by one Kingdom.
5. Age of Corruption generation (Empire in decline balkanizes itself from internal strife and external factors, including waking Beasts of Legend, their monsters, and non-Imperial civilizations acting as barbarians, pirates, or raiders). Ends when 80% of Empire has balkanized.
6. Age of Collapse generation (city-states war with each other and monster incursions led by Beasts of Legend increase, civilizations and leaders fall, individuals desert the falling civilizations to try to preserve themselves). Ends when 80% of remaining civilizations have fallen.
7. Age of Shadow generation (post-apocalyptic scenario, remaining individuals try to survive in world dominated by monsters, beasts of legend, and shadowy overlords). Does not end... for now.

#### Milestone 4: Character creation

(tbd)

#### Milestone 5: Regional Management

(tbd)

#### Milestone 6: Movement and basic interaction

(tbd)

#### Milestone 7: Save/Load system

(tbd)



### Phase 2: Simulation & Emulation Systems

#### Milestone 1: NPC AI, relationships, and memory

#### Milestone 2: Economic emulation

#### Milestone 3: Environmental emulation

#### Milestone 4: Civic emulation

#### Milestone 5: Political emulation



### Phase 3: Content and Polish

#### Milestone 1: Dynamic Story Arc Generation

- Civic, terrain, politlcal, economic, history, and npc alteration based on player action
- "Character inventory" for reusing recurring characters in dramatic situations
- Dynamic encounter spawns based on player history, regional history, and relationships
- Arcs constructed from individual beats which are executed as dynamic encounter spawns

#### Milestone 2: Dialog System

#### Milestone 3: UI Improvements

Quest generation

1. Dialog system
2. UI improvements
3. Balance and testing

## Testing Strategy

1. **Unit Tests**
   - Core systems
   - Generation algorithms
   - AI behavior

2. **Integration Tests**
   - System interaction
   - State persistence
   - Performance benchmarks

3. **Playtesting Focus**
   - World coherence
   - Game balance
   - User experience
   - Performance under load