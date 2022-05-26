from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation

# NS = Natural Selection
class NSAgent(Agent):
    """An agent with base attribute values"""

    def __init__(self, unique_id: int, model: Model, speed = 1, awareness = 1, size = 1, trail = 0) -> None:
        super().__init__(unique_id, model)
        self.speed = speed
        self.awareness = awareness # or maybe name it "reach"
        self.size = size
        self.trail = trail # binary
    
    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)
        print("Agent " + str(self.unique_id) + " moved position to " + str(new_position))

    def step(self):
        # Agent's step
        self.move()
        # print("Hi, I'm agent " + str(self.unique_id) + ".")

        



class NSModel(Model):
    """Model with a specified number of agents"""

    def __init__(self, N: int, width: int, height: int) -> None:
        self.num_agents = N
        self.grid = MultiGrid(width, height, False)
        self.schedule = RandomActivation(self)

        # Create agents
        for i in range(self.num_agents):
            a = NSAgent(i, self)
            self.schedule.add(a)

            # Add each agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y)) # Adds the coordinate to the agent automatically
    
    def step(self):
        """Advance the model by one step"""
        print("Stepping model!")
        self.schedule.step()