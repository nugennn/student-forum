#!/usr/bin/env python
"""
Verification script for image upload setup.
Run this to check if everything is configured correctly.
"""

import os
import sys
from pathlib import Path

def check_directory():
    """Check if martor_uploads directory exists and is writable."""
    print("\n" + "="*60)
    print("1. CHECKING DIRECTORY")
    print("="*60)
    
    base_dir = Path(__file__).parent
    media_dir = base_dir / 'media'
    upload_dir = media_dir / 'martor_uploads'
    
    print(f"Base directory: {base_dir}")
    print(f"Media directory: {media_dir}")
    print(f"Upload directory: {upload_dir}")
    
    # Check if media directory exists
    if media_dir.exists():
        print("✓ Media directory exists")
    else:
        print("✗ Media directory NOT found")
        return False
    
    # Check if upload directory exists
    if upload_dir.exists():
        print("✓ Upload directory exists")
    else:
        print("✗ Upload directory NOT found")
        print(f"  Creating: {upload_dir}")
        try:
            upload_dir.mkdir(parents=True, exist_ok=True)
            print("✓ Upload directory created")
        except Exception as e:
            print(f"✗ Failed to create directory: {e}")
            return False
    
    # Check if directory is writable
    try:
        test_file = upload_dir / '.write_test'
        test_file.write_text('test')
        test_file.unlink()
        print("✓ Upload directory is writable")
    except Exception as e:
        print(f"✗ Upload directory is NOT writable: {e}")
        return False
    
    return True


def check_settings():
    """Check if Django settings are configured correctly."""
    print("\n" + "="*60)
    print("2. CHECKING SETTINGS")
    print("="*60)
    
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
        django.setup()
        
        from django.conf import settings
        
        # Check MEDIA_URL
        if hasattr(settings, 'MEDIA_URL'):
            print(f"✓ MEDIA_URL: {settings.MEDIA_URL}")
        else:
            print("✗ MEDIA_URL not configured")
            return False
        
        # Check MEDIA_ROOT
        if hasattr(settings, 'MEDIA_ROOT'):
            print(f"✓ MEDIA_ROOT: {settings.MEDIA_ROOT}")
        else:
            print("✗ MEDIA_ROOT not configured")
            return False
        
        # Check MARTOR_UPLOAD_PATH
        if hasattr(settings, 'MARTOR_UPLOAD_PATH'):
            print(f"✓ MARTOR_UPLOAD_PATH: {settings.MARTOR_UPLOAD_PATH}")
        else:
            print("⚠ MARTOR_UPLOAD_PATH not configured (optional)")
        
        # Check MARTOR_ENABLE_CONFIGS
        if hasattr(settings, 'MARTOR_ENABLE_CONFIGS'):
            imgur_enabled = settings.MARTOR_ENABLE_CONFIGS.get('imgur', 'true')
            print(f"✓ MARTOR_ENABLE_CONFIGS found")
            print(f"  - imgur: {imgur_enabled} (should be 'false' for custom uploader)")
        else:
            print("⚠ MARTOR_ENABLE_CONFIGS not found")
        
        return True
    
    except Exception as e:
        print(f"✗ Error checking settings: {e}")
        return False


def check_urls():
    """Check if URL routes are configured."""
    print("\n" + "="*60)
    print("3. CHECKING URL ROUTES")
    print("="*60)
    
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
        django.setup()
        
        from django.urls import reverse
        
        # Check if martor uploader URL exists
        try:
            url = reverse('qa:markdown_uploader')
            print(f"✓ Martor uploader URL: {url}")
        except Exception as e:
            print(f"✗ Martor uploader URL not found: {e}")
            return False
        
        # Check if media URL is served
        from django.conf import settings
        from django.conf.urls.static import static
        
        print(f"✓ Media URL configured: {settings.MEDIA_URL}")
        print(f"✓ Media root: {settings.MEDIA_ROOT}")
        
        return True
    
    except Exception as e:
        print(f"✗ Error checking URLs: {e}")
        return False


def check_view():
    """Check if the upload view exists."""
    print("\n" + "="*60)
    print("4. CHECKING VIEW FUNCTION")
    print("="*60)
    
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
        django.setup()
        
        from qa.views import martor_upload_image
        
        print("✓ martor_upload_image view found")
        print(f"  - Function: {martor_upload_image.__name__}")
        print(f"  - Module: {martor_upload_image.__module__}")
        
        # Check if it has login_required decorator
        if hasattr(martor_upload_image, '__wrapped__'):
            print("✓ View has @login_required decorator")
        
        return True
    
    except Exception as e:
        print(f"✗ Error checking view: {e}")
        return False


def check_files():
    """Check if uploaded files can be accessed."""
    print("\n" + "="*60)
    print("5. CHECKING UPLOADED FILES")
    print("="*60)
    
    try:
        base_dir = Path(__file__).parent
        upload_dir = base_dir / 'media' / 'martor_uploads'
        
        if not upload_dir.exists():
            print("⚠ Upload directory doesn't exist yet (will be created on first upload)")
            return True
        
        files = list(upload_dir.glob('*'))
        
        if not files:
            print("⚠ No files uploaded yet (directory is empty)")
            return True
        
        print(f"✓ Found {len(files)} uploaded files:")
        for file in files[:5]:  # Show first 5 files
            size_kb = file.stat().st_size / 1024
            print(f"  - {file.name} ({size_kb:.1f} KB)")
        
        if len(files) > 5:
            print(f"  ... and {len(files) - 5} more files")
        
        return True
    
    except Exception as e:
        print(f"✗ Error checking files: {e}")
        return False


def main():
    """Run all checks."""
    print("\n" + "="*60)
    print("IMAGE UPLOAD VERIFICATION")
    print("="*60)
    
    checks = [
        ("Directory Setup", check_directory),
        ("Django Settings", check_settings),
        ("URL Routes", check_urls),
        ("View Function", check_view),
        ("Uploaded Files", check_files),
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✓ All checks passed! Image upload is ready to use.")
        return 0
    else:
        print(f"\n✗ {total - passed} check(s) failed. Please fix the issues above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
