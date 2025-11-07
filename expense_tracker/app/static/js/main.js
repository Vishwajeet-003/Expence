// Load dashboard data when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
});

// Handle file upload form submission
document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData();
    const fileInput = document.getElementById('file');
    formData.append('file', fileInput.files[0]);
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            closeUploadModal();
            loadDashboard();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error uploading file');
    });
});

// Handle manual expense form submission
document.getElementById('manualForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const description = document.getElementById('description').value;
    const amount = parseFloat(document.getElementById('amount').value);
    
    fetch('/manual', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            description: description,
            amount: amount
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            closeManualModal();
            loadDashboard();
            document.getElementById('manualForm').reset();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error adding expense');
    });
});

// Load dashboard data
async function loadDashboard() {
    try {
        const [expensesResponse, summaryResponse] = await Promise.all([
            fetch('/api/expenses'),
            fetch('/api/summary')
        ]);
        
        const expenses = await expensesResponse.json();
        const summary = await summaryResponse.json();
        
        displaySummaryCards(summary);
        displayPieChart(summary);
        displayBarChart(summary);
        displayExpensesList(expenses);
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
        alert('Error loading dashboard data');
    }
}

// Display summary cards
function displaySummaryCards(summary) {
    const container = document.getElementById('summaryCards');
    container.innerHTML = '';
    
    const total = Object.values(summary).reduce((sum, val) => sum + val, 0);
    
    // Add total card
    container.innerHTML += `
        <div class="summary-card">
            <h3>Total Expenses</h3>
            <div class="amount">₹${total.toFixed(2)}</div>
        </div>
    `;
    
    // Add category cards
    Object.entries(summary).forEach(([category, amount]) => {
        container.innerHTML += `
            <div class="summary-card">
                <h3>${category}</h3>
                <div class="amount">₹${amount.toFixed(2)}</div>
            </div>
        `;
    });
}

// Display pie chart
function displayPieChart(summary) {
    const data = [{
        values: Object.values(summary),
        labels: Object.keys(summary),
        type: 'pie',
        hole: 0.4,
    }];
    
    const layout = {
        height: 400,
        showlegend: true,
    };
    
    Plotly.newPlot('pieChart', data, layout);
}

// Display bar chart
function displayBarChart(summary) {
    const data = [{
        x: Object.keys(summary),
        y: Object.values(summary),
        type: 'bar',
        marker: {
            color: '#3498db'
        }
    }];
    
    const layout = {
        height: 400,
        yaxis: {
            title: 'Amount (₹)'
        }
    };
    
    Plotly.newPlot('barChart', data, layout);
}

// Display expenses list
function displayExpensesList(expenses) {
    const tbody = document.getElementById('expensesBody');
    tbody.innerHTML = '';
    
    if (expenses.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="3" style="text-align: center;">No expenses yet</td>
            </tr>
        `;
        return;
    }
    
    expenses.forEach(expense => {
        tbody.innerHTML += `
            <tr>
                <td>${expense.description}</td>
                <td>₹${expense.amount.toFixed(2)}</td>
                <td>${expense.category}</td>
            </tr>
        `;
    });
}

// Clear all expenses
function clearExpenses() {
    if (confirm('Are you sure you want to clear all expenses?')) {
        fetch('/api/clear', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            loadDashboard();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error clearing expenses');
        });
    }
}

// Modal functions
function showUploadModal() {
    document.getElementById('uploadModal').style.display = 'block';
}

function closeUploadModal() {
    document.getElementById('uploadModal').style.display = 'none';
    document.getElementById('uploadForm').reset();
}

function showManualModal() {
    document.getElementById('manualModal').style.display = 'block';
}

function closeManualModal() {
    document.getElementById('manualModal').style.display = 'none';
    document.getElementById('manualForm').reset();
}

// Close modals when clicking outside
window.onclick = function(event) {
    const uploadModal = document.getElementById('uploadModal');
    const manualModal = document.getElementById('manualModal');
    
    if (event.target === uploadModal) {
        closeUploadModal();
    }
    if (event.target === manualModal) {
        closeManualModal();
    }
}