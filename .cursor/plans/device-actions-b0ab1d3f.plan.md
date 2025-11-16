<!-- b0ab1d3f-5134-4b1d-bce0-38a0358c3165 d3dc5379-1a73-4046-9c75-941ae87ddf11 -->
# Add Actions Dropdown to Device Detail View

## 1. Add WeasyPrint Dependency

Update `src/requirements.txt` to include WeasyPrint for PDF generation:

- Add `weasyprint==61.2` (latest stable version)

## 2. Create Actions Dropdown UI

Modify `src/frontend/templates/device_detail.html`:

- Add dropdown button in top-right corner of the Overview section (line ~25, after the h3 title)
- Follow the profile menu pattern from `base.html` (lines 70-97)
- Structure: Button with chevron icon + hidden menu with two options
- Use Tailwind classes for styling (similar to existing UI)

## 3. Create JavaScript for Dropdown & Delete

Create `src/frontend/static/js/devices.js`:

- `toggleActionsMenu()` - Show/hide dropdown (similar to `toggleProfileMenu()`)
- `deleteDevice()` - Handle delete with confirmation dialog
- Follow the pattern from `rules.js` (lines 202-238) for AJAX delete
- Confirmation message: "Are you sure you want to delete device {hostname}? This will permanently remove the device and all its reports."

## 4. Create PDF Export View

Add `device_export_pdf()` view in `src/frontend/views.py`:

- Get device and latest report (same as `device_detail`)
- Create PDF template with device overview, compliance status, and security feedback
- Use WeasyPrint to render HTML template to PDF
- Return PDF as downloadable file with name: `device-{hostname}-{timestamp}.pdf`

## 5. Create PDF Template

Create `src/frontend/templates/device/device_pdf.html`:

- Standalone template (no extends base.html)
- Include device overview section
- Include compliance section with ruleset evaluations
- Include security feedback (warnings & suggestions)
- Add CSS for PDF formatting (page breaks, styling)

## 6. Create Delete View

Add `device_delete()` view in `src/frontend/views.py`:

- Follow pattern from `ruleset_delete()` (lines 498-515)
- Hard delete: `device.delete()` (CASCADE will remove associated reports)
- Support AJAX (return JSON) and traditional requests (redirect)
- Require POST method + @csrf_protect

## 7. Add URL Routes

Update `src/frontend/urls.py`:

- Add `path('device/<int:device_id>/export-pdf/', views.device_export_pdf, name='device_export_pdf')`
- Add `path('device/<int:device_id>/delete/', views.device_delete, name='device_delete')`

## 8. Load JavaScript in Template

Update `src/frontend/templates/device_detail.html`:

- Add `<script src="{% static 'js/devices.js' %}"></script>` in the scripts block (line ~240)

## Key Files to Modify

- `src/requirements.txt` - Add WeasyPrint
- `src/frontend/templates/device_detail.html` - Add dropdown button
- `src/frontend/static/js/devices.js` - New file for dropdown/delete logic
- `src/frontend/views.py` - Add `device_export_pdf()` and `device_delete()` views
- `src/frontend/templates/device/device_pdf.html` - New PDF template
- `src/frontend/urls.py` - Add new routes

### To-dos

- [ ] Add WeasyPrint to requirements.txt
- [ ] Add Actions dropdown button to device_detail.html
- [ ] Create devices.js with dropdown toggle and delete function
- [ ] Add device_delete view to views.py
- [ ] Create device_pdf.html template for PDF export
- [ ] Add device_export_pdf view to views.py with WeasyPrint
- [ ] Add URL routes for export-pdf and delete endpoints
- [ ] Test both PDF export and delete device functionality