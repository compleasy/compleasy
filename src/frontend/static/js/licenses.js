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
});

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
        document.getElementById('license_max_devices').value = '';
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

