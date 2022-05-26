from mesa import Agent


# NS = Natural Selection
class NSAgent(Agent):
    """An agent with base attribute values"""

    def __init__(self, unique_id: int, model: Model) -> None:
        super().__init__(unique_id, model)
        self.speed = 1
        self.awareness = 1 # or maybe name it "reach"
        self.size = 1
        self.trail = 0 # binary

    def step(self):
        # The agent's step will go here.
        print("Hi, I'm agent " + str(self.unique_id) + ".")

