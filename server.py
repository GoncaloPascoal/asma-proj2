
from mesa import Agent
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model import Food, Organism, NSModel

def agent_portrayal(agent: Agent):
    portrayal = {
        'Filled': 'true',
        'Layer': 0
    }

    if isinstance(agent, Food):
        portrayal['Shape'] = 'circle'
        portrayal['Color'] = 'green'
        portrayal['r'] = 0.25
        portrayal['xAlign'] = 0.2
        portrayal['yAlign'] = 0.2
    elif isinstance(agent, Organism):
        portrayal['Shape'] = 'rect'
        portrayal['Color'] = 'blue'
        portrayal['w'] = 0.25
        portrayal['h'] = 0.25
        portrayal['xAlign'] = 0.8
        portrayal['yAlign'] = 0.8

        for attr in ['speed', 'awareness', 'size', 'prob_survival', 'prob_replication']:
            portrayal[attr] = agent.__dict__.get(attr)

    return portrayal

grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)
server = ModularServer(
    NSModel,
    [grid],
    'Natural Selection Model',
    {'num_agents': 10, 'width': 10, 'height': 10}
)
