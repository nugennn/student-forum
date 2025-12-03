# Quick Image Upload Reference

## What Was Fixed

### Problem
Images were disappearing after upload because the upload system was unreliable.

### Solution
Implemented a **direct file system approach** with:
- Automatic directory creation
- Proper error handling
- Unique filename generation
- File validation

## How to Use

### 1. Upload an Image
- Go to "Ask a Question" page
- Scroll to "Add Media (Optional)" section
- Click file input and select an image
- Image uploads automatically
- URL appears in the form

### 2. Image URL Format
```
/media/martor_uploads/20251202_211500_a1b2c3d4_image.jpg
```

### 3. Supported Formats
- **Images**: JPG, PNG, GIF, WebP
- **Documents**: PDF, DOC, DOCX, TXT

### 4. File Size Limit
- **Maximum**: 5MB per file

## Configuration

### Directory
```
media/martor_uploads/  ← All uploads go here
```

### Settings
```python
# main/settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MARTOR_UPLOAD_PATH = 'martor_uploads/'
```

### URL Route
```python
# qa/urls.py
path('martor/uploader/', views.martor_upload_image, name='markdown_uploader')
```

## If Images Still Don't Show

### Step 1: Check Directory Exists
```bash
# Directory should exist
media/martor_uploads/
```

### Step 2: Check File Was Saved
```bash
# Files should be in this directory
ls media/martor_uploads/
```

### Step 3: Check URL in Browser
```
http://localhost:8000/media/martor_uploads/filename.jpg
```

### Step 4: Check Browser Console
- Open DevTools (F12)
- Look for 404 errors
- Check Network tab for failed requests

### Step 5: Check Django Logs
- Look for error messages in console
- Check for file system permission errors

## Common Issues

### Issue: "File size exceeds 5MB limit"
**Solution**: Upload a smaller file (under 5MB)

### Issue: "File type .xyz not allowed"
**Solution**: Use supported formats (jpg, png, gif, pdf, doc, docx, txt)

### Issue: 404 Not Found
**Solution**: 
1. Check file exists in `media/martor_uploads/`
2. Check URL is correct
3. Check Django is serving media files

### Issue: Permission Denied
**Solution**:
1. Check directory permissions: `chmod 755 media/martor_uploads/`
2. Check file permissions: `chmod 644 media/martor_uploads/*`

## Testing

### Test Upload via Browser
1. Go to "Ask a Question"
2. Scroll to "Add Media"
3. Select an image
4. Check console for success message

### Test URL Access
1. Copy image URL from upload response
2. Paste in browser address bar
3. Image should display

### Test File System
```bash
# Check if directory exists
ls -la media/martor_uploads/

# Check if files are there
find media/martor_uploads/ -type f

# Check file permissions
ls -la media/martor_uploads/filename.jpg
```

## Files Modified

✅ `main/settings.py` - Added MARTOR_UPLOAD_PATH
✅ `qa/views.py` - Improved martor_upload_image()
✅ `media/martor_uploads/` - Directory created

## Key Improvements

1. **Automatic Directory Creation** - No manual setup needed
2. **Better Error Messages** - Know exactly what went wrong
3. **Unique Filenames** - Prevents file overwrites
4. **File Validation** - Size and type checking
5. **Direct File System** - No external dependencies
6. **Reliable Storage** - Files persist after upload

## Next Steps

1. Test image upload on "Ask a Question" page
2. Verify images display in questions
3. Check images persist after page reload
4. Monitor for any error messages

## Support

If images still don't show:
1. Check `IMAGE_UPLOAD_SETUP.md` for detailed info
2. Review error messages in browser console
3. Check Django server logs
4. Verify file permissions on media directory
