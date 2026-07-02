import ApexCharts from 'apexcharts';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const themeToggleBtn = document.getElementById('theme-toggle');
const darkIcon = document.getElementById('theme-toggle-dark-icon');
const lightIcon = document.getElementById('theme-toggle-light-icon');

if (localStorage.getItem('color-theme') === 'dark' || (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark');
    if (lightIcon) lightIcon.classList.remove('hidden');
    if (darkIcon) darkIcon.classList.add('hidden');
} else {
    document.documentElement.classList.remove('dark');
    if (darkIcon) darkIcon.classList.remove('hidden');
    if (lightIcon) lightIcon.classList.add('hidden');
}

if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', function () {
        if (darkIcon) darkIcon.classList.toggle('hidden');
        if (lightIcon) lightIcon.classList.toggle('hidden');

        if (localStorage.getItem('color-theme')) {
            if (localStorage.getItem('color-theme') === 'light') {
                document.documentElement.classList.add('dark');
                localStorage.setItem('color-theme', 'dark');
            } else {
                document.documentElement.classList.remove('dark');
                localStorage.setItem('color-theme', 'light');
            }
        } else {
            if (document.documentElement.classList.contains('dark')) {
                document.documentElement.classList.remove('dark');
                localStorage.setItem('color-theme', 'light');
            } else {
                document.documentElement.classList.add('dark');
                localStorage.setItem('color-theme', 'dark');
            }
        }
        updateChartTheme();
    });
}

const options = {
    series: [{
        name: 'Envíos',
        data: (typeof chartDataEnvios !== 'undefined') ? chartDataEnvios : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    }, {
        name: 'Entregas',
        data: (typeof chartDataEntregas !== 'undefined') ? chartDataEntregas : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    }],
    chart: {
        type: 'bar',
        height: 320,
        toolbar: { show: false },
        fontFamily: 'Outfit, sans-serif',
        background: 'transparent'
    },
    colors: ['#3C50E0', '#80CAEE'],
    plotOptions: {
        bar: {
            horizontal: false,
            columnWidth: '55%',
            endingShape: 'rounded',
            borderRadius: 4
        },
    },
    dataLabels: { enabled: false },
    stroke: {
        show: true,
        width: 2,
        colors: ['transparent']
    },
    xaxis: {
        categories: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
        axisBorder: { show: false },
        axisTicks: { show: false },
        labels: { style: { colors: '#64748B' } }
    },
    yaxis: { labels: { style: { colors: '#64748B' } } },
    fill: { opacity: 1 },
    tooltip: {
        y: { formatter: function (val) { return val + " envíos" } },
        theme: 'dark'
    },
    grid: {
        borderColor: '#e2e8f0',
        strokeDashArray: 4,
        yaxis: { lines: { show: true } }
    },
    legend: {
        position: 'top',
        horizontalAlign: 'left',
        labels: { colors: '#64748B' }
    }
};

let chart;

const updateChartTheme = () => {
    const isDarkMode = document.documentElement.classList.contains('dark');
    const darkColors = { grid: '#374151', labels: '#9CA3AF' };
    const lightColors = { grid: '#e2e8f0', labels: '#64748B' };
    const themeColors = isDarkMode ? darkColors : lightColors;

    options.grid.borderColor = themeColors.grid;
    options.xaxis.labels.style.colors = themeColors.labels;
    options.yaxis.labels.style.colors = themeColors.labels;
    options.legend.labels.colors = themeColors.labels;

    if (chart) {
        chart.updateOptions(options);
    }
};

const chartElement = document.querySelector("#estadisticas-chart");

if (chartElement) {
    updateChartTheme();
    chart = new ApexCharts(chartElement, options);
    chart.render();
}

const latBogota = 4.7110;
const lngBogota = -74.0721;
const zoomLevel = 12;

const mapContainer = document.getElementById('mapaBogota');
if (mapContainer) {
    const mapa = L.map('mapaBogota').setView([latBogota, lngBogota], zoomLevel);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(mapa);

    L.marker([latBogota, lngBogota]).addTo(mapa)
        .bindPopup('Centro de Operaciones')
        .openPopup();

    setTimeout(() => {
        mapa.invalidateSize();
    }, 100);
}