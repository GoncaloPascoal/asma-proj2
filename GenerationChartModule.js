
const GenerationChartModule = function(series, canvas_width, canvas_height) {
    const canvas = document.createElement('canvas');
    Object.assign(canvas, {
        width: canvas_width,
        height: canvas_height,
        style: 'border:1px dotted',
    });

    document.getElementById('elements').appendChild(canvas);

    const context = canvas.getContext("2d");

    const convertColorOpacity = (hex) => {
        if (hex.indexOf('#') != 0) {
            return 'rgba(0,0,0,0.1)';
        }
  
        hex = hex.replace('#', '');
        const r = parseInt(hex.substring(0, 2), 16);
        const g = parseInt(hex.substring(2, 4), 16);
        const b = parseInt(hex.substring(4, 6), 16);
        
        return `rgba(${r},${g},${b},0.1)`;
    };

    // Prep the chart properties and series:
    const datasets = [];
    for (const i in series) {
        const s = series[i];
        const newSeries = {
            label: s.Label,
            borderColor: s.Color,
            backgroundColor: convertColorOpacity(s.Color),
            data: [],
        };
        datasets.push(newSeries);
    }
  
    const chartData = {
        labels: [],
        datasets: datasets,
    };
  
    const chartOptions = {
        responsive: true,
        tooltips: {
            mode: 'index',
            intersect: false,
        },
        hover: {
            mode: 'nearest',
            intersect: true,
        },
        scales: {
            x: {
                display: true,
                title: {
                    display: true,
                },
                ticks: {
                    maxTicksLimit: 11,
                },
            },
            y: {
                display: true,
                title: {
                    display: true,
                },
            },
        },
    };
  
    const chart = new Chart(context, {
        type: 'line',
        data: chartData,
        options: chartOptions,
    });

    let generation = 1;

    this.render = function(data) {
        if (data != null) {
            chart.data.labels.push(generation++);
            for (let i = 0; i < data.length; i++) {
                chart.data.datasets[i].data.push(data[i]);
            }
            chart.update();
        }
    };
  
    this.reset = function() {
        while (chart.data.labels.length) {
            chart.data.labels.pop();
        }
        chart.data.datasets.forEach((dataset) => {
            while (dataset.data.length) {
                dataset.data.pop();
            }
        });
        chart.update();
    };
};
