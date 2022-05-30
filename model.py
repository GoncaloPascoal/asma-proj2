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
        needed_for_survival = 1.0 - prob_survival
        used_for_survival = min(amount, needed_for_survival)
        amount -= used_for_survival
        self.prob_survival += used_for_survival

        needed_for_replication = 1.0 - prob_replication
        used_for_replication = min(amount, needed_for_replication)
        self.prob_replication += used_for_replication

    def eat_food(self, food: Agent, amount: float):
        if self.prob_replication < 1.0:
            self.eat(amount)
            food.amount -= amount
            if food.amount <= 0:
                self.model.agents_to_remove.append(food)

    def eat_organism(self, organism: Agent):
        if self.prob_replication < 1.0:
            self.eat(1.0)
            self.model.agents_to_remove.append(organism)

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
    def __init__(self, num_agents: int, width: int, height: int) -> None:
        self.num_agents = num_agents
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        self.agents_to_remove = set()

        # Create agents
        for i in range(self.num_agents):
            a = Organism(i, self)
            self.schedule.add(a)

            # Add each agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y)) # Adds the coordinate to the agent automatically

    def step(self):
        print("Stepping model!")
        self.schedule.step()

        for agent in self.agents_to_remove:
            self.grid.remove_agent(agent)
            self.schedule.remove(agent)
        self.agents_to_remove.clear()
