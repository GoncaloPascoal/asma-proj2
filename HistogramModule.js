
const HistogramModule = function(bins, canvasWidth, canvasHeight, label) {
    let canvasTag = '<canvas width="' + canvasWidth + '" height="' +
        canvasHeight + '" style="border:1px dotted"></canvas>';

    let canvas = $(canvasTag)[0];
    $('#elements').append(canvas);

    let context = canvas.getContext('2d');

    let datasets = [{
        label: label,
        fillColor: 'rgba(151,187,205,0.5)',
        strokeColor: 'rgba(151,187,205,0.8)',
        highlightFill: 'rgba(151,187,205,0.75)',
        highlightStroke: 'rgba(151,187,205,1)',
        data: []
    }];

    for (let _ in bins)
        datasets[0].data.push(0);
    
    let data = {
        labels: bins,
        datasets: datasets
    };

    let options = {
        scaleBeginsAtZero: true
    };

    let chart = new Chart(context, {type: 'bar', data: data, options: options});

    this.render = function(data) {
        datasets[0].data = data;
        chart.update();
    };

    this.reset = function() {
        chart.destroy();
        chart = new Chart(context, {type: 'bar', data: data, options: options});
    };
}