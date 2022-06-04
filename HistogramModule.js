
const HistogramModule = function(bins, canvasWidth, canvasHeight, label, color) {
    const canvasTag = '<canvas width="' + canvasWidth + '" height="' +
        canvasHeight + '" style="border:1px dotted"></canvas>';

    const canvas = $(canvasTag)[0];
    $('#elements').append(canvas);

    const context = canvas.getContext('2d');

    const hexToRgb = function (hex, a = 1.0) {
        if (hex.indexOf('#') != 0) {
            return 'rgba(0,0,0,1.0)';
        }

        hex = hex.replace('#', '');
        const r = parseInt(hex.substring(0, 2), 16);
        const g = parseInt(hex.substring(2, 4), 16);
        const b = parseInt(hex.substring(4, 6), 16);

        return `rgba(${r},${g},${b},${a})`;
    };

    const datasets = [{
        label: label,
        backgroundColor: hexToRgb(color, 0.6),
        borderColor: 'rgba(20,20,20,0.8)',
        borderWidth: 2.0,
        hoverBackgroundColor: hexToRgb(color, 0.8),
        hoverBorderColor: 'rgba(20,20,20,1.0)',
        hoverBorderWidth: 2.0,
        data: []
    }];

    for (let _ in bins)
        datasets[0].data.push(0);
    
    const data = {
        labels: bins,
        datasets: datasets
    };

    const options = {
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