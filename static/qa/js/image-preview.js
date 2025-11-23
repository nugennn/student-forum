/**
 * Image Preview Functionality for Post Forms
 * Displays image previews before form submission
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize image preview for file inputs
    initializeImagePreview();
});

function initializeImagePreview() {
    // Find all file inputs in the document
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        // Create a preview container if it doesn't exist
        if (!input.nextElementSibling || !input.nextElementSibling.classList.contains('image-preview-container')) {
            const previewContainer = document.createElement('div');
            previewContainer.className = 'image-preview-container';
            previewContainer.style.cssText = `
                margin-top: 12px;
                display: none;
                padding: 12px;
                background: #f1f5f9;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
            `;
            input.parentNode.insertBefore(previewContainer, input.nextSibling);
        }
        
        // Add change event listener
        input.addEventListener('change', function(e) {
            handleImagePreview(e, input);
        });
    });
    
    // Also handle Martor image uploads
    handleMartorImagePreview();
}

function handleImagePreview(event, fileInput) {
    const files = event.target.files;
    const previewContainer = fileInput.nextElementSibling;
    
    if (!previewContainer || !previewContainer.classList.contains('image-preview-container')) {
        return;
    }
    
    // Clear previous previews
    previewContainer.innerHTML = '';
    previewContainer.style.display = 'none';
    
    if (files.length === 0) {
        return;
    }
    
    // Create preview for each image
    Array.from(files).forEach((file, index) => {
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                const previewItem = document.createElement('div');
                previewItem.className = 'image-preview-item';
                previewItem.style.cssText = `
                    margin-bottom: 12px;
                    text-align: center;
                `;
                
                const img = document.createElement('img');
                img.src = e.target.result;
                img.style.cssText = `
                    max-width: 100%;
                    max-height: 300px;
                    border-radius: 6px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                `;
                
                const fileName = document.createElement('p');
                fileName.textContent = file.name;
                fileName.style.cssText = `
                    margin-top: 8px;
                    font-size: 13px;
                    color: #64748b;
                    word-break: break-all;
                `;
                
                const fileSize = document.createElement('p');
                fileSize.textContent = formatFileSize(file.size);
                fileSize.style.cssText = `
                    margin: 4px 0 0 0;
                    font-size: 12px;
                    color: #94a3b8;
                `;
                
                previewItem.appendChild(img);
                previewItem.appendChild(fileName);
                previewItem.appendChild(fileSize);
                previewContainer.appendChild(previewItem);
            };
            
            reader.readAsDataURL(file);
        }
    });
    
    // Show preview container
    if (previewContainer.children.length > 0) {
        previewContainer.style.display = 'block';
    }
}

function handleMartorImagePreview() {
    // Monitor Martor's image upload functionality
    // This handles images uploaded through the Martor editor
    
    // Check if Martor is loaded
    if (typeof $ !== 'undefined' && $.fn.martor) {
        // Martor uses AJAX for image uploads
        // We'll intercept the upload success to show preview
        
        document.addEventListener('martor:imageInserted', function(e) {
            // Image was inserted into the editor
            // The preview is already shown in the editor
            console.log('Image inserted into editor');
        });
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Re-initialize preview when new file inputs are added dynamically
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.addedNodes.length) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) { // Element node
                    if (node.tagName === 'INPUT' && node.type === 'file') {
                        // New file input added
                        const previewContainer = document.createElement('div');
                        previewContainer.className = 'image-preview-container';
                        previewContainer.style.cssText = `
                            margin-top: 12px;
                            display: none;
                            padding: 12px;
                            background: #f1f5f9;
                            border-radius: 8px;
                            border: 1px solid #e2e8f0;
                        `;
                        node.parentNode.insertBefore(previewContainer, node.nextSibling);
                        
                        node.addEventListener('change', function(e) {
                            handleImagePreview(e, node);
                        });
                    }
                }
            });
        }
    });
});

// Start observing the document for changes
observer.observe(document.body, {
    childList: true,
    subtree: true
});
