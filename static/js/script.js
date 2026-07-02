/* Enviart Interactive Logic - Modular Version */

let landChart;
let landMap;

/**
 * Update interactive components based on theme
 * @param {string} theme - 'dark' or 'light'
 */
function updateInteractiveTheme(theme) {
    const isDark = theme === 'dark';
    
    // 1. ApexCharts Update
    if (landChart) {
        landChart.updateOptions({
            theme: { mode: isDark ? 'dark' : 'light' },
            xaxis: {
                labels: { style: { colors: isDark ? '#9ca3af' : '#6b7280' } }
            },
            yaxis: {
                labels: { style: { colors: isDark ? '#9ca3af' : '#6b7280' } }
            },
            grid: { borderColor: isDark ? '#1f2133' : '#e5e7eb' },
            legend: { labels: { colors: isDark ? '#9ca3af' : '#6b7280' } }
        });
    }

    // 2. Leaflet Map Update
    if (landMap) {
        const tileUrl = isDark 
            ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
            : 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';
        
        landMap.eachLayer((layer) => {
            if (layer instanceof L.TileLayer) {
                landMap.removeLayer(layer);
            }
        });

        L.tileLayer(tileUrl, {
            attribution: '&copy; OpenStreetMap &copy; CARTO'
        }).addTo(landMap);
    }
}

document.addEventListener('DOMContentLoaded', function () {
    // 🔹 1. Theme Synchronization
    // Listen for global theme changes from theme.js
    document.addEventListener('themeChanged', (e) => {
        updateInteractiveTheme(e.detail.theme);
    });

    // Initial sync
    const currentTheme = document.documentElement.getAttribute('data-theme') || 
                         (document.documentElement.classList.contains('dark') ? 'dark' : 'light');
    
    // 🔹 2. Carousel Logic
    const slides = document.querySelectorAll('.carousel-slide');
    const dots = document.querySelectorAll('.hero-dot');
    const nextBtn = document.getElementById('next');
    const prevBtn = document.getElementById('prev');
    let currentSlide = 0;

    function showSlide(n) {
        if (!slides.length) return;
        slides[currentSlide].classList.remove('active');
        if (dots.length > 0) {
            dots[currentSlide].classList.remove('active');
            dots[currentSlide].setAttribute('aria-selected', 'false');
        }

        currentSlide = (n + slides.length) % slides.length;

        slides[currentSlide].classList.add('active');
        if (dots.length > 0) {
            dots[currentSlide].classList.add('active');
            dots[currentSlide].setAttribute('aria-selected', 'true');
        }
    }

    if (nextBtn && prevBtn) {
        nextBtn.addEventListener('click', () => showSlide(currentSlide + 1));
        prevBtn.addEventListener('click', () => showSlide(currentSlide - 1));

        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => showSlide(index));
        });

        let autoPlay = setInterval(() => showSlide(currentSlide + 1), 6000);
        const pauseAutoPlay = () => clearInterval(autoPlay);
        
        [nextBtn, prevBtn, ...dots].forEach(el => {
            if (el) el.addEventListener('mousedown', pauseAutoPlay);
        });
    }

    // 🔹 3. ApexCharts Initialization
    const chartElement = document.querySelector("#estadisticas-chart");
    if (chartElement && typeof ApexCharts !== 'undefined') {
        const isDark = currentTheme === 'dark';
        const brandColor = getComputedStyle(document.documentElement).getPropertyValue('--color-brand').trim() || '#3C50E0';

        const options = {
            series: [{
                name: 'Envíos',
                data: [31, 40, 28, 51, 42, 109, 100, 120, 80, 95, 110, 130]
            }, {
                name: 'Entregas',
                data: [11, 32, 45, 32, 34, 52, 41, 80, 60, 70, 85, 95]
            }],
            chart: {
                type: 'area',
                height: 350,
                toolbar: { show: false },
                background: 'transparent'
            },
            theme: { mode: isDark ? 'dark' : 'light' },
            colors: [brandColor, '#80CAEE'],
            fill: {
                type: 'gradient',
                gradient: { shadeIntensity: 1, opacityFrom: 0.7, opacityTo: 0.3 }
            },
            dataLabels: { enabled: false },
            stroke: { curve: 'smooth' },
            xaxis: {
                categories: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
                labels: { style: { colors: isDark ? '#9ca3af' : '#6b7280' } }
            },
            yaxis: { labels: { style: { colors: isDark ? '#9ca3af' : '#6b7280' } } },
            grid: { borderColor: isDark ? '#1f2133' : '#e5e7eb', strokeDashArray: 4 },
            legend: { labels: { colors: isDark ? '#9ca3af' : '#6b7280' } }
        };

        landChart = new ApexCharts(chartElement, options);
        landChart.render();
    }

    // 🔹 4. Leaflet Map Initialization
    const mapContainer = document.getElementById('mapaBogota');
    if (mapContainer && typeof L !== 'undefined') {
        const latBogota = 4.6548;
        const lngBogota = -74.0655;
        const isDark = currentTheme === 'dark';
        const brandColor = getComputedStyle(document.documentElement).getPropertyValue('--color-brand').trim() || '#3C50E0';

        const tileUrl = isDark 
            ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
            : 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';

        landMap = L.map('mapaBogota', {
            zoomControl: false
        }).setView([latBogota, lngBogota], 12);

        L.tileLayer(tileUrl, {
            attribution: '&copy; OpenStreetMap &copy; CARTO'
        }).addTo(landMap);

        const customIcon = L.divIcon({
            className: 'custom-marker',
            html: `<div style="background-color: ${brandColor}; width: 15px; height: 15px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 10px ${brandColor};"></div>`,
            iconSize: [15, 15]
        });

        L.marker([latBogota, lngBogota], { icon: customIcon }).addTo(landMap)
            .bindPopup('<b>Centro de Operaciones Enviart</b><br>Bogotá, Colombia');

        window.addEventListener('resize', () => landMap.invalidateSize());
    }
});
