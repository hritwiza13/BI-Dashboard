// Global variable to store current data
let currentData = [];

// Fetch data from API
async function fetchData(startDate, endDate) {
    try {
        const response = await fetch(`/api/data?start_date=${startDate}&end_date=${endDate}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        // Ensure date column is Date objects for frontend processing
        data.forEach(row => {
            row.date = new Date(row.date);
        });
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
        alert('Error fetching data. Please try again.');
        return [];
    }
}

// Initialize date range
const today = new Date();
const thirtyDaysAgo = new Date(today);
thirtyDaysAgo.setDate(today.getDate() - 30);

const startDateInput = document.getElementById('start-date');
const endDateInput = document.getElementById('end-date');

startDateInput.value = thirtyDaysAgo.toISOString().split('T')[0];
endDateInput.value = today.toISOString().split('T')[0];

// Load initial data
fetchData(startDateInput.value, endDateInput.value).then(data => {
    currentData = data;
    updateDashboard(currentData);
});

// Event Listeners
document.getElementById('apply-filter').addEventListener('click', async () => {
    try {
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        currentData = await fetchData(startDate, endDate);
        updateDashboard(currentData);
    } catch (error) {
        console.error('Error applying filter:', error);
        alert('Error applying filter. Please try again.');
    }
});

document.getElementById('refresh-btn').addEventListener('click', async () => {
    try {
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        currentData = await fetchData(startDate, endDate);
        updateDashboard(currentData);
    } catch (error) {
        console.error('Error refreshing data:', error);
        alert('Error refreshing data. Please try again.');
    }
});

document.getElementById('export-btn').addEventListener('click', () => {
    try {
        if (currentData.length === 0) {
            alert('No data to export');
            return;
        }
        
        // Convert data to CSV
        const headers = ['Date', 'Sales', 'Customers', 'Conversion Rate'];
        const csvData = currentData.map(row => [
            row.date.toISOString().split('T')[0],
            row.sales,
            row.customers,
            (row.conversion_rate * 100).toFixed(1) + '%'
        ]);
        
        const csvContent = [
            headers.join(','),
            ...csvData.map(row => row.join(','))
        ].join('\n');
        
        // Create and download file
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `dashboard_export_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (error) {
        console.error('Error exporting data:', error);
        alert('Error exporting data. Please try again.');
    }
});

document.getElementById('table-search').addEventListener('input', (e) => {
    try {
        filterTable(e.target.value);
    } catch (error) {
        console.error('Error filtering table:', error);
    }
});

document.getElementById('table-filter').addEventListener('change', (e) => {
    try {
        filterTable(document.getElementById('table-search').value, e.target.value);
    } catch (error) {
        console.error('Error filtering table:', error);
    }
});

// Update dashboard with new data
function updateDashboard(data) {
    if (!Array.isArray(data) || data.length === 0) {
        console.warn("No data available for the selected date range.");
        updateKPIs([]);
        updateCharts([]);
        updateTable([]);
        return;
    }
    updateKPIs(data);
    updateCharts(data);
    updateTable(data);
}

// Update KPI cards
function updateKPIs(data) {
    if (!Array.isArray(data) || data.length === 0) {
        document.getElementById('total-sales').textContent = '$0.00';
        document.getElementById('total-customers').textContent = '0';
        document.getElementById('conversion-rate').textContent = '0%';
        document.getElementById('avg-order-value').textContent = '$0.00';
        updateTrend('total-sales', 0);
        updateTrend('total-customers', 0);
        updateTrend('conversion-rate', 0);
        updateTrend('avg-order-value', 0);
        return;
    }

    const totalSales = data.reduce((sum, row) => sum + row.sales, 0);
    const totalCustomers = data.reduce((sum, row) => sum + row.customers, 0);
    const avgConversionRate = data.reduce((sum, row) => sum + row.conversion_rate, 0) / data.length;
    const avgOrderValue = totalCustomers === 0 ? 0 : totalSales / totalCustomers;

    document.getElementById('total-sales').textContent = `$${totalSales.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    document.getElementById('total-customers').textContent = totalCustomers.toLocaleString();
    document.getElementById('conversion-rate').textContent = `${(avgConversionRate * 100).toFixed(1)}%`;
    document.getElementById('avg-order-value').textContent = `$${avgOrderValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

    // Calculate actual trends (comparing first and last values)
    const firstDay = data[0];
    const lastDay = data[data.length - 1];
    
    const salesTrend = ((lastDay.sales - firstDay.sales) / firstDay.sales) * 100;
    const customersTrend = ((lastDay.customers - firstDay.customers) / firstDay.customers) * 100;
    const conversionTrend = ((lastDay.conversion_rate - firstDay.conversion_rate) / firstDay.conversion_rate) * 100;
    const aovTrend = ((lastDay.sales/lastDay.customers - firstDay.sales/firstDay.customers) / (firstDay.sales/firstDay.customers)) * 100;

    updateTrend('total-sales', salesTrend);
    updateTrend('total-customers', customersTrend);
    updateTrend('conversion-rate', conversionTrend);
    updateTrend('avg-order-value', aovTrend);
}

function updateTrend(elementId, value) {
    const element = document.querySelector(`#${elementId}`).nextElementSibling;
    element.textContent = `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
    element.className = `kpi-trend ${value >= 0 ? 'positive' : 'negative'}`;
}

// Update charts
function updateCharts(data) {
    if (!Array.isArray(data) || data.length === 0) {
        // Clear charts if no data
        Plotly.newPlot('sales-chart', [], {});
        Plotly.newPlot('customers-chart', [], {});
        Plotly.newPlot('conversion-chart', [], {});
        return;
    }

    // Sales Trend Chart
    const salesTrace = {
        x: data.map(row => row.date),
        y: data.map(row => row.sales),
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Sales',
        line: { color: '#2563eb' }
    };

    Plotly.newPlot('sales-chart', [salesTrace], {
        margin: { t: 20, r: 20, b: 40, l: 40 },
        showlegend: false,
        xaxis: { title: 'Date' },
        yaxis: { title: 'Sales ($)' }
    });

    // Customer Acquisition Chart
    const customersTrace = {
        x: data.map(row => row.date),
        y: data.map(row => row.customers),
        type: 'bar',
        name: 'Customers',
        marker: { color: '#22c55e' }
    };

    Plotly.newPlot('customers-chart', [customersTrace], {
        margin: { t: 20, r: 20, b: 40, l: 40 },
        showlegend: false,
        xaxis: { title: 'Date' },
        yaxis: { title: 'Number of Customers' }
    });

    // Conversion Rate Chart
    const conversionTrace = {
        x: data.map(row => row.date),
        y: data.map(row => row.conversion_rate * 100),
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Conversion Rate',
        line: { color: '#f59e0b' }
    };

    Plotly.newPlot('conversion-chart', [conversionTrace], {
        margin: { t: 20, r: 20, b: 40, l: 40 },
        showlegend: false,
        xaxis: { title: 'Date' },
        yaxis: { title: 'Conversion Rate (%)' }
    });
}

// Update data table
function updateTable(data) {
    const tbody = document.querySelector('#data-table tbody');
    tbody.innerHTML = '';

    if (!Array.isArray(data) || data.length === 0) {
        return;
    }

    data.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row.date.toISOString().split('T')[0]}</td>
            <td>$${row.sales.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
            <td>${row.customers.toLocaleString()}</td>
            <td>${(row.conversion_rate * 100).toFixed(1)}%</td>
        `;
        tbody.appendChild(tr);
    });
}

// Filter table data
function filterTable(searchTerm, filterType = 'all') {
    const rows = document.querySelectorAll('#data-table tbody tr');
    const searchTermLower = searchTerm.toLowerCase();

    rows.forEach(row => {
        const date = row.cells[0].textContent;
        const sales = row.cells[1].textContent;
        const customers = row.cells[2].textContent;
        const conversion = row.cells[3].textContent;

        let showRow = true;

        // Apply search filter
        if (searchTerm) {
            showRow = date.includes(searchTermLower) ||
                     sales.toLowerCase().includes(searchTermLower) ||
                     customers.toLowerCase().includes(searchTermLower) ||
                     conversion.toLowerCase().includes(searchTermLower);
        }

        // Apply type filter
        if (showRow && filterType !== 'all') {
            switch (filterType) {
                case 'sales':
                    showRow = parseFloat(sales.replace(/[^0-9.-]+/g," ")) !== 0;
                    break;
                case 'customers':
                    showRow = parseInt(customers.replace(/[^0-9.-]+/g," ")) !== 0;
                    break;
            }
        }

        row.style.display = showRow ? '' : 'none';
    });
}

// Advanced filtering and drill-down
function setupAdvancedFilters() {
    const filterContainer = document.createElement('div');
    filterContainer.className = 'advanced-filters';
    filterContainer.innerHTML = `
        <div class="filter-group">
            <label>Sales Range:</label>
            <input type="number" id="min-sales" placeholder="Min">
            <input type="number" id="max-sales" placeholder="Max">
        </div>
        <div class="filter-group">
            <label>Customer Range:</label>
            <input type="number" id="min-customers" placeholder="Min">
            <input type="number" id="max-customers" placeholder="Max">
        </div>
        <button id="apply-advanced-filters" class="btn">Apply Filters</button>
    `;
    document.querySelector('.filters').appendChild(filterContainer);

    document.getElementById('apply-advanced-filters').addEventListener('click', applyAdvancedFilters);
}

function applyAdvancedFilters() {
    const minSales = document.getElementById('min-sales').value;
    const maxSales = document.getElementById('max-sales').value;
    const minCustomers = document.getElementById('min-customers').value;
    const maxCustomers = document.getElementById('max-customers').value;

    let filteredData = [...currentData];

    if (minSales) filteredData = filteredData.filter(row => row.sales >= minSales);
    if (maxSales) filteredData = filteredData.filter(row => row.sales <= maxSales);
    if (minCustomers) filteredData = filteredData.filter(row => row.customers >= minCustomers);
    if (maxCustomers) filteredData = filteredData.filter(row => row.customers <= maxCustomers);

    updateDashboard(filteredData);
}

// Date range presets
function setupDatePresets() {
    const presetContainer = document.createElement('div');
    presetContainer.className = 'date-presets';
    presetContainer.innerHTML = `
        <button class="preset-btn" data-days="7">Last 7 Days</button>
        <button class="preset-btn" data-days="30">Last 30 Days</button>
        <button class="preset-btn" data-days="90">Last 90 Days</button>
        <button class="preset-btn" data-days="365">Last Year</button>
    `;
    document.querySelector('.filters').appendChild(presetContainer);

    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const days = parseInt(btn.dataset.days);
            const endDate = new Date();
            const startDate = new Date();
            startDate.setDate(endDate.getDate() - days);
            
            startDateInput.value = startDate.toISOString().split('T')[0];
            endDateInput.value = endDate.toISOString().split('T')[0];
            
            fetchData(startDateInput.value, endDateInput.value).then(data => {
                currentData = data;
                updateDashboard(currentData);
            });
        });
    });
}

// Enhanced chart types
function createPieChart(data) {
    const salesByDay = data.reduce((acc, row) => {
        const day = row.date.toLocaleDateString('en-US', { weekday: 'long' });
        acc[day] = (acc[day] || 0) + row.sales;
        return acc;
    }, {});

    const pieTrace = {
        values: Object.values(salesByDay),
        labels: Object.keys(salesByDay),
        type: 'pie',
        name: 'Sales by Day'
    };

    Plotly.newPlot('sales-pie-chart', [pieTrace], {
        margin: { t: 20, r: 20, b: 40, l: 40 },
        title: 'Sales Distribution by Day'
    });
}

// Enhanced data export
function exportData(format) {
    if (currentData.length === 0) {
        alert('No data to export');
        return;
    }

    switch (format) {
        case 'csv':
            exportToCSV();
            break;
        case 'json':
            exportToJSON();
            break;
        case 'excel':
            exportToExcel();
            break;
    }
}

function exportToJSON() {
    const jsonData = JSON.stringify(currentData, null, 2);
    const blob = new Blob([jsonData], { type: 'application/json' });
    downloadFile(blob, 'dashboard_export.json');
}

function exportToExcel() {
    // Convert to CSV first (Excel can open CSV files)
    const headers = ['Date', 'Sales', 'Customers', 'Conversion Rate'];
    const csvData = currentData.map(row => [
        row.date.toISOString().split('T')[0],
        row.sales,
        row.customers,
        (row.conversion_rate * 100).toFixed(1) + '%'
    ]);
    
    const csvContent = [
        headers.join(','),
        ...csvData.map(row => row.join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    downloadFile(blob, 'dashboard_export.xlsx');
}

function downloadFile(blob, filename) {
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Initialize new features
document.addEventListener('DOMContentLoaded', () => {
    setupAdvancedFilters();
    setupDatePresets();
    
    // Add export format buttons
    const exportContainer = document.createElement('div');
    exportContainer.className = 'export-options';
    exportContainer.innerHTML = `
        <button onclick="exportData('csv')" class="btn">Export CSV</button>
        <button onclick="exportData('json')" class="btn">Export JSON</button>
        <button onclick="exportData('excel')" class="btn">Export Excel</button>
    `;
    document.querySelector('.actions').appendChild(exportContainer);
}); 