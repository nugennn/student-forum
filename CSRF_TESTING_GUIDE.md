# CSRF Testing Guide

## Quick Start

### 1. Clear Everything and Restart
```bash
# Clear browser cache and cookies
# Then restart Django:
python manage.py runserver
```

### 2. Test Login Form
1. Go to `http://localhost:8000/accounts/login/`
2. Enter credentials
3. Click Login
4. ✅ Should succeed without CSRF error

### 3. Test AJAX Requests
1. Login successfully
2. Go to a question page
3. Try to:
   - Share a post
   - Repost a post
   - Quote a post
   - Like a post
4. ✅ All should work without CSRF errors

### 4. Test After Page Reload
1. Login
2. Reload page (F5)
3. Try to submit a form
4. ✅ Should work without CSRF error

---

## Verification Steps

### Check CSRF Token in Browser
1. Open DevTools (F12)
2. Go to Application/Storage > Cookies
3. Look for `csrftoken` cookie
4. ✅ Should be present with a long alphanumeric value

### Check CSRF Token in Form
1. Open DevTools (F12)
2. Go to Elements/Inspector
3. Find any `<form method="post">` element
4. Look for `<input type="hidden" name="csrfmiddlewaretoken" value="...">`
5. ✅ Should be present

### Check AJAX CSRF Header
1. Open DevTools (F12)
2. Go to Network tab
3. Make an AJAX request (e.g., share a post)
4. Click on the request
5. Go to Request Headers
6. Look for `X-CSRFToken` header
7. ✅ Should be present with token value

---

## Common Issues & Fixes

### Issue 1: "Forbidden (403) – CSRF verification failed"

**Fix 1: Clear Cookies**
```
DevTools > Application > Cookies > Delete all cookies > Reload
```

**Fix 2: Hard Refresh**
```
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)
```

**Fix 3: Check csrf-helper.js Loaded**
```
DevTools > Console > Type: getCsrfToken()
Should return a token string, not null
```

**Fix 4: Check Settings**
```python
# In main/settings.py, verify:
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False
```

### Issue 2: CSRF Token Not in Form

**Check Template:**
```html
<form method="post">
    {% csrf_token %}  <!-- Must be here -->
    <!-- form fields -->
</form>
```

### Issue 3: AJAX Request Failing

**Check JavaScript Console:**
```
DevTools > Console > Look for errors
```

**Verify csrf-helper.js:**
```
DevTools > Sources > static/js/csrf-helper.js
Should be loaded and no errors
```

---

## Test Scenarios

### Scenario 1: Fresh Login
```
1. Clear all cookies
2. Go to login page
3. Login with credentials
4. ✅ Should redirect to home without CSRF error
```

### Scenario 2: Form Submission
```
1. Login
2. Go to any page with a form
3. Fill and submit form
4. ✅ Should process without CSRF error
```

### Scenario 3: AJAX Request
```
1. Login
2. Go to question page
3. Click "Share" button
4. ✅ Should show success message without CSRF error
```

### Scenario 4: Multiple Requests
```
1. Login
2. Make multiple AJAX requests rapidly
3. ✅ All should succeed
```

### Scenario 5: Browser Back Button
```
1. Login
2. Submit a form
3. Click browser back button
4. ✅ Should not cause CSRF error
```

---

## Browser Console Commands

### Check CSRF Token
```javascript
getCsrfToken()
// Output: "abc123def456..." (token string)
```

### Check jQuery AJAX Setup
```javascript
$.ajaxSetup()
// Output: Should show beforeSend function
```

### Manually Test CSRF
```javascript
$.ajax({
    url: '/qa/share-post/',
    type: 'POST',
    data: {
        post_id: 1,
        post_type: 'question',
        share_type: 'share'
    },
    success: function(response) {
        console.log('Success:', response);
    },
    error: function(error) {
        console.log('Error:', error);
    }
});
```

---

## Debug Logging

### Enable Django Debug Logging
Add to `main/settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

### Check Server Logs
```
Look for CSRF-related messages in terminal running Django server
```

---

## Network Inspection

### Check Request Headers
1. DevTools > Network tab
2. Make a POST request
3. Click on the request
4. Go to "Headers" tab
5. Look for:
   - `X-CSRFToken` header (for AJAX)
   - `Cookie` header (should include `csrftoken`)

### Check Response Headers
1. DevTools > Network tab
2. Click on any response
3. Go to "Response Headers" tab
4. Look for:
   - `Set-Cookie: csrftoken=...`

---

## Performance Check

### Verify No Errors
```
DevTools > Console > Should be empty (no red errors)
```

### Check Load Time
```
DevTools > Network > Should load quickly
```

### Check Resources
```
DevTools > Application > Storage > Cookies
Should only have necessary cookies
```

---

## Rollback Instructions

If CSRF fixes cause issues:

### Step 1: Revert Settings
```python
# In main/settings.py, remove or comment out:
# CSRF_COOKIE_HTTPONLY = False
# CSRF_COOKIE_SECURE = False
# CSRF_TRUSTED_ORIGINS = [...]
# CSRF_COOKIE_SAMESITE = 'Lax'
```

### Step 2: Revert Template
```html
<!-- In templates/profile/base.html, remove: -->
<!-- <script src="{% static 'js/csrf-helper.js' %}"></script> -->
```

### Step 3: Restart Server
```bash
python manage.py runserver
```

---

## Success Indicators

✅ All of the following should be true:

- [ ] Login form works without CSRF error
- [ ] All POST forms work without CSRF error
- [ ] AJAX requests work without CSRF error
- [ ] Page reload doesn't cause CSRF error
- [ ] Browser back button doesn't cause CSRF error
- [ ] CSRF token appears in forms
- [ ] CSRF token appears in AJAX headers
- [ ] No console errors related to CSRF
- [ ] No server errors related to CSRF

---

## Support

If issues persist:

1. Check `CSRF_FIX_SUMMARY.md` for detailed implementation
2. Review browser console for JavaScript errors
3. Check Django server logs for CSRF-related messages
4. Verify all files were modified correctly
5. Clear all cookies and restart server
6. Try in incognito/private browsing mode
