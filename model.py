from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation

'''
Agent Types:
0 -> food
1 -> half food
2 -> living being
'''

# NS = Natural Selection
class NSAgent(Agent):
    """An agent with base attribute values"""

    def __init__(self, unique_id: int, model: Model, agentType = 0, speed = 1, awareness = 1, size = 1, trail = 0) -> None:
        super().__init__(unique_id, model)

        self.speed = speed
        self.size = size
        self.trail = trail # binary
        self.awareness = awareness # or maybe name it "reach"

        self.agentType = agentType
        self.daysToLiveBuffer = 1
    
    def move(self):
        if self.agentType != 2:
            print("Food is not supposed to move")
            return

        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)
        print("Agent " + str(self.unique_id) + " moved position to " + str(new_position))

    # Agent's step
    def step(self):
        # Check current square
        cellmates = self.model.grid.get_cell_list_contents([self.pos]) # maybe model food as agent???

        # agent is not alone in cell
        if len(cellmates) > 1:
            for other in cellmates:
                # living being is in cell with food
                if self.agentType == 2 and other.agentType != 2:
                    if self.trail: # has the pheromone trail attribute, i.e. eats only half

                        # TODO formula for 50-50 to live until next day
                        

                        other.agentType = 1 # changed to half food
                        
                    else:           # eats whole food
                        self.livesToNextDay += 1
                        self.grid.remove_agent(other) # food no longer exists
                
                # living being is in cell with another living being
                elif self.agentType == 2 and other.agentType == 2:
                    if self.size > other.size: # if agent is bigger than other, eat it
                        self.size += 1
                        self.daysToLiveBuffer += other.size
                        self.grid.remove_agent(other)

        # Make the next move
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

        # Add here place agent in edges of grid? 
        # 

        self.schedule.step()