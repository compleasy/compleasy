<!-- fafca527-2cae-44d8-b0e1-1b2bed57c15e 3de1196c-6fda-496b-947c-71dd9005d295 -->
# Move Enrollment Script to Lynis API

## Objective

Move the enrollment script endpoint from the frontend (`/download/enroll.sh`) to the Lynis API (`/api/lynis/enroll/`) to allow servers to complete enrollment without accessing the admin UI endpoint, strengthening the dual-endpoint security architecture.

## Implementation Steps

### 1. Move View Function

- **Move** `enroll_sh()` function from `src/frontend/views.py` (line 386) to `src/api/views.py`
- **Remove** `@login_required` decorator (API endpoints don't use session auth)
- **Keep** license validation logic intact
- **Update** imports as needed (render, settings, urlparse, etc.)
- **Update** template reference from `enroll.html` to `api/enroll.sh`

### 2. Update URL Routing

- **Add** new route in `src/api/urls.py`: `path('lynis/enroll/', views.enroll_sh, name='enroll_sh')`
- **Remove** old route from `src/frontend/urls.py`: `path('download/enroll.sh', ...)`
- This creates the new endpoint: `/api/lynis/enroll/`

### 3. Move Template

- **Move** `src/frontend/templates/enroll.html` to `src/api/templates/api/enroll.sh`
- Template will render as shell script (no HTML base needed)
- Keep template content unchanged (already generates valid bash script)

### 4. Update Frontend References

- **File**: `src/frontend/static/js/license_selection.js`
- Line 40: Change `/download/enroll.sh?licensekey=` to `/api/lynis/enroll/?licensekey=`
- Line 46: Same change
- Update to use `trikusecLynisUploadServer` (API URL) instead of `trikusecUrl` (Admin UI URL)

- **File**: `src/frontend/templates/license/license_selection_section.html`
- Line 34: Change `/download/enroll.sh?licensekey=` to `/api/lynis/enroll/?licensekey=`
- Change `{{ trikusec_url }}` to `{{ trikusec_lynis_api_url }}`

### 5. Update View Context Variables

- **File**: `src/frontend/views.py`
- `onboarding()` view (line 92): Pass `trikusec_lynis_api_url` (full URL) instead of just `trikusec_lynis_upload_server`
- `enroll_device()` view (line 1589): Same change
- Remove `parsed_lynis_api_url.netloc` logic; pass full API URL directly

### 6. Update Templates

- **File**: `src/frontend/templates/onboarding.html`
- Line 90: Change `trikusecUrl` to `trikusecLynisApiUrl` in JavaScript config
- **File**: `src/frontend/templates/license/enroll_device.html`
- Line 79: Same change

### 7. Update Integration Tests

- **File**: `lynis/run-lynis-test.sh`
- Line 58: Change `${TRIKUSEC_SERVER_URL}/download/enroll.sh` to `${TRIKUSEC_SERVER_URL}/api/lynis/enroll/`

### 8. Update Documentation

- **File**: `docs/configuration/security.md`
- Line 137: Update "Used for downloading `enroll.sh`" to reflect it's now served from Lynis API
- Update the security benefits section to emphasize that enrollment is now fully API-based

- **File**: `docs/configuration/environment-variables.md`
- Line 156: Update reference to enrollment script endpoint

### 9. Update Agent Guidelines

- **File**: `.cursorrules` (workspace rules)
- Update references to enrollment script endpoint in critical endpoints section
- Document the API endpoint location

## Testing

- Run unit tests to verify API endpoint works
- Run integration test (`lynis/run-lynis-test.sh`) to verify end-to-end enrollment
- Manually test enrollment from frontend UI (onboarding and enroll pages)
- Verify license validation still works correctly

## Expected Outcome

After this change, servers will:

- Download enrollment script from `/api/lynis/enroll/` (Lynis API)
- Complete entire enrollment using only `TRIKUSEC_LYNIS_API_URL`
- No longer need access to `TRIKUSEC_URL` (Admin UI)
- Strengthen security isolation between admin and API endpoints

### To-dos

- [ ] Move enroll_sh() from frontend/views.py to api/views.py
- [ ] Update URL routing in api/urls.py and frontend/urls.py
- [ ] Move enroll.html template to api/templates/api/enroll.sh
- [ ] Update JavaScript references in license_selection.js
- [ ] Update template references and context variables
- [ ] Update integration test script with new endpoint
- [ ] Update documentation to reflect new endpoint location
- [ ] Run tests to verify enrollment works end-to-end