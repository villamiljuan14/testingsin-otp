/**
 * ── Helper Functions ── 
 */

const formatCOP = (value) => 
    new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(value);

function renderKPI(value, element) {
    if (!element) return;
    const val = parseFloat(value);
    const isEmpty = isNaN(val) || val === 0;
    element.textContent = isEmpty ? '—' : value;
    element.dataset.empty = isEmpty;
}

/**
 * Update interactive components based on theme
 * @param {string} theme - 'dark' or 'light'
 */
function updateDashboardInteractiveTheme(theme) {
    const bentoAxisColor = '#94a3b8';
    
    // Update ApexChart
    if (deliveryChart) {
        deliveryChart.updateOptions({
            chart: { foreColor: bentoAxisColor },
            xaxis: { labels: { style: { colors: bentoAxisColor } } },
            yaxis: { labels: { style: { colors: bentoAxisColor } } },
            grid: { borderColor: 'rgba(148, 163, 184, 0.1)' },
            tooltip: { theme: theme }
        });
    }

    // Update Leaflet Map
    if (trackingMap) {
        const isDark = theme === 'dark';
        const TILES = {
            light: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
            dark:  'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png'
        };
        
        trackingMap.eachLayer((layer) => {
            if (layer instanceof L.TileLayer) {
                trackingMap.removeLayer(layer);
            }
        });

        L.tileLayer(TILES[isDark ? 'dark' : 'light'], {
            attribution: '&copy; OpenStreetMap &copy; CARTO'
        }).addTo(trackingMap);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // ── 1. Theme Synchronization ──
    document.addEventListener('themeChanged', (e) => {
        updateDashboardInteractiveTheme(e.detail.theme);
    });

    const currentTheme = document.documentElement.getAttribute('data-theme') || 
                         (document.documentElement.classList.contains('dark') ? 'dark' : 'light');

    // ── 2. Format Initial Data ──
    document.querySelectorAll('.currency-format').forEach(el => {
        const val = el.dataset.value || el.textContent.replace('$', '').replace(/,/g, '');
        el.textContent = formatCOP(parseFloat(val));
    });

    renderKPI(document.getElementById('kpi-total-pedidos')?.textContent, document.getElementById('kpi-total-pedidos'));
    renderKPI(document.getElementById('kpi-en-transito')?.textContent, document.getElementById('kpi-en-transito'));
    renderKPI(document.getElementById('kpi-entregados')?.textContent, document.getElementById('kpi-entregados'));

    // ── 3. Delivery Chart ──
    const chartElement = document.querySelector("#deliveryChart");
    if (chartElement && typeof ApexCharts !== 'undefined') {
        const bentoAxisColor = '#94a3b8'; // Strict Bento v2 standard
        
        const chartOptions = {
            series: [{
                name: 'Envíos',
                data: [31, 40, 28, 51, 42, 109, 100, 120, 140, 110, 90, 100]
            }, {
                name: 'Entregas',
                data: [11, 32, 45, 32, 34, 52, 41, 60, 80, 70, 60, 80]
            }],
            chart: {
                height: 220, // Adjusted for zero-scroll
                type: 'area',
                toolbar: { show: false },
                background: 'transparent',
                foreColor: bentoAxisColor,
            },
            colors: ['#0066FF', '#A855F7'], // Precise mockup colors
            dataLabels: { enabled: false },
            stroke: { 
                curve: 'smooth', 
                width: 4, 
                lineCap: 'round'
            },
            fill: {
                type: 'gradient',
                gradient: {
                    shadeIntensity: 1,
                    opacityFrom: 0.3,
                    opacityTo: 0.02,
                    stops: [0, 90, 100]
                }
            },
            xaxis: {
                categories: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                labels: { style: { colors: bentoAxisColor, fontSize: '11px' } },
                axisBorder: { show: false },
                axisTicks: { show: false }
            },
            yaxis: {
                labels: { style: { colors: bentoAxisColor, fontSize: '11px' } }
            },
            grid: {
                borderColor: 'rgba(148, 163, 184, 0.1)',
                strokeDashArray: 4,
            },
            tooltip: { theme: currentTheme }
        };
        deliveryChart = new ApexCharts(chartElement, chartOptions);
        deliveryChart.render();
    }

    // ── 4. Tracking Map ──
    const mapElement = document.getElementById('trackingMap');
    if (mapElement && typeof L !== 'undefined') {
        const isDark = currentTheme === 'dark';
        trackingMap = L.map('trackingMap').setView([4.6097, -74.0817], 13); // Bogotá
        
        const TILES = {
            light: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
            dark:  'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png'
        };

        L.tileLayer(TILES[isDark ? 'dark' : 'light'], {
            attribution: '&copy; OpenStreetMap &copy; CARTO'
        }).addTo(trackingMap);

        // Parsear los datos de pedidos enviados desde Django
        let pedidosMapa = [];
        const dataElement = document.getElementById('pedidos-mapa-data');
        if (dataElement) {
            try {
                pedidosMapa = JSON.parse(dataElement.textContent);
            } catch (e) {
                console.error("Error al leer datos del mapa", e);
            }
        }

        if (pedidosMapa.length > 0) {
            // Group and bound the markers properly
            const bounds = [];
            const seenCoords = new Set();
            
            pedidosMapa.forEach(p => {
                if(p.lat && p.lng) {
                    let finalLat = p.lat;
                    let finalLng = p.lng;
                    
                    // Si ya existe un marcador en esta coordenada exacta, añadir pequeña dispersión aleatoria
                    const coordKey = `${finalLat},${finalLng}`;
                    if (seenCoords.has(coordKey)) {
                        finalLat += (Math.random() - 0.5) * 0.006;
                        finalLng += (Math.random() - 0.5) * 0.006;
                    }
                    seenCoords.add(coordKey);
                    
                    bounds.push([finalLat, finalLng]);
                    // Se usa el marcador por defecto
                    L.marker([finalLat, finalLng]).addTo(trackingMap)
                        .bindPopup(`<b>Pedido ${p.id}</b><br>Destinatario: ${p.cliente}<br>Estado: ${p.estado}`);
                }
            });
            // Update view to bound all elements if possible
            if(bounds.length > 0) {
                trackingMap.fitBounds(bounds, { maxZoom: 14, padding: [30, 30] });
            }
        } else {
            // Default Demo Marker (if no data)
            L.marker([4.65, -74.1]).addTo(trackingMap)
                .bindPopup('<b>Buscando operaciones...</b><br>Esperando asignación logística.');
        }
    }
});
