// Add event listeners for all license edit panel buttons
document.addEventListener('DOMContentLoaded', function() {
    const licenseEditPanelButtons = document.querySelectorAll('.license-edit-panel-button');
    licenseEditPanelButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const licenseId = this.dataset.licenseId;
            toggleLicenseEditPanel(licenseId);
        });
    });

    // Handle form submission
    const form = document.getElementById('license-edit-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            submitLicenseForm();
        });
    }

    // Initialize filtering (with a small delay to ensure licenses data is available)
    setTimeout(initializeLicenseFilters, 100);
});

// Initialize license filtering functionality
function initializeLicenseFilters() {
    // Only initialize if we're on the license list page
    const searchInput = document.getElementById('license-search');
    const statusFilter = document.getElementById('status-filter');
    const expirationFilter = document.getElementById('expiration-filter');
    const clearFiltersBtn = document.getElementById('clear-filters');
    const clearFiltersInlineBtn = document.getElementById('clear-filters-inline');

    if (!searchInput || !statusFilter || !expirationFilter) {
        return; // Not on license list page
    }

    // Wait for licenses data to be available (it's defined in inline script)
    if (typeof licenses === 'undefined') {
        // Retry after a short delay if licenses isn't available yet
        setTimeout(initializeLicenseFilters, 100);
        return;
    }

    // Set expiration data attributes on rows based on license data
    setExpirationDataAttributes();

    // Add event listeners
    searchInput.addEventListener('input', filterLicenses);
    statusFilter.addEventListener('change', filterLicenses);
    expirationFilter.addEventListener('change', filterLicenses);
    
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', clearFilters);
    }
    if (clearFiltersInlineBtn) {
        clearFiltersInlineBtn.addEventListener('click', clearFilters);
    }
}

// Set expiration data attributes on table rows
function setExpirationDataAttributes() {
    const now = new Date();
    const thirtyDaysFromNow = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);
    
    const rows = document.querySelectorAll('.license-row');
    rows.forEach(row => {
        const licenseId = parseInt(row.dataset.licenseId);
        const license = licenses.find(l => l.id === licenseId);
        
        if (!license) return;
        
        let expirationStatus = 'never';
        if (license.expires_at) {
            const expiresAt = new Date(license.expires_at);
            if (expiresAt < now) {
                expirationStatus = 'expired';
            } else if (expiresAt <= thirtyDaysFromNow) {
                expirationStatus = 'expires_soon';
            } else {
                expirationStatus = 'active';
            }
        }
        
        row.dataset.expiration = expirationStatus;
    });
}

// Filter licenses based on search and filter criteria
function filterLicenses() {
    const searchInput = document.getElementById('license-search');
    const statusFilter = document.getElementById('status-filter');
    const expirationFilter = document.getElementById('expiration-filter');
    
    if (!searchInput || !statusFilter || !expirationFilter) {
        return;
    }

    const searchTerm = searchInput.value.toLowerCase().trim();
    const statusValue = statusFilter.value;
    const expirationValue = expirationFilter.value;

    const rows = document.querySelectorAll('.license-row');
    const emptyStateNoLicenses = document.getElementById('empty-state-no-licenses');
    const emptyStateFiltered = document.getElementById('empty-state-filtered');
    
    let visibleCount = 0;

    rows.forEach(row => {
        const licenseName = row.dataset.licenseName || '';
        const licenseKey = row.dataset.licenseKey || '';
        const status = row.dataset.status || '';
        const expiration = row.dataset.expiration || '';

        // Check search term
        const matchesSearch = !searchTerm || 
            licenseName.includes(searchTerm) || 
            licenseKey.includes(searchTerm);

        // Check status filter
        const matchesStatus = statusValue === 'all' || status === statusValue;

        // Check expiration filter
        let matchesExpiration = true;
        if (expirationValue === 'never') {
            matchesExpiration = expiration === 'never';
        } else if (expirationValue === 'expires_soon') {
            matchesExpiration = expiration === 'expires_soon';
        } else if (expirationValue === 'expired') {
            matchesExpiration = expiration === 'expired';
        } else if (expirationValue === 'all') {
            matchesExpiration = true;
        }

        // Show/hide row based on all filters
        if (matchesSearch && matchesStatus && matchesExpiration) {
            row.style.display = '';
            visibleCount++;
        } else {
            row.style.display = 'none';
        }
    });

    // Show/hide empty states
    if (emptyStateNoLicenses) {
        emptyStateNoLicenses.style.display = (rows.length === 0) ? '' : 'none';
    }
    if (emptyStateFiltered) {
        if (visibleCount === 0 && rows.length > 0) {
            emptyStateFiltered.classList.remove('hidden');
        } else {
            emptyStateFiltered.classList.add('hidden');
        }
    }
}

// Clear all filters
function clearFilters() {
    const searchInput = document.getElementById('license-search');
    const statusFilter = document.getElementById('status-filter');
    const expirationFilter = document.getElementById('expiration-filter');

    if (searchInput) searchInput.value = '';
    if (statusFilter) statusFilter.value = 'all';
    if (expirationFilter) expirationFilter.value = 'all';

    filterLicenses();
}

function toggleLicenseEditPanel(licenseId) {
    const panel = document.getElementById('license-edit-panel');
    panel.classList.toggle('hidden');

    // If the panel is hidden, do nothing
    if (panel.classList.contains('hidden')) {
        return;
    }

    // Update the form action dynamically
    const form = document.getElementById('license-edit-form');
    const title = document.getElementById('license-edit-title');

    if (licenseId) {
        console.log('Editing license:', licenseId);
        form.action = `/license/${licenseId}/edit/`;
        title.textContent = 'Edit License';
        loadLicenseDetails(licenseId);
    } else {
        console.log('Creating a new license');
        form.action = '/licenses/create/';
        title.textContent = 'Create New License';
        loadLicenseDetails();
    }
}

function loadLicenseDetails(licenseId) {
    // Empty data if licenseId is not provided (i.e. when creating a new license)
    if (!licenseId) {
        document.getElementById('license_is_active').checked = true;
        document.getElementById('license_is_active_message').textContent = 'ACTIVE';
        document.getElementById('license_name').value = '';
        document.getElementById('license_max_devices').value = '1';
        document.getElementById('license_expires_at').value = '';
        document.getElementById('license_id').value = '';
        hideFormErrors();
        return;
    }

    // Convert licenseId to a number
    licenseId = Number(licenseId);

    // Get license details by ID
    let license;
    if (typeof licenses !== 'undefined') {
        license = licenses.find(l => l.id === licenseId);
    } else if (typeof licenseData !== 'undefined') {
        license = licenseData;
    }
    
    if (!license) {
        console.error('License not found:', licenseId);
        return;
    }

    console.log('License details:', license);

    // Populate the form fields with the license details
    document.getElementById('license_is_active').checked = license.is_active;
    document.getElementById('license_is_active_message').textContent = license.is_active ? 'ACTIVE' : 'INACTIVE';
    document.getElementById('license_name').value = license.name || '';
    document.getElementById('license_max_devices').value = license.max_devices || '';
    document.getElementById('license_id').value = license.id;
    
    // Handle expires_at - convert from Python datetime format to HTML datetime-local format
    if (license.expires_at) {
        // Expecting format like "2024-12-31T23:59:59" or "2024-12-31 23:59:59"
        const expiresAt = license.expires_at.replace(' ', 'T').substring(0, 16);
        document.getElementById('license_expires_at').value = expiresAt;
    } else {
        document.getElementById('license_expires_at').value = '';
    }
    
    hideFormErrors();
}

function toggleLicenseStatus() {
    const checkbox = document.getElementById('license_is_active');
    const message = document.getElementById('license_is_active_message');
    message.textContent = checkbox.checked ? 'ACTIVE' : 'INACTIVE';
}

function submitLicenseForm() {
    const form = document.getElementById('license-edit-form');
    const formData = new FormData(form);
    
    // Show loading state
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.textContent = 'Saving...';
    submitButton.disabled = true;

    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close the panel and reload the page
            toggleLicenseEditPanel();
            location.reload();
        } else {
            // Show errors
            showFormErrors(data.errors);
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showFormErrors(['An error occurred while saving the license.']);
        submitButton.textContent = originalText;
        submitButton.disabled = false;
    });
}

function showFormErrors(errors) {
    const errorContainer = document.getElementById('license-form-errors');
    const errorList = document.getElementById('license-error-list');
    
    errorList.innerHTML = '';
    
    if (typeof errors === 'object' && !Array.isArray(errors)) {
        // errors is an object with field names as keys
        for (const [field, messages] of Object.entries(errors)) {
            messages.forEach(message => {
                const li = document.createElement('li');
                li.textContent = `${field}: ${message}`;
                errorList.appendChild(li);
            });
        }
    } else if (Array.isArray(errors)) {
        // errors is an array of messages
        errors.forEach(message => {
            const li = document.createElement('li');
            li.textContent = message;
            errorList.appendChild(li);
        });
    }
    
    errorContainer.classList.remove('hidden');
}

function hideFormErrors() {
    const errorContainer = document.getElementById('license-form-errors');
    errorContainer.classList.add('hidden');
}

// Delete license with confirmation
// Attach to window to make it globally accessible from inline onclick handlers
window.deleteLicense = function(licenseId, licenseName) {
    if (!confirm(`Are you sure you want to delete the license "${licenseName}"?\n\nThis action cannot be undone.`)) {
        return;
    }
    
    // Get CSRF token
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                      document.cookie.match(/csrftoken=([^;]+)/)?.[1];
    
    if (!csrftoken) {
        alert('Error: CSRF token not found. Please refresh the page and try again.');
        return;
    }
    
    // Send DELETE request via POST (Django doesn't support DELETE method easily)
    fetch(`/license/${licenseId}/delete/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Reload page to show updated list
            location.reload();
        } else {
            alert('Error deleting license: ' + (data.message || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error deleting license. Please try again.');
    });
};

