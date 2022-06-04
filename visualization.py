
import numpy as np

from mesa.visualization.ModularVisualization import VisualizationElement, CHART_JS_FILE
from mesa import Model

from model import Organism

class HistogramModule(VisualizationElement):
    package_includes = [CHART_JS_FILE]
    local_includes = ['HistogramModule.js']

    def __init__(self, bins, canvas_width: int, canvas_height: int, attribute: str):
        self.bins = bins
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.attribute = attribute

        new_element = 'new HistogramModule({}, {}, {}, {})'.format(
            bins, canvas_width, canvas_height, repr(attribute)
        )

        self.js_code = 'elements.push(' + new_element + ');'
    
    def render(self, model: Model):
        values = [
            agent.__getattribute__(self.attribute)
            for agent in model.schedule.agents
            if isinstance(agent, Organism)
        ]
        hist = np.histogram(values, bins=self.bins)[0]
        return [int(x) for x in hist]
