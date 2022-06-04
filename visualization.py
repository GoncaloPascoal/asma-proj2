
import numpy as np
import json

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

class GenerationChartModule(VisualizationElement):
    package_includes = [CHART_JS_FILE]
    local_includes = ['GenerationChartModule.js']

    def __init__(
        self,
        series,
        canvas_height: int = 200,
        canvas_width: int = 500,
        data_collector_name: str = 'datacollector',
    ):
        self.series = series
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.data_collector_name = data_collector_name
        self.generation = None

        series_json = json.dumps(self.series)
        new_element = 'new GenerationChartModule({}, {},  {})'
        new_element = new_element.format(series_json, canvas_width, canvas_height)
        self.js_code = 'elements.push(' + new_element + ');'

    def render(self, model: Model):
        if self.generation == model.generation:
            return None
        else:
            self.generation = model.generation

        current_values = []
        data_collector = getattr(model, self.data_collector_name)

        for s in self.series:
            name = s['Label']
            try:
                val = data_collector.model_vars[name][-1]  # Latest value
            except (IndexError, KeyError):
                val = 0
            current_values.append(val)

        return current_values
