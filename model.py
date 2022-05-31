from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation

class Food(Agent):
    def __init__(self, unique_id: int, model: Model, amount: float = 1.0):
        super().__init__(unique_id, model)
        self.amount = amount

class Organism(Agent):
    MAX_ENERGY: int = 25

    def __init__(self, unique_id: int, model: Model, speed = 1, awareness = 1, size = 1, trail: bool = False):
        super().__init__(unique_id, model)

        # Genes
        self.speed = speed
        self.awareness = awareness
        self.size = size
        self.trail = trail

        self.energy = Organism.MAX_ENERGY

        self.prob_survival = 0.0
        self.prob_replication = 0.0

    def move(self):
        adjacent = self.model.grid.get_neighborhood(self.pos, moore=True)
        new_pos = self.random.choice(adjacent)
        self.model.grid.move_agent(self, new_pos)

        print(f'Agent {self.unique_id} moved to position {new_pos}')
    
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

class NSModel(Model):
    STEPS_PER_GENERATION = 150

    def __init__(self, num_agents: int, width: int, height: int, food_per_generation: int = 10) -> None:
        self.num_agents = num_agents
        self.grid = MultiGrid(width, height, torus=False)
        self.food_per_generation = food_per_generation
        self.schedule = RandomActivation(self)
        self.agents_to_remove = set()
        self.step_count = 0

        # Create agents
        for i in range(self.num_agents):
            agent = Organism(i, self)
            self.schedule.add(agent)

            # Add each agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y)) # Adds the coordinate to the agent automatically

        self.place_food()

    def remove_agent(self, agent: Agent):
        self.grid.remove_agent(agent)
        self.schedule.remove(agent)

    def place_food(self):
        cells = [(x, y) for x in range(self.grid.width) for y in range(self.grid.height)]
        cells = self.random.sample(cells, self.food_per_generation)

        for i in range(self.food_per_generation):
            food = Food(1000 + i, self)
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

                # TODO: replication logic

    def step(self):
        self.schedule.step()

        for agent in self.agents_to_remove:
            self.remove_agent(agent)
        self.agents_to_remove.clear()

        self.step_count = (self.step_count + 1) % NSModel.STEPS_PER_GENERATION
