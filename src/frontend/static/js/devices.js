// Toggle actions dropdown menu
function toggleActionsMenu() {
    const actionsMenu = document.getElementById('device-actions-menu');
    actionsMenu?.classList.toggle('hidden');
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const actionsButton = document.getElementById('device-actions-button');
    const actionsMenu = document.getElementById('device-actions-menu');

    if (actionsButton && actionsMenu && !actionsButton.contains(event.target) && !actionsMenu.contains(event.target)) {
        actionsMenu.classList.add('hidden');
    }
});

// Delete device with confirmation
function deleteDevice(deviceId, hostname) {
    if (!confirm(`Are you sure you want to delete device "${hostname}"?\n\nThis will permanently remove the device and all its reports.`)) {
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
    fetch(`/device/${deviceId}/delete/`, {
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
            // Redirect to device list page
            window.location.href = '/devices/';
        } else {
            alert('Error deleting device: ' + (data.message || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error deleting device. Please try again.');
    });
}

// Device search toggle - using event delegation for Firefox compatibility
document.addEventListener('DOMContentLoaded', function() {
    const searchContainer = document.getElementById('device-search-container');
    const searchInput = document.getElementById('device-search-input');
    const deviceRows = document.querySelectorAll('tbody tr[data-device-name]');

    function filterDevices(term) {
        const normalized = term.trim().toLowerCase();

        deviceRows.forEach((row) => {
            const deviceName = row.getAttribute('data-device-name') || '';
            const matches = !normalized || deviceName.includes(normalized);
            row.classList.toggle('hidden', !matches);
        });
    }

    // Use event delegation on document to avoid Firefox issues with hidden elements
    document.addEventListener('click', function(e) {
        const searchToggle = e.target.closest('#device-search-toggle');

        if (searchToggle && searchContainer) {
            const wasOpen = searchContainer.classList.contains('max-w-xs');

            searchContainer.classList.toggle('max-w-xs');
            searchContainer.classList.toggle('opacity-100');

            if (!wasOpen && searchInput) {
                // Wait a bit so the transition starts, then focus
                setTimeout(() => searchInput.focus(), 150);
            } else if (wasOpen) {
                // Closing the search panel should clear filters
                if (searchInput) {
                    searchInput.value = '';
                }
                filterDevices('');
            }
        }
    });

    if (searchInput) {
        searchInput.addEventListener('input', (event) => {
            filterDevices(event.target.value);
        });
    }
});
