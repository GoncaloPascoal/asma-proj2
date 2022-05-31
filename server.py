
from mesa import Agent
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model import Food, Organism, NSModel

def agent_portrayal(agent: Agent):
    portrayal = {}

    if isinstance(agent, Food):
        portrayal['Shape'] = 'circle'
        portrayal['Color'] = 'green'
        portrayal['Filled'] = 'true'
        portrayal['Layer'] = 0

    return portrayal

grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)
server = ModularServer(
    NSModel,
    [grid],
    'Natural Selection Model',
    {'num_agents': 10, 'width': 10, 'height': 10}
)
print(grid.render(server.model))
server.launch()

