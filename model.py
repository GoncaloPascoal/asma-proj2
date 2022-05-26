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
    

    def step(self):
        # Agent's step
        print("Hi, I'm agent " + str(self.unique_id) + ".")

        



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
        self.schedule.step()