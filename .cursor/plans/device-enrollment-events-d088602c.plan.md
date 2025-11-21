<!-- d088602c-b22c-4a6e-b5d0-c67a0b4edb7c 9ef2f257-860f-456a-87bb-fb3515b4eb1a -->
# Add Device Enrollment Events to Activity View

## 1. Create DeviceEvent Model

**File**: `src/api/models.py`

Add new model after `DiffReport` (around line 78):

```python
class DeviceEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('enrolled', 'Device Enrolled'),
        # Future: ('removed', 'Device Removed'), ('license_changed', 'License Changed'), etc.
    ]
    
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['device', '-created_at']),
            models.Index(fields=['event_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.device.hostname or self.device.hostid} - {self.get_event_type_display()}"
```

## 2. Create and Run Migration

Generate migration:

```bash
docker compose -f docker-compose.dev.yml run --rm trikusec python manage.py makemigrations
```

The migration will run automatically in test containers.

## 3. Create Enrollment Events on Device Creation

**File**: `src/api/views.py` - `upload_report()` function (around line 71)

After creating new device, add enrollment event:

```python
# After line 71: device = Device.objects.create(...)
from api.models import DeviceEvent

device = Device.objects.create(hostid=post_hostid, hostid2=post_hostid2, licensekey=licensekey)
# Create enrollment event
DeviceEvent.objects.create(device=device, event_type='enrolled')
```

## 4. Update Activity View to Include DeviceEvents

**File**: `src/frontend/views.py` - `activity()` function (starting line 978)

After fetching DiffReport activities (around line 1114, before grouping), query and merge DeviceEvents:

```python
# After filtering activities (line 1114), before grouped_activities_list:

# Fetch device enrollment events
device_events = DeviceEvent.objects.select_related('device').all().order_by('-created_at')

# Convert DeviceEvents to activity format
event_activities = []
for event in device_events:
    event_activities.append({
        'device': event.device,
        'created_at': event.created_at,
        'event_type': event.event_type,
        'type': 'enrollment',  # Special type for enrollment events
        'metadata': event.metadata,
    })

# Merge and sort all activities by timestamp
all_activities = activities + event_activities
all_activities = sorted(all_activities, key=lambda x: x['created_at'], reverse=True)
```

Then use `all_activities` instead of `activities` for grouping logic.

## 5. Update Template for Enrollment Event Display

**File**: `src/frontend/templates/activity.html`

Add special rendering for enrollment events in the activity card loop. After line 264 (inside the type block loop), add enrollment event handling:

```html
{% if block.type == 'enrollment' %}
    {% for activity in block.activities %}
    <div class="activity-entry {% if forloop.counter > preview_limit %}hidden extra-entry{% endif %}">
        <div class="flex items-center justify-between mb-2">
            <div class="flex items-center space-x-2">
                <svg class="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="font-semibold text-gray-900">Device enrolled</span>
            </div>
            <div class="text-xs text-gray-500">{{ activity.created_at|timesince }} ago</div>
        </div>
        <p class="text-sm text-gray-600">New device registered with TrikuSec</p>
    </div>
    {% endfor %}
{% elif block.type == 'changed' %}
    {# Existing changed logic #}
```

Add CSS for enrollment pill in activity styles (around line 50):

```css
.activity-pill--enrollment {
    background-color: #d1fae5;
    color: #065f46;
}
```

Update the type_blocks loop (line 1194) to include 'enrollment':

```python
for change_type in ['enrollment', 'changed', 'added', 'removed', 'other']:
```

## 6. Add Tests

**File**: `src/api/tests.py`

Add test for enrollment event creation:

```python
def test_upload_report_creates_enrollment_event(self, test_license_key, sample_lynis_report):
    """Test that uploading a report for a new device creates an enrollment event."""
    client = Client()
    url = reverse('upload_report')
    
    response = client.post(url, {
        'licensekey': test_license_key.licensekey,
        'hostid': 'new-host-enrollment',
        'hostid2': 'new-host-enrollment-2',
        'data': sample_lynis_report
    })
    
    assert response.status_code == 200
    
    # Verify device was created
    device = Device.objects.get(hostid='new-host-enrollment')
    
    # Verify enrollment event was created
    enrollment_event = DeviceEvent.objects.filter(device=device, event_type='enrolled').first()
    assert enrollment_event is not None
    assert enrollment_event.created_at is not None

def test_upload_report_no_enrollment_event_for_existing_device(self, test_license_key, sample_lynis_report):
    """Test that uploading a report for existing device does NOT create another enrollment event."""
    # Create device first
    device = Device.objects.create(
        hostid='existing-host',
        hostid2='existing-host-2',
        licensekey=test_license_key
    )
    
    client = Client()
    url = reverse('upload_report')
    
    # Upload first report (device exists, so no enrollment event)
    response = client.post(url, {
        'licensekey': test_license_key.licensekey,
        'hostid': 'existing-host',
        'hostid2': 'existing-host-2',
        'data': sample_lynis_report
    })
    
    assert response.status_code == 200
    
    # Should have no enrollment events (device was created manually, not via upload)
    enrollment_count = DeviceEvent.objects.filter(device=device, event_type='enrolled').count()
    assert enrollment_count == 0
```

**File**: `src/frontend/tests_e2e.py` (optional)

Add E2E test to verify enrollment events appear in Activity view (can be added after manual verification).

## Key Implementation Notes

- DeviceEvent model uses `metadata` JSONField for future extensibility
- Only first report upload creates enrollment event (when `created = True` in upload_report)
- Enrollment events bypass ActivityIgnorePattern filtering
- Enrollment events displayed as distinct cards with green checkmark icon
- Event type order: enrollment first, then changed/added/removed/other
- All activities sorted by timestamp across both DiffReport and DeviceEvent sources

### To-dos

- [ ] Create DeviceEvent model in api/models.py
- [ ] Generate and verify migration for DeviceEvent model
- [ ] Modify upload_report() to create enrollment events for new devices
- [ ] Update activity() view to query and merge DeviceEvents with DiffReport
- [ ] Add enrollment event rendering to activity.html template
- [ ] Add unit tests for enrollment event creation
- [ ] Run full test suite to verify implementation