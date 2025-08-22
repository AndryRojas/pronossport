/**
 * Pronossport Dashboard - JavaScript Functions
 * Funcionalidades principales para la interfaz web
 */

// Variables globales
let currentView = 'cards';
let refreshInterval = null;

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupEventListeners();
    showLoadingComplete();
});

/**
 * Inicialización principal del dashboard
 */
function initializeDashboard() {
    console.log('🚀 Iniciando Pronossport Dashboard');
    
    // Configurar tooltips de Bootstrap
    enableTooltips();
    
    // Configurar auto-refresh si está en la página principal
    if (window.location.pathname === '/') {
        setupAutoRefresh();
    }
    
    // Agregar animaciones de entrada
    addFadeInAnimations();
}

/**
 * Configurar event listeners
 */
function setupEventListeners() {
    // Búsqueda en tiempo real en tablas
    setupTableSearch();
    
    // Filtros dinámicos
    setupDynamicFilters();
    
    // Manejo de errores de imágenes
    setupImageErrorHandling();
    
    // Teclas de acceso rápido
    setupKeyboardShortcuts();
}

/**
 * Habilitar tooltips de Bootstrap
 */
function enableTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Configurar auto-refresh para el dashboard principal
 */
function setupAutoRefresh() {
    const refreshButton = document.querySelector('[onclick="refreshData()"]');
    if (refreshButton) {
        // Auto-refresh cada 5 minutos
        refreshInterval = setInterval(refreshData, 300000);
        console.log('✅ Auto-refresh configurado (5 minutos)');
    }
}

/**
 * Agregar animaciones de entrada
 */
function addFadeInAnimations() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

/**
 * Configurar búsqueda en tablas
 */
function setupTableSearch() {
    const searchInputs = document.querySelectorAll('[data-table-search]');
    
    searchInputs.forEach(input => {
        const tableId = input.getAttribute('data-table-search');
        const table = document.getElementById(tableId);
        
        if (table) {
            input.addEventListener('input', function() {
                filterTable(table, this.value);
            });
        }
    });
}

/**
 * Filtrar tabla por texto
 */
function filterTable(table, searchText) {
    const rows = table.querySelectorAll('tbody tr');
    const search = searchText.toLowerCase();
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const visible = text.includes(search);
        row.style.display = visible ? '' : 'none';
    });
    
    // Mostrar mensaje si no hay resultados
    const visibleRows = table.querySelectorAll('tbody tr[style=""]').length;
    showNoResultsMessage(table, visibleRows === 0 && searchText !== '');
}

/**
 * Mostrar mensaje de "sin resultados"
 */
function showNoResultsMessage(table, show) {
    let noResultsRow = table.querySelector('.no-results-row');
    
    if (show && !noResultsRow) {
        const tbody = table.querySelector('tbody');
        const colCount = table.querySelectorAll('thead th').length;
        
        noResultsRow = document.createElement('tr');
        noResultsRow.className = 'no-results-row';
        noResultsRow.innerHTML = `
            <td colspan="${colCount}" class="text-center text-muted py-4">
                <i class="bi bi-search"></i>
                <div class="mt-2">No se encontraron resultados</div>
            </td>
        `;
        
        tbody.appendChild(noResultsRow);
    } else if (!show && noResultsRow) {
        noResultsRow.remove();
    }
}

/**
 * Configurar filtros dinámicos
 */
function setupDynamicFilters() {
    const filterSelects = document.querySelectorAll('[data-dynamic-filter]');
    
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            const form = this.closest('form');
            if (form) {
                // Auto-submit form when filter changes
                setTimeout(() => form.submit(), 100);
            }
        });
    });
}

/**
 * Manejo de errores de imágenes
 */
function setupImageErrorHandling() {
    const images = document.querySelectorAll('img');
    
    images.forEach(img => {
        img.addEventListener('error', function() {
            if (this.classList.contains('team-logo') || this.classList.contains('league-logo')) {
                this.src = '/static/images/default-logo.png';
                this.alt = 'Logo no disponible';
            } else if (this.classList.contains('player-photo')) {
                this.src = '/static/images/default-player.png';
                this.alt = 'Foto no disponible';
            } else if (this.classList.contains('flag-icon')) {
                this.src = '/static/images/default-flag.png';
                this.alt = 'Bandera no disponible';
            }
        });
    });
}

/**
 * Configurar teclas de acceso rápido
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + R para refrescar datos
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            refreshData();
        }
        
        // Escape para limpiar filtros
        if (e.key === 'Escape') {
            clearFilters();
        }
        
        // Ctrl/Cmd + F para enfocar búsqueda
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            const searchInput = document.querySelector('input[type="search"], input[data-table-search]');
            if (searchInput) {
                e.preventDefault();
                searchInput.focus();
            }
        }
    });
}

/**
 * Refrescar datos del dashboard
 */
function refreshData() {
    console.log('🔄 Refrescando datos...');
    
    const refreshBtn = document.querySelector('[onclick="refreshData()"]');
    if (refreshBtn) {
        const originalText = refreshBtn.innerHTML;
        refreshBtn.innerHTML = '<span class="loading-spinner"></span> Actualizando...';
        refreshBtn.disabled = true;
        
        // Simular refresco (en una implementación real, aquí harías llamadas AJAX)
        setTimeout(() => {
            location.reload();
        }, 1000);
    }
}

/**
 * Exportar datos (placeholder)
 */
function exportData() {
    console.log('📊 Exportando datos...');
    
    // Aquí implementarías la funcionalidad de exportación
    const currentPage = window.location.pathname;
    let exportType = 'general';
    
    if (currentPage.includes('/leagues')) exportType = 'leagues';
    else if (currentPage.includes('/teams')) exportType = 'teams';
    else if (currentPage.includes('/players')) exportType = 'players';
    else if (currentPage.includes('/matches')) exportType = 'matches';
    
    showToast(`Exportando datos de ${exportType}...`, 'info');
    
    // Implementación futura: generar CSV/Excel
    setTimeout(() => {
        showToast('Función de exportación en desarrollo', 'warning');
    }, 1500);
}

/**
 * Limpiar filtros
 */
function clearFilters() {
    const form = document.querySelector('form');
    if (form) {
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            if (input.type === 'text' || input.type === 'date') {
                input.value = '';
            } else if (input.tagName === 'SELECT') {
                input.selectedIndex = 0;
            }
        });
        
        showToast('Filtros limpiados', 'success');
    }
}

/**
 * Alternar vista entre tabla y tarjetas
 */
function toggleView(viewType) {
    const tableView = document.getElementById('tableView');
    const cardsView = document.getElementById('cardsView');
    const buttons = document.querySelectorAll('[onclick^="toggleView"]');
    
    if (!tableView || !cardsView) return;
    
    // Remover clase active de todos los botones
    buttons.forEach(btn => btn.classList.remove('active'));
    
    // Aplicar transición suave
    if (viewType === 'table') {
        cardsView.style.opacity = '0';
        setTimeout(() => {
            tableView.style.display = 'block';
            cardsView.style.display = 'none';
            tableView.style.opacity = '1';
        }, 150);
        document.querySelector('[onclick="toggleView(\'table\')"]')?.classList.add('active');
    } else {
        tableView.style.opacity = '0';
        setTimeout(() => {
            cardsView.style.display = 'block';
            tableView.style.display = 'none';
            cardsView.style.opacity = '1';
        }, 150);
        document.querySelector('[onclick="toggleView(\'cards\')"]')?.classList.add('active');
    }
    
    currentView = viewType;
    localStorage.setItem('preferredView', viewType);
}

/**
 * Mostrar toast notification
 */
function showToast(message, type = 'info') {
    // Crear toast container si no existe
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1055';
        document.body.appendChild(toastContainer);
    }
    
    // Crear toast
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'warning' ? 'warning' : type === 'error' ? 'danger' : 'info'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : type === 'error' ? 'x-circle' : 'info-circle'}"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Mostrar toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Limpiar después de que se oculte
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

/**
 * Mostrar indicador de carga completada
 */
function showLoadingComplete() {
    const loadingIndicator = document.querySelector('.loading-spinner');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
    }
    
    // Agregar indicador de online
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        const onlineIndicator = document.createElement('div');
        onlineIndicator.className = 'online-indicator';
        onlineIndicator.title = 'Conectado';
        navbar.appendChild(onlineIndicator);
    }
}

/**
 * Formatear números con separadores de miles
 */
function formatNumber(num) {
    return new Intl.NumberFormat('es-ES').format(num);
}

/**
 * Formatear fechas de forma legible
 */
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('es-ES', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        }).format(date);
    } catch {
        return dateString;
    }
}

/**
 * Formatear fechas con hora
 */
function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('es-ES', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    } catch {
        return dateString;
    }
}

/**
 * Debounce function para optimizar búsquedas
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Cargar datos via AJAX (para futuras implementaciones)
 */
async function loadData(endpoint, params = {}) {
    try {
        const url = new URL(endpoint, window.location.origin);
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error loading data:', error);
        showToast('Error cargando datos', 'error');
        return null;
    }
}

/**
 * Cleanup al cerrar la página
 */
window.addEventListener('beforeunload', function() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});

// Funciones globales para uso en templates
window.refreshData = refreshData;
window.exportData = exportData;
window.toggleView = toggleView;
window.showToast = showToast;

console.log('✅ Dashboard JavaScript cargado correctamente');