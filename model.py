
from math import sqrt
from typing import Tuple

from mesa import Agent, DataCollector, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation

def squared_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    return pow(pos1[0] - pos2[0], 2) + pow(pos1[1] - pos2[1], 2)

def distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    return sqrt(squared_distance(pos1, pos2))

def clamp(val, lower, upper):
    return max(lower, min(val, upper))

class PheromoneTrail(Agent):
    MAX_STRENGTH = 10

    def __init__(self, model: Model, creator: int, came_from: Tuple[int, int],
            strength_reduction: int = 0) -> None:
        super().__init__(model.next_id(), model)
        self.creator = creator
        self.came_from = came_from
        self.strength = PheromoneTrail.MAX_STRENGTH - strength_reduction

    def step(self):
        self.strength -= 1
        if self.strength == 0:
            self.model.agents_to_remove.add(self)

class Food(Agent):
    def __init__(self, model: Model, amount: float = 1.0):
        super().__init__(model.next_id(), model)
        self.amount = amount

class Organism(Agent):
    MAX_ENERGY: float = 150.0

    MIN_SPEED: int = 1
    MAX_SPEED: int = 6

    MIN_AWARENESS: int = 0
    MAX_AWARENESS: int = 6

    MIN_SIZE: float = 0.5
    MAX_SIZE: float = 2.0
    MAX_SIZE_MUTATION = 0.15
    SIZE_TO_EAT: float = 0.20

    MAX_TRAIL_LENGTH: int = 5

    def __init__(self, model: Model, speed: int = 3, awareness: int = 2,
            size: float = 1.0, trail: bool = False):
        super().__init__(model.next_id(), model)

        # Genes
        self.speed = speed
        self.awareness = awareness
        self.size = size
        self.trail = trail

        self.food_positions = set()
        self.trail_length = 0

        self.age = 0

        self.reset_move_ticks()
        self.reset()

    def reset_move_ticks(self):
        self.move_ticks = 1 + Organism.MAX_SPEED - self.speed

    def reset(self):
        self.food_positions.clear()
        self.energy = Organism.MAX_ENERGY
        self.prob_survival = 0.0
        self.prob_replication = 0.0

    def move(self):
        closest_threat, closest_food, strongest_trail = None, None, None
        next_pos = None

        adjacent = self.model.grid.get_neighborhood(self.pos, moore=True)
        visible = self.model.grid.get_neighborhood(self.pos, moore=False, radius=self.awareness)

        # Determine closest threat and closest source of food
        for agent in self.model.grid.iter_cell_list_contents(visible):
            if isinstance(agent, Organism) and Organism.can_eat(agent, self):
                if not closest_threat or squared_distance(self.pos, closest_threat.pos) < squared_distance(self.pos, agent.pos):
                    closest_threat = agent
            elif isinstance(agent, Food):
                if not closest_food or squared_distance(self.pos, closest_food.pos) < squared_distance(self.pos, agent.pos):
                    closest_food = agent

        if self.trail:
            for agent in self.model.grid.iter_cell_list_contents([self.pos]):
                if isinstance(agent, PheromoneTrail) and agent.creator != self.unique_id:
                    if (not strongest_trail or agent.strength > strongest_trail.strength) and agent.came_from != self.pos:
                        strongest_trail = agent

        if closest_threat:
            for pos in adjacent:
                if not next_pos or squared_distance(pos, closest_threat.pos) > squared_distance(next_pos, closest_threat.pos):
                    next_pos = pos
        elif closest_food:
            for pos in adjacent:
                if not next_pos or squared_distance(pos, closest_food.pos) < squared_distance(next_pos, closest_food.pos):
                    next_pos = pos
        elif strongest_trail and self.random.random() <= strongest_trail.strength / PheromoneTrail.MAX_STRENGTH:
            next_pos = strongest_trail.came_from
        else:
            next_pos = self.random.choice(adjacent)

        required_energy = self.move_energy(distance(self.pos, next_pos))
        if self.energy >= required_energy:
            self.energy -= required_energy

            came_from = self.pos
            self.model.grid.move_agent(self, next_pos)
            if self.trail_length > 0:
                trail = PheromoneTrail(self.model, self.unique_id, came_from, Organism.MAX_TRAIL_LENGTH - self.trail_length)
                self.model.schedule.add(trail)
                self.model.grid.place_agent(trail, self.pos)
                self.trail_length -= 1

    def move_energy(self, distance_moved: float) -> float:
        return 0.35 * pow(self.size, 3) * pow(self.speed, 2) * distance_moved + 0.4 * self.awareness

    @staticmethod
    def can_eat(organism1, organism2) -> bool:
        return organism1.size / organism2.size > (1 + Organism.SIZE_TO_EAT)

    def eat(self, amount: float):
        needed_for_survival = 1.0 - self.prob_survival
        used_for_survival = min(amount, needed_for_survival)
        amount -= used_for_survival
        self.prob_survival += used_for_survival

        needed_for_replication = 1.0 - self.prob_replication
        used_for_replication = min(amount, needed_for_replication)
        self.prob_replication += used_for_replication

    def eat_food(self, food: Agent, amount: float):
        if self.prob_replication < 1.0:
            self.eat(amount)
            food.amount -= amount
            if food.amount <= 0:
                self.model.agents_to_remove.add(food)

    def eat_organism(self, organism: Agent):
        # Organisms with the trail gene won't eat each other
        if self.prob_replication < 1.0 and not (self.trail and organism.trail):
            self.eat(1.0)
            self.model.agents_to_remove.add(organism)
            self.model.num_organisms -= 1

    def step(self):
        if self in self.model.agents_to_remove:
            return

        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        if len(cell_contents) > 1:
            # Agent is not alone in cell
            for other in cell_contents:
                if other in self.model.agents_to_remove:
                    continue

                if isinstance(other, Food) and other.pos not in self.food_positions:
                    # Organism is in cell with food
                    amount = other.amount
                    if self.trail:
                        amount = min(0.5, other.amount)
                        if other.amount > 0.5:
                            self.food_positions.add(other.pos)
                            self.trail_length = Organism.MAX_TRAIL_LENGTH
                    self.eat_food(other, amount)
                elif isinstance(other, Organism):
                    # Organism is in cell with another agent
                    if self.size > other.size: # If agent is bigger than other, eat it
                        self.eat_organism(other)

        self.move_ticks -= 1
        if self.move_ticks == 0:
            self.move()
            self.reset_move_ticks()

    def replicate(self):
        speed = self.speed
        awareness = self.awareness
        size = self.size

        # Speed mutation
        if self.model.random.random() <= self.model.speed_mutation_rate:
            speed += 1 if self.model.random.randint(0, 1) else -1
            speed = clamp(speed, Organism.MIN_SPEED, Organism.MAX_SPEED)
        
        # Awareness mutation
        if self.model.random.random() <= self.model.awareness_mutation_rate:
            awareness += 1 if self.model.random.randint(0, 1) else -1
            awareness = clamp(awareness, Organism.MIN_AWARENESS, Organism.MAX_AWARENESS)

        # Size mutation
        if self.model.random.random() <= self.model.size_mutation_rate:
            # Within [-MAX_SIZE_MUTATION, MAX_SIZE_MUTATION]
            size += 2 * Organism.MAX_SIZE_MUTATION * self.model.random.random() - Organism.MAX_SIZE_MUTATION
            size = clamp(size, Organism.MIN_SIZE, Organism.MAX_SIZE)

        return Organism(self.model, speed, awareness, size, self.trail)

class NSModel(Model):
    STEPS_PER_GENERATION = 120

    def __init__(
            self,
            seed = None, num_organisms: int = 25, width: int = 20, height: int = 20,
            food_per_generation: int = 60, speed_mutation_rate: float = 0.08,
            awareness_mutation_rate: float = 0.08, size_mutation_rate: float = 0.08,
            initial_speed: int = 3, initial_awareness: int = 2,
            initial_size: float = 1.0, initial_trail: float = 0.5
        ) -> None:
        super().__init__()

        self.num_organisms = num_organisms
        self.grid = MultiGrid(width, height, torus=False)
        self.food_per_generation = food_per_generation

        self.speed_mutation_rate = speed_mutation_rate
        self.awareness_mutation_rate = awareness_mutation_rate
        self.size_mutation_rate = size_mutation_rate

        self.schedule = RandomActivation(self)
        self.agents_to_remove = set()

        self.border_cells = (
            {(0, y) for y in range(self.grid.height)} |
            {(x, 0) for x in range(self.grid.width)} |
            {(self.grid.width - 1, y) for y in range(self.grid.height)} |
            {(x, self.grid.height - 1) for x in range(self.grid.width)}
        )
        self.center_cells = (
            {(x, y) for x in range(self.grid.width) for y in range(self.grid.height)} -
            self.border_cells
        )

        self.generation = 1
        self.step_count = 0

        # Create agents
        for i in range(num_organisms):
            trail = i < num_organisms * initial_trail
            agent = Organism(self, initial_speed, initial_awareness, initial_size, trail)
            self.schedule.add(agent)

        self.place_agents(init=True)
        self.place_food()

        # Initialize data collectors
        self.dc_num_organisms = DataCollector(
            model_reporters={'Organisms': 'num_organisms'}
        )
        self.dc_properties = DataCollector(
            model_reporters={
                'Speed': lambda _: self.property_average('speed'),
                'Awareness': lambda _: self.property_average('awareness'),
                'Size': lambda _: self.property_average('size')
            }
        )
        self.dc_trail_percentage = DataCollector(
            model_reporters={'Trail Percentage': self.trail_percentage}
        )
        self.dc_age = DataCollector(
            model_reporters={'Age': lambda _: self.property_average('age')}
        )

        self.data_collectors = [self.dc_num_organisms, self.dc_properties,
            self.dc_trail_percentage, self.dc_age]
        self.update_data_collectors()

    def remove_agent(self, agent: Agent):
        self.grid.remove_agent(agent)
        self.schedule.remove(agent)

    def place_agents(self, init=False):
        if len(self.border_cells) >= len(self.schedule.agents):
            positions = self.random.sample(self.border_cells, len(self.schedule.agents))
        else:
            positions = self.random.choices(list(self.border_cells), k=len(self.schedule.agents))

        for i, agent in enumerate(self.schedule.agents):
            if init:
                self.grid.place_agent(agent, positions[i])
            else:
                self.grid.move_agent(agent, positions[i])

    def place_food(self):
        cells = self.random.sample(self.center_cells, self.food_per_generation)

        for i in range(self.food_per_generation):
            food = Food(self)
            self.schedule.add(food)
            self.grid.place_agent(food, cells[i])

    def property_average(self, prop_name: str) -> float:
        acc, count = 0, 0
        for agent in self.schedule.agents:
            if isinstance(agent, Organism):
                acc += getattr(agent, prop_name)
                count += 1
        return acc / count if count != 0 else 0.0

    def trail_percentage(self) -> float:
        acc, count = 0, 0
        for agent in self.schedule.agents:
            if isinstance(agent, Organism):
                acc += int(agent.trail)
                count += 1
        return 100 * acc / count if count != 0 else 0.0

    def update_data_collectors(self):
        for dc in self.data_collectors:
            dc.collect(self)

    def new_generation(self):
        for agent in self.schedule.agents:
            if isinstance(agent, Organism):
                survives = self.random.random() <= agent.prob_survival
                replicates = self.random.random() <= agent.prob_replication

                if not survives:
                    self.remove_agent(agent)
                    self.num_organisms -= 1
                else:
                    agent.age += 1
                    if replicates:
                        replica = agent.replicate()
                        self.schedule.add(replica)
                        self.grid.place_agent(replica, (0, 0))
                        self.num_organisms += 1

                agent.reset()
            else:
                self.remove_agent(agent)

        self.place_agents()
        self.place_food()
        self.generation += 1

        self.update_data_collectors()

    def step(self):
        self.schedule.step()

        for agent in self.agents_to_remove:
            self.remove_agent(agent)
        self.agents_to_remove.clear()

        self.step_count = (self.step_count + 1) % NSModel.STEPS_PER_GENERATION

        if self.step_count == 0:
            self.new_generation()
