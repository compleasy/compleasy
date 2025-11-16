// Toggle actions dropdown menu
function toggleActionsMenu() {
    const actionsMenu = document.getElementById('device-actions-menu');
    actionsMenu.classList.toggle('hidden');
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

