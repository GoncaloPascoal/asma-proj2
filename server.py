
from matplotlib.colors import to_hex

from mesa import Agent, Model
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

from model import Food, Organism, NSModel, PheromoneTrail

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
    elif isinstance(agent, PheromoneTrail):
        portrayal['Shape'] = 'arrowHead'
        portrayal['Color'] = to_hex(
            [0.95, 0.5, 0.95, 0.1 + 0.5 * agent.strength / PheromoneTrail.MAX_STRENGTH],
            keep_alpha=True
        )
        portrayal['scale'] = 0.3
        portrayal['heading_x'] = agent.came_from[0] - agent.pos[0]
        portrayal['heading_y'] = agent.came_from[1] - agent.pos[1]

    return portrayal

grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)
server = ModularServer(
    NSModel,
    [generation, grid],
    'Natural Selection Model',
    {'num_agents': 10, 'width': 10, 'height': 10}
)
