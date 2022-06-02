
from typing import Tuple

from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation

def squared_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    return pow(pos1[0] - pos2[0], 2) + pow(pos1[1] - pos2[1], 2)

def clamp(val: int, lower: int, upper: int) -> int:
    return max(lower, min(val, upper))

class Food(Agent):
    def __init__(self, model: Model, amount: float = 1.0):
        super().__init__(model.next_id(), model)
        self.amount = amount

class Organism(Agent):
    MAX_ENERGY: int = 25

    MIN_SPEED: int = 1
    MAX_SPEED: int = 5
    MIN_AWARENESS: int = 0
    MAX_AWARENESS: int = 5
    MIN_SIZE: int = 1
    MAX_SIZE: int = 5

    def __init__(self, model: Model, speed = 1, awareness = 1, size = 1, trail: bool = False):
        super().__init__(model.next_id(), model)

        # Genes
        self.speed = speed
        self.awareness = awareness
        self.size = size
        self.trail = trail

        self.reset()

    def reset(self):
        self.energy = Organism.MAX_ENERGY
        self.prob_survival = 0.0
        self.prob_replication = 0.0

    def move(self):
        closest_threat, closest_food = None, None
        next_pos = None

        adjacent = self.model.grid.get_neighborhood(self.pos, moore=True)
        visible = self.model.grid.get_neighborhood(self.pos, moore=True, radius=self.awareness)

        # Determine closest threat and closest source of food
        for agent in self.model.grid.iter_cell_list_contents(visible):
            if isinstance(agent, Organism) and Organism.can_eat(agent, self):
                if not closest_threat or squared_distance(self.pos, closest_threat.pos) < squared_distance(self.pos, agent.pos):
                    closest_threat = agent
            elif isinstance(agent, Food):
                if not closest_food or squared_distance(self.pos, closest_food.pos) < squared_distance(self.pos, agent.pos):
                    closest_food = agent

        if closest_threat:
            for pos in adjacent:
                if not next_pos or squared_distance(pos, closest_threat.pos) > squared_distance(next_pos, closest_threat.pos):
                    next_pos = pos
        elif closest_food:
            for pos in adjacent:
                if not next_pos or squared_distance(pos, closest_food.pos) < squared_distance(next_pos, closest_food.pos):
                    next_pos = pos
        else:
            next_pos = self.random.choice(adjacent)

        self.model.grid.move_agent(self, next_pos)

    @staticmethod
    def can_eat(organism1, organism2) -> bool:
        return organism1.size > organism2.size

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
        if self.prob_replication < 1.0:
            self.eat(1.0)
            self.model.agents_to_remove.add(organism)

    def step(self):
        if self in self.model.agents_to_remove:
            return

        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        if len(cell_contents) > 1:
            # Agent is not alone in cell
            for other in cell_contents:
                if other in self.model.agents_to_remove:
                    continue

                if isinstance(other, Food):
                    # Organism is in cell with food
                    amount = other.amount
                    if self.trail:
                        amount = min(0.5, other.amount)
                    self.eat_food(other, amount)
                elif isinstance(other, Organism):
                    # Organism is in cell with another agent
                    if self.size > other.size: # If agent is bigger than other, eat it
                        self.eat_organism(other)

        # Make the next move
        self.move()
    
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
        if self.model.random.random() <= self.model.speed_mutation_rate:
            size += 1 if self.model.random.randint(0, 1) else -1
            size = clamp(size, Organism.MIN_SIZE, Organism.MAX_SIZE)

        return Organism(self.model, speed, awareness, size, self.trail)

class NSModel(Model):
    STEPS_PER_GENERATION = 25

    def __init__(self, num_agents: int, width: int, height: int,
            food_per_generation: int = 10, speed_mutation_rate: float = 0.1,
            awareness_mutation_rate: float = 0.05, size_mutation_rate: float = 0.05) -> None:
        super().__init__()

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
        for _ in range(num_agents):
            agent = Organism(self)
            self.schedule.add(agent)

        self.place_agents(init=True)
        self.place_food()

    def remove_agent(self, agent: Agent):
        self.grid.remove_agent(agent)
        self.schedule.remove(agent)

    def place_agents(self, init=False):
        for agent in self.schedule.agents:
            pos = self.random.sample(self.border_cells, 1)[0]
            if init:
                self.grid.place_agent(agent, pos)
            else:
                self.grid.move_agent(agent, pos)

    def place_food(self):
        cells = self.random.sample(self.center_cells, self.food_per_generation)

        for i in range(self.food_per_generation):
            food = Food(self)
            self.schedule.add(food)
            self.grid.place_agent(food, cells[i])

    def new_generation(self):
        for agent in self.schedule.agents:
            if isinstance(agent, Food):
                self.remove_agent(agent)
            elif isinstance(agent, Organism):
                survives = self.random.random() <= agent.prob_survival
                replicates = self.random.random() <= agent.prob_replication

                if not survives:
                    self.remove_agent(agent)
                elif replicates:
                    replica = agent.replicate()
                    self.schedule.add(replica)
                    self.grid.place_agent(replica, (0, 0))

                agent.reset()

        self.place_agents()
        self.place_food()
        self.generation += 1

    def step(self):
        self.schedule.step()

        for agent in self.agents_to_remove:
            self.remove_agent(agent)
        self.agents_to_remove.clear()

        self.step_count = (self.step_count + 1) % NSModel.STEPS_PER_GENERATION

        if self.step_count == 0:
            self.new_generation()
