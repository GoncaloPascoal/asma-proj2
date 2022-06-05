
import numpy as np
from matplotlib.colors import to_hex
from typing import Dict, Any, Tuple

from mesa import Agent, Model
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

from visualization import GenerationChartModule, HistogramModule
from model import Food, Organism, NSModel, PheromoneTrail

def generation(model: Model) -> str:
    return f'Generation: {model.generation}'

def offset_to_coordinate(offset: Tuple[int, int]) -> str:
    coord = ''

    # North / South
    if offset[1] > 0:
        coord += 'n'
    elif offset[1] < 0:
        coord += 's'

    # East / West
    if offset[0] > 0:
        coord += 'e'
    elif offset[0] < 0:
        coord += 'w'

    return coord

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

        r = 0.45 if agent.prob_survival < 1 else 0.1
        g = 0.45 if agent.prob_survival == 1 and agent.prob_replication < 1 else 0.1
        b = 0.45 if agent.prob_replication == 1 else 0.1

        portrayal['Shape'] = 'rect'
        portrayal['Color'] = to_hex([
            r + r * speed_rate,
            g + g * speed_rate,
            b + b * speed_rate
        ])
        portrayal['w'] = w
        portrayal['h'] = h
        portrayal['xAlign'] = 0.9 - w / 2
        portrayal['yAlign'] = 0.9 - h / 2

        for attr in ['age', 'speed', 'awareness', 'size', 'energy', 'trail', 'prob_survival', 'prob_replication']:
            portrayal[attr] = agent.__dict__.get(attr)
    elif isinstance(agent, PheromoneTrail):
        offset = (agent.came_from[0] - agent.pos[0], agent.came_from[1] - agent.pos[1])
        portrayal['Shape'] = f'images/arrow_{offset_to_coordinate(offset)}.png'
        portrayal['scale'] = 0.2 + 0.4 * agent.strength / PheromoneTrail.MAX_STRENGTH

    return portrayal

def create_server(model_args: Dict[str, Any]) -> ModularServer:
    grid = CanvasGrid(agent_portrayal, model_args['width'], model_args['height'], 750, 750)

    # Charts
    num_organisms = GenerationChartModule(
        [{'Label': 'Organisms', 'Color': '#0000FF'}],
        data_collector_name='dc_num_organisms'
    )

    average_age = GenerationChartModule(
        [{'Label': 'Age', 'Color': '#EE2233'}],
        data_collector_name='dc_age'
    )
    hist_age = HistogramModule(
        bins=list(range(8)),
        attribute='age',
        color='#EE2233'
    )

    properties = GenerationChartModule(
        [
            {'Label': 'Speed', 'Color': '#00AADD'},
            {'Label': 'Awareness', 'Color': '#DDAA00'},
            {'Label': 'Size', 'Color': '#AA00DD'},
        ],
        data_collector_name='dc_properties'
    )
    trail_percentage = GenerationChartModule(
        [{'Label': 'Trail Percentage', 'Color': '#DD3300'}],
        data_collector_name='dc_trail_percentage'
    )

    hist_speed = HistogramModule(
        bins=list(range(Organism.MIN_SPEED, Organism.MAX_SPEED + 1)),
        attribute='speed',
        color='#00AADD'
    )
    hist_awareness = HistogramModule(
        bins=list(range(Organism.MIN_AWARENESS, Organism.MAX_AWARENESS + 1)),
        attribute='awareness',
        color='#DDAA00'
    )
    hist_size = HistogramModule(
        bins=list(np.arange(Organism.MIN_SIZE, Organism.MAX_SIZE + 0.125, 0.125)),
        attribute='size',
        color='#AA00DD'
    )

    elements = [generation, grid, num_organisms]
    if (
        model_args['speed_mutation_rate'] != 0 or
        model_args['awareness_mutation_rate'] != 0 or
        model_args['size_mutation_rate'] != 0
    ):
        elements.append(properties)

    if model_args['initial_trail'] != 0.0:
        elements.append(trail_percentage)

    if model_args['speed_mutation_rate'] != 0.0:
        elements.append(hist_speed)

    if model_args['awareness_mutation_rate'] != 0.0:
        elements.append(hist_awareness)

    if model_args['size_mutation_rate'] != 0.0:
        elements.append(hist_size)

    return ModularServer(
        NSModel,
        [
            generation, grid, num_organisms, average_age, hist_age, properties,
            trail_percentage, hist_speed, hist_awareness, hist_size
        ],
        'Natural Selection Model',
        model_args
    )
