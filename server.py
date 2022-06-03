
from matplotlib.colors import to_hex

from mesa import Agent, Model
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.TextVisualization import TextData

from model import Food, Organism, NSModel

def generation(model: Model) -> str:
    return f'Generation: {model.generation}'

def agent_portrayal(agent: Agent):
    portrayal = {
        'Filled': 'true',
        'Layer': 0
    }

    if isinstance(agent, Food):
        portrayal['Shape'] = 'circle'
        portrayal['Color'] = 'green'
        portrayal['r'] = 0.25 * agent.amount
        portrayal['xAlign'] = 0.2
        portrayal['yAlign'] = 0.2
    elif isinstance(agent, Organism):
        w = 0.2 + 0.4 * (agent.size - Organism.MIN_SIZE) / (Organism.MAX_SIZE - Organism.MIN_SIZE)
        h = 0.2 + 0.4 * (agent.awareness - Organism.MIN_AWARENESS) / (Organism.MAX_AWARENESS - Organism.MIN_AWARENESS)

        speed_rate = (agent.speed - Organism.MIN_SPEED) / (Organism.MAX_SPEED - Organism.MIN_SPEED)

        portrayal['Shape'] = 'rect'
        portrayal['Color'] = to_hex([
            0.1 + 0.1 * speed_rate,
            0.2 + 0.1 * speed_rate,
            0.4 + 0.5 * speed_rate
        ])
        portrayal['w'] = w
        portrayal['h'] = h
        portrayal['xAlign'] = 0.9 - w / 2
        portrayal['yAlign'] = 0.9 - h / 2

        for attr in ['speed', 'awareness', 'size', 'energy', 'prob_survival', 'prob_replication']:
            portrayal[attr] = agent.__dict__.get(attr)

    return portrayal

grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)
chart = ChartModule(
    [{"Label": "Number", "Color": "#0000FF"}], data_collector_name="datacollector"
)

server = ModularServer(
    NSModel,
    [generation, grid, chart],
    'Natural Selection Model',
    {'num_agents': 10, 'width': 10, 'height': 10}
)
