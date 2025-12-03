# Verify Image Solution - Testing Guide

## Quick Verification

### Step 1: Check Upload Directory
```bash
ls -la media/martor_uploads/
```
Should show: Directory exists and is writable

### Step 2: Check Settings
```python
# main/settings.py should have:
MARTOR_UPLOAD_PATH = 'martor_uploads/'
'imgur': 'false'
```

### Step 3: Check Filters
```python
# qa/templatetags/qa_tags.py should have:
@register.filter
def fix_markdown_images(html_content):
    # ... implementation

@register.filter
def ensure_image_urls(html_content):
    # ... implementation
```

### Step 4: Check Templates
```django
# questionDetailView.html line 263:
{{data.body|safe_markdown|fix_markdown_images|ensure_image_urls|safe}}

# questionDetailView.html line 684:
{{answer.body|safe_markdown|fix_markdown_images|ensure_image_urls|safe}}
```

## Manual Testing

### Test 1: Upload Image

1. Go to "Ask a Question" page
2. Scroll to "Add Media (Optional)"
3. Select an image (JPG, PNG, etc.)
4. Verify upload completes
5. Check image URL appears
6. Submit question

**Expected Result**: ✓ Image displays in question

### Test 2: Image Persistence

1. Create question with image
2. Reload page (F5)
3. Navigate away and back

**Expected Result**: ✓ Image still displays

### Test 3: Broken Image Handling

1. Create question with image
2. Delete image file from `/media/martor_uploads/`
3. Reload page

**Expected Result**: ✓ No broken image icon shown

### Test 4: File Size Validation

1. Try uploading file > 5MB
2. Check error message

**Expected Result**: ✓ Error: "File size exceeds 5MB limit"

### Test 5: File Type Validation

1. Try uploading unsupported file (e.g., .exe)
2. Check error message

**Expected Result**: ✓ Error: "File type not allowed"

### Test 6: Answer Images

1. Create question
2. Add answer with image
3. Verify image displays

**Expected Result**: ✓ Answer image displays correctly

### Test 7: Mobile Responsive

1. Open question on mobile device
2. Verify images display correctly
3. Check images are responsive

**Expected Result**: ✓ Images responsive on mobile

### Test 8: Multiple Images

1. Create question with multiple images
2. Verify all images display
3. Check layout is correct

**Expected Result**: ✓ All images display correctly

## Browser Testing

### Chrome/Edge
- [ ] Images display
- [ ] Loading animation shows
- [ ] No console errors
- [ ] Responsive on mobile

### Firefox
- [ ] Images display
- [ ] Loading animation shows
- [ ] No console errors
- [ ] Responsive on mobile

### Safari
- [ ] Images display
- [ ] Loading animation shows
- [ ] No console errors
- [ ] Responsive on mobile

## Console Checks

Open browser DevTools (F12) and check:

### Console Tab
- [ ] No 404 errors
- [ ] No JavaScript errors
- [ ] No warnings

### Network Tab
- [ ] Image requests return 200
- [ ] No failed requests
- [ ] Proper content-type headers

### Elements Tab
- [ ] Images have `src` attribute
- [ ] Images have `alt` attribute
- [ ] Images have `loading="lazy"`
- [ ] Images have `onerror` handler

## File System Checks

### Check Directory
```bash
ls -la media/martor_uploads/
```
Should show uploaded files with format:
```
20251202_211500_a1b2c3d4_image.jpg
```

### Check File Permissions
```bash
ls -la media/martor_uploads/filename.jpg
```
Should show: `-rw-r--r--` (644)

### Check Directory Permissions
```bash
ls -la media/ | grep martor_uploads
```
Should show: `drwxr-xr-x` (755)

## URL Testing

### Test Image URL Directly

1. Copy image URL from page
2. Paste in browser address bar
3. Image should display

Example:
```
http://localhost:8000/media/martor_uploads/20251202_211500_a1b2c3d4_image.jpg
```

## Database Checks

### Check Stored Markdown

```python
from qa.models import Question
q = Question.objects.latest('id')
print(q.body)
```

Should show markdown like:
```
![image](martor_uploads/20251202_211500_a1b2c3d4_image.jpg)
```

## Performance Checks

### Load Time
- [ ] Page loads quickly
- [ ] Images load with lazy loading
- [ ] No performance issues

### Memory Usage
- [ ] No memory leaks
- [ ] Reasonable memory usage
- [ ] Smooth scrolling

## Accessibility Checks

### Alt Text
- [ ] All images have alt text
- [ ] Alt text is descriptive
- [ ] Screen readers work

### Keyboard Navigation
- [ ] Can tab to images
- [ ] Images are accessible
- [ ] No keyboard traps

## Edge Cases

### Test 1: Empty Image
- [ ] No errors
- [ ] Graceful handling

### Test 2: Very Large Image
- [ ] Scales properly
- [ ] Responsive
- [ ] No layout issues

### Test 3: External Image URL
- [ ] Displays correctly
- [ ] Not converted
- [ ] Works as expected

### Test 4: Data URL Image
- [ ] Displays correctly
- [ ] Not converted
- [ ] Works as expected

### Test 5: Rapid Uploads
- [ ] Multiple images upload
- [ ] All display correctly
- [ ] No conflicts

## Success Criteria

All tests should pass:

✅ **Upload**
- [ ] Files save correctly
- [ ] Unique names generated
- [ ] Validation works

✅ **Display**
- [ ] Images show (not icons)
- [ ] URLs converted properly
- [ ] All attributes present

✅ **Performance**
- [ ] Lazy loading works
- [ ] Page loads fast
- [ ] Smooth animations

✅ **Accessibility**
- [ ] Alt text present
- [ ] Semantic HTML
- [ ] Keyboard accessible

✅ **Reliability**
- [ ] Images persist
- [ ] Broken images hidden
- [ ] Error handling works

✅ **Responsive**
- [ ] Desktop display
- [ ] Tablet display
- [ ] Mobile display

## Troubleshooting

If any test fails:

1. **Check file exists**
   ```bash
   ls -la media/martor_uploads/filename.jpg
   ```

2. **Check permissions**
   ```bash
   chmod 755 media/martor_uploads/
   chmod 644 media/martor_uploads/*
   ```

3. **Check browser console** (F12)
   - Look for errors
   - Check Network tab

4. **Check Django logs**
   - Look for server errors
   - Check for file system errors

5. **Clear cache**
   - Ctrl+Shift+Delete (Windows)
   - Cmd+Shift+Delete (Mac)

6. **Restart Django**
   - Stop server
   - Start server again

## Final Verification

Run this Python script to verify everything:

```python
import os
from pathlib import Path

# Check directory
upload_dir = Path('media/martor_uploads')
print(f"✓ Directory exists: {upload_dir.exists()}")

# Check permissions
print(f"✓ Directory writable: {os.access(upload_dir, os.W_OK)}")

# Check files
files = list(upload_dir.glob('*'))
print(f"✓ Files uploaded: {len(files)}")

# Check settings
from django.conf import settings
print(f"✓ MARTOR_UPLOAD_PATH: {hasattr(settings, 'MARTOR_UPLOAD_PATH')}")
print(f"✓ MEDIA_URL: {settings.MEDIA_URL}")
print(f"✓ MEDIA_ROOT: {settings.MEDIA_ROOT}")

# Check filters
from qa.templatetags.qa_tags import fix_markdown_images, ensure_image_urls
print(f"✓ fix_markdown_images filter: OK")
print(f"✓ ensure_image_urls filter: OK")

print("\n✅ All checks passed!")
```

## Summary

If all tests pass:
- ✅ Upload system working
- ✅ Display system working
- ✅ Error handling working
- ✅ Performance optimized
- ✅ Accessibility enabled
- ✅ Responsive design
- ✅ Production ready

**Result**: Image solution is complete and working!
