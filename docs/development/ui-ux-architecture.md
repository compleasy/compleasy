# UI/UX Architecture

TrikuSec follows a consistent UI/UX pattern for CRUD operations to provide a modern, efficient user experience.

## Overview

### The Three-Layer Pattern

TrikuSec uses a **consistent three-layer approach** for data management:

1. **List Views**: Full-window display showing all items
2. **Detail Views**: Full-window view with related data and relationships
3. **Create/Edit Operations**: Collapsible right-side panel (sidebar)

```
┌─────────────────────────────────────────┐
│ List View (Full Window)                │
│ ┌─────────────────────────────────────┐ │
│ │ Item 1                         Edit │ │
│ │ Item 2                         Edit │ │
│ │ Item 3                         Edit │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Detail View (Full Window)               │
│ ┌─────────────────────────────────────┐ │
│ │ Item Details                        │ │
│ │ • Related Data                      │ │
│ │ • Relationships                     │ │
│ │ • History                           │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘

┌────────────────────────┬────────────────┐
│ List/Detail View       │ Edit Sidebar   │
│                        │ ┌────────────┐ │
│                        │ │ Form       │ │
│                        │ │ Fields     │ │
│                        │ └────────────┘ │
└────────────────────────┴────────────────┘
```

## Rationale

This pattern provides several key benefits:

### 1. Context Preservation
Users can see the list or related data while editing, maintaining context and reducing cognitive load.

### 2. Reduced Navigation
No page reloads or navigation interruptions. Users stay focused on their task.

### 3. Quick Operations
Fast edits without losing place. Ideal for frequent, repetitive operations.

### 4. Modern UX
Follows patterns from popular applications like:
- Gmail (compose/reply sidebar)
- Slack (thread/message sidebar)
- Linear (issue detail sidebar)
- Notion (page editing)

## Decision Guidelines

### ✅ Use Collapsible Sidebar For:

- **Simple forms** (3-6 fields)
  - Example: License keys (name, max devices, expiration, active status)
- **Frequent edit operations**
  - Example: Updating rule names, toggling rule status
- **Quick create/update workflows**
  - Example: Creating multiple licenses in succession
- **Forms where context matters**
  - Example: Editing while viewing related devices

### ❌ Use Full-Page Forms For:

- **Complex forms** (10+ fields)
  - Example: Multi-section configuration pages
- **Multi-step wizards**
  - Example: Guided setup processes
- **Critical operations**
  - Example: Payment forms, destructive actions
- **Rich content editing**
  - Example: Markdown editors, WYSIWYG content
- **Heavy media uploads**
  - Example: Bulk file uploads with previews
- **Mobile-first features**
  - Sidebars don't work well on small screens

## Current Implementations

### 1. Rules (`src/frontend/templates/policy/rule_edit_sidebar.html`)
- **Form fields**: Name, description, query, enabled status
- **Context**: See rule list while editing
- **JavaScript**: `src/frontend/static/js/rules.js`

### 2. Rulesets (`src/frontend/templates/policy/ruleset_selection_sidebar.html`)
- **Form fields**: Ruleset selection checkboxes
- **Context**: See device details while assigning rulesets
- **JavaScript**: `src/frontend/static/js/rulesets.js`

### 3. Licenses (`src/frontend/templates/license/license_edit_sidebar.html`)
- **Form fields**: Name, max devices, expiration, active status
- **Context**: See license list or device list while editing
- **JavaScript**: `src/frontend/static/js/licenses.js`

## Implementation Pattern

### Template Structure

```html
<!-- Include in both list and detail pages -->
<div id="item-edit-panel" class="hidden fixed right-0 top-0 h-full w-1/4 bg-white shadow-md z-50">
    <!-- Header -->
    <div class="flex justify-between items-center p-4 border-b bg-gray-200">
        <h2 class="text-xl font-bold" id="item-edit-title">Edit Item</h2>
        <button class="item-edit-panel-button text-gray-600">
            <!-- Close icon (X) -->
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
        </button>
    </div>
    
    <!-- Form -->
    <form id="item-edit-form" method="POST">
        {% csrf_token %}
        <input type="hidden" name="item_id" id="item_id" value="">
        
        <!-- Form fields here -->
        <div class="p-4 mb-4">
            <label for="item_name" class="block text-sm font-medium text-gray-700">
                Name <span class="text-red-500">*</span>
            </label>
            <input type="text" id="item_name" name="name" 
                   class="mt-1 p-2 block w-full border border-gray-300 rounded-md" 
                   required />
        </div>
        
        <!-- Error messages container -->
        <div id="item-form-errors" class="hidden p-4 mb-4 mx-4 bg-red-100 border border-red-400 text-red-700 rounded">
            <ul id="item-error-list"></ul>
        </div>
        
        <!-- Action buttons (fixed at bottom) -->
        <div class="absolute flex space-x-2 w-full bottom-0 p-4 bg-gray-200">
            <button type="submit" class="w-1/2 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                Save
            </button>
            <button type="button" class="item-edit-panel-button w-1/2 bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600">
                Cancel
            </button>
        </div>
    </form>
</div>
```

### JavaScript Structure

**Important: Firefox Compatibility**

When implementing event listeners for buttons in sidebars (especially those initially hidden), use **event delegation** instead of direct event listeners. Firefox has issues with attaching listeners to hidden elements or elements that become visible dynamically.

```javascript
// ✅ GOOD: Event delegation (works in all browsers including Firefox)
const panel = document.getElementById('rule-selection-panel');
if (panel) {
    panel.addEventListener('click', function(e) {
        const button = e.target.closest('.rule-edit-panel-button');
        if (button) {
            e.preventDefault();
            e.stopPropagation();
            const ruleId = button.hasAttribute('data-rule-id') ? button.dataset.ruleId : null;
            openRuleEditFromSelection(ruleId);
        }
    });
}

// ❌ BAD: Direct event listener (may fail in Firefox for hidden elements)
const button = document.querySelector('.rule-edit-panel-button');
button.addEventListener('click', function() { ... }); // May not work in Firefox
```

```javascript
// Toggle sidebar visibility
function toggleItemEditPanel(itemId) {
    const panel = document.getElementById('item-edit-panel');
    panel.classList.toggle('hidden');
    
    // Don't load data if closing
    if (panel.classList.contains('hidden')) {
        return;
    }
    
    // Update form action and title
    const form = document.getElementById('item-edit-form');
    const title = document.getElementById('item-edit-title');
    
    if (itemId) {
        // Edit mode
        form.action = `/item/${itemId}/edit/`;
        title.textContent = 'Edit Item';
        loadItemDetails(itemId);
    } else {
        // Create mode
        form.action = '/item/create/';
        title.textContent = 'Create New Item';
        loadItemDetails(); // Empty form
    }
}

// Load item data into form
function loadItemDetails(itemId) {
    if (!itemId) {
        // Clear form for new item
        document.getElementById('item_name').value = '';
        document.getElementById('item_id').value = '';
        hideFormErrors();
        return;
    }
    
    // Find item in data (passed from Django)
    const item = items.find(i => i.id === Number(itemId));
    if (!item) {
        console.error('Item not found:', itemId);
        return;
    }
    
    // Populate form fields
    document.getElementById('item_name').value = item.name;
    document.getElementById('item_id').value = item.id;
    hideFormErrors();
}

// Submit form via AJAX
function submitItemForm() {
    const form = document.getElementById('item-edit-form');
    const formData = new FormData(form);
    const submitButton = form.querySelector('button[type="submit"]');
    
    // Show loading state
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
            // Close panel and reload page
            toggleItemEditPanel();
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
        showFormErrors(['An error occurred while saving.']);
        submitButton.textContent = originalText;
        submitButton.disabled = false;
    });
}

// Error handling
function showFormErrors(errors) {
    const errorContainer = document.getElementById('item-form-errors');
    const errorList = document.getElementById('item-error-list');
    
    errorList.innerHTML = '';
    
    if (typeof errors === 'object' && !Array.isArray(errors)) {
        // Django form errors: {field: [errors]}
        for (const [field, messages] of Object.entries(errors)) {
            messages.forEach(message => {
                const li = document.createElement('li');
                li.textContent = `${field}: ${message}`;
                errorList.appendChild(li);
            });
        }
    } else if (Array.isArray(errors)) {
        // Simple error messages
        errors.forEach(message => {
            const li = document.createElement('li');
            li.textContent = message;
            errorList.appendChild(li);
        });
    }
    
    errorContainer.classList.remove('hidden');
}

function hideFormErrors() {
    document.getElementById('item-form-errors').classList.add('hidden');
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Close/cancel buttons
    document.querySelectorAll('.item-edit-panel-button').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            toggleItemEditPanel();
        });
    });
    
    // Form submission
    const form = document.getElementById('item-edit-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            submitItemForm();
        });
    }
});
```

### Django View Structure

```python
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
import json

@login_required
def item_list(request):
    """List view with sidebar support"""
    items = Item.objects.all().order_by('-created_at')
    
    # Serialize for JavaScript
    items_data = [
        {
            'id': item.id,
            'name': item.name,
            # ... other fields
        }
        for item in items
    ]
    
    return render(request, 'item/item_list.html', {
        'items': items,
        'items_json': json.dumps(items_data),
    })

@login_required
def item_detail(request, item_id):
    """Detail view with sidebar support"""
    item = get_object_or_404(Item, id=item_id)
    
    # Serialize for JavaScript
    item_data = {
        'id': item.id,
        'name': item.name,
        # ... other fields
    }
    
    return render(request, 'item/item_detail.html', {
        'item': item,
        'item_json': json.dumps(item_data),
    })

@login_required
@csrf_protect
def item_create(request):
    """Create item (AJAX + fallback)"""
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            
            # AJAX request: return JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'item_id': item.id,
                    'message': 'Item created successfully'
                })
            
            # Traditional request: redirect
            return redirect('item_detail', item_id=item.id)
        else:
            # AJAX request: return errors
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
    
    # Fallback for GET or non-AJAX POST
    return redirect('item_list')

@login_required
@csrf_protect
def item_edit(request, item_id):
    """Edit item (AJAX + fallback)"""
    item = get_object_or_404(Item, id=item_id)
    
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            
            # AJAX request: return JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'item_id': item.id,
                    'message': 'Item updated successfully'
                })
            
            # Traditional request: redirect
            return redirect('item_detail', item_id=item.id)
        else:
            # AJAX request: return errors
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
    
    # Fallback for GET or non-AJAX POST
    return redirect('item_detail', item_id=item.id)
```

### Template Integration

In list and detail templates:

```html
{% extends 'base.html' %}
{% load static %}

{% block content %}
    <!-- Your list/detail content here -->
    
    <!-- Include the sidebar -->
    {% include 'item/item_edit_sidebar.html' %}
    
    <script>
        // Pass data to JavaScript
        const items = {{ items_json|safe }};
    </script>
    <script src="{% static 'js/items.js' %}"></script>
{% endblock %}
```

## Best Practices

### 1. Error Handling
- Show validation errors inline without closing the sidebar
- Display field-specific errors next to the relevant field
- Provide clear, actionable error messages

### 2. Loading States
- Disable submit button while saving
- Show "Saving..." text or spinner
- Prevent double submissions

### 3. Success Feedback
- Currently: Page reload (simple, reliable)
- Future: Toast notifications (better UX, no reload)

### 4. Keyboard Support
- **Planned**: `Esc` key to close sidebar
- **Planned**: `Cmd/Ctrl + Enter` to save
- Tab navigation should work naturally

### 5. Mobile Responsiveness
- Consider full-screen modal on mobile
- Test sidebar behavior on tablets
- Ensure touch targets are large enough

### 6. Data Synchronization
- Serialize data from Django to JavaScript using `json.dumps()`
- Keep data serialization in the view layer
- Handle timezone conversions properly (use `.isoformat()`)

### 7. Consistency
- Use the same class names (`.item-edit-panel-button`)
- Follow the same HTML structure
- Use consistent error handling patterns

### 8. Firefox Compatibility
- **Always use event delegation** for buttons in sidebars, especially when panels are initially hidden
- Direct event listeners may fail in Firefox when attached to hidden elements
- Event delegation (`addEventListener` on parent, use `closest()` to find target) works reliably across all browsers
- See JavaScript Structure section above for example implementation

## Testing Checklist

When implementing a new sidebar:

- [ ] Create mode works (empty form)
- [ ] Edit mode works (pre-populated form)
- [ ] Save button submits via AJAX
- [ ] Cancel button closes sidebar
- [ ] Close button (X) closes sidebar
- [ ] Validation errors display inline
- [ ] Success closes sidebar and updates view
- [ ] Works from list page
- [ ] Works from detail page
- [ ] Form data serializes correctly
- [ ] Backend handles AJAX and fallback
- [ ] No console errors
- [ ] Loading state shows during save
- [ ] Double-submit is prevented

## Migration Guide

### Converting Full-Page Form to Sidebar

1. **Create sidebar template** (e.g., `item_edit_sidebar.html`)
   - Copy form fields from existing template
   - Wrap in sidebar structure
   - Add error container

2. **Create JavaScript file** (e.g., `items.js`)
   - Implement toggle function
   - Implement load function
   - Implement submit function
   - Add event listeners

3. **Update views**
   - Add JSON serialization
   - Add AJAX response handling
   - Keep traditional fallback

4. **Update list/detail templates**
   - Include sidebar template
   - Load JavaScript file
   - Pass data to JavaScript
   - Convert links to buttons with `onclick`

5. **Delete old form template**
   - Only after testing everything works

6. **Test thoroughly**
   - All items from testing checklist
   - Both list and detail pages
   - Create and edit modes

## Future Enhancements

### Planned Improvements

1. **Toast Notifications**
   - Replace page reload with toast feedback
   - Show success/error messages elegantly

2. **Keyboard Shortcuts**
   - `Esc` to close sidebar
   - `Cmd/Ctrl + Enter` to save
   - Arrow keys for navigation

3. **Animation**
   - Smooth slide-in/out transitions
   - Loading spinners
   - Success animations

4. **Mobile Optimization**
   - Full-screen modal on small screens
   - Better touch interactions
   - Swipe to close

5. **Auto-save**
   - Save draft changes automatically
   - Restore unsaved changes on reopen

## References

- **AGENTS.md** - Detailed implementation guidelines
- **Existing implementations**: Rules, Rulesets, Licenses
- **Django JsonResponse**: [Django documentation](https://docs.djangoproject.com/en/stable/ref/request-response/#jsonresponse-objects)
- **Fetch API**: [MDN documentation](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)

---

**Questions or suggestions?** Open an issue or submit a pull request!

