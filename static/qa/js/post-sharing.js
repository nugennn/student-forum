/**
 * Post Sharing Functionality
 * Handles share, repost, and quote operations for posts
 * Requires csrf-helper.js to be loaded first
 */

document.addEventListener('DOMContentLoaded', function() {
    initializePostSharing();
});

function initializePostSharing() {
    // Initialize share buttons
    const shareButtons = document.querySelectorAll('[data-share-action]');
    
    shareButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const action = this.getAttribute('data-share-action');
            const postId = this.getAttribute('data-post-id');
            const postType = this.getAttribute('data-post-type'); // 'question' or 'answer'
            
            handleShareAction(action, postId, postType);
        });
    });
}

function handleShareAction(action, postId, postType) {
    switch(action) {
        case 'share':
            sharePost(postId, postType);
            break;
        case 'repost':
            repostPost(postId, postType);
            break;
        case 'quote':
            quotePost(postId, postType);
            break;
        default:
            console.error('Unknown share action:', action);
    }
}

function sharePost(postId, postType) {
    // Check if user is authenticated
    if (!isUserAuthenticated()) {
        showLoginPrompt();
        return;
    }
    
    // Send share request to server
    $.ajax({
        url: '/qa/share-post/',
        type: 'POST',
        data: {
            post_id: postId,
            post_type: postType,
            share_type: 'share'
        },
        success: function(response) {
            showNotification('Post shared successfully!', 'success');
            updateShareCount(postId, postType, 'share');
        },
        error: function(error) {
            showNotification('Error sharing post', 'error');
            console.error('Share error:', error);
        }
    });
}

function repostPost(postId, postType) {
    // Check if user is authenticated
    if (!isUserAuthenticated()) {
        showLoginPrompt();
        return;
    }
    
    // Send repost request to server
    $.ajax({
        url: '/qa/share-post/',
        type: 'POST',
        data: {
            post_id: postId,
            post_type: postType,
            share_type: 'repost'
        },
        success: function(response) {
            showNotification('Post reposted!', 'success');
            updateShareCount(postId, postType, 'repost');
        },
        error: function(error) {
            showNotification('Error reposting', 'error');
            console.error('Repost error:', error);
        }
    });
}

function quotePost(postId, postType) {
    // Check if user is authenticated
    if (!isUserAuthenticated()) {
        showLoginPrompt();
        return;
    }
    
    // Show modal for quote text
    showQuoteModal(postId, postType);
}

function showQuoteModal(postId, postType) {
    const modalHTML = `
        <div class="modal fade" id="quoteModal" tabindex="-1" role="dialog">
            <div class="modal-dialog" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Quote Post</h5>
                        <button type="button" class="close" data-dismiss="modal">
                            <span>&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <textarea id="quoteText" class="form-control" rows="4" placeholder="Add your thoughts..."></textarea>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="submitQuote('${postId}', '${postType}')">Quote</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if present
    const existingModal = document.getElementById('quoteModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Show modal
    $('#quoteModal').modal('show');
}

function submitQuote(postId, postType) {
    const quoteText = document.getElementById('quoteText').value;
    
    if (!quoteText.trim()) {
        showNotification('Please add some text to your quote', 'warning');
        return;
    }
    
    // Send quote request to server
    $.ajax({
        url: '/qa/share-post/',
        type: 'POST',
        data: {
            post_id: postId,
            post_type: postType,
            share_type: 'quote',
            quote_text: quoteText
        },
        success: function(response) {
            showNotification('Post quoted successfully!', 'success');
            $('#quoteModal').modal('hide');
            updateShareCount(postId, postType, 'quote');
        },
        error: function(error) {
            showNotification('Error quoting post', 'error');
            console.error('Quote error:', error);
        }
    });
}

function updateShareCount(postId, postType, shareType) {
    const countElement = document.querySelector(`[data-share-count="${postType}-${postId}"]`);
    if (countElement) {
        const currentCount = parseInt(countElement.textContent) || 0;
        countElement.textContent = currentCount + 1;
    }
}

function isUserAuthenticated() {
    // Check if user is authenticated (you may need to adjust this based on your template)
    return document.body.getAttribute('data-user-authenticated') === 'true';
}

function showLoginPrompt() {
    showNotification('Please log in to share posts', 'info');
    // Optionally redirect to login page
    // window.location.href = '/accounts/login/';
}

function showNotification(message, type) {
    const alertClass = `alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : type === 'warning' ? 'warning' : 'info'}`;
    const notificationHTML = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert" style="position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
            ${message}
            <button type="button" class="close" data-dismiss="alert">
                <span>&times;</span>
            </button>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', notificationHTML);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            if (alert.textContent.includes(message)) {
                alert.remove();
            }
        });
    }, 5000);
}

