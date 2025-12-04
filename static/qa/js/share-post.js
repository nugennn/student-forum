/**
 * Post Share Feature
 * Handles sharing posts via multiple channels
 * Updated: 2025-12-01 - Fixed URL path for homepage sharing
 */

let currentShareData = {
    postId: null,
    postType: null,
    postUrl: null,
    postTitle: null
};

// Initialize share modal
function openShareModal(postType, postId) {
    console.log('Opening share modal for:', postType, postId);
    
    currentShareData.postType = postType;
    currentShareData.postId = postId;
    
    // Build post URL - Use /questionDetailView/ (without /qa/ prefix, same as detail page)
    const baseUrl = window.location.origin;
    if (postType === 'question') {
        currentShareData.postUrl = `${baseUrl}/questionDetailView/${postId}/`;
        // Get the question title from the page
        const titleElement = document.querySelector('h1');
        currentShareData.postTitle = titleElement ? titleElement.innerText : 'Check out this question';
    } else if (postType === 'answer') {
        // For answers, use the current question URL with anchor
        const questionId = document.querySelector('[data-question-id]')?.getAttribute('data-question-id');
        currentShareData.postUrl = `${baseUrl}/questionDetailView/${questionId}/#answer-${postId}`;
        currentShareData.postTitle = 'Check out this answer';
    }
    
    console.log('Share data set:', currentShareData);
    
    // (Modal will load recipients when opened)
    
    // Show modal
    $('#shareModal').modal('show');
}

// Share action handler
function shareAction(action) {
    switch(action) {
        case 'copy':
            copyToClipboard();
            break;
        case 'whatsapp':
            shareToWhatsApp();
            break;
        case 'facebook':
            shareToFacebook();
            break;
        case 'twitter':
            shareToTwitter();
            break;
        case 'repost':
            repostToProfile();
            break;
        case 'chat':
            $('#shareModal').modal('hide');
            $('#chatUserModal').modal('show');
            break;
        default:
            console.error('Unknown share action:', action);
    }
}

// Copy link to clipboard
function copyToClipboard() {
    const url = currentShareData.postUrl;
    
    // Use modern Clipboard API if available
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(() => {
            showToast('Link copied to clipboard!', 'success');
            $('#shareModal').modal('hide');
        }).catch(() => {
            fallbackCopyToClipboard(url);
        });
    } else {
        fallbackCopyToClipboard(url);
    }
}

// Fallback copy to clipboard for older browsers
function fallbackCopyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    
    try {
        document.execCommand('copy');
        showToast('Link copied to clipboard!', 'success');
        $('#shareModal').modal('hide');
    } catch (err) {
        showToast('Failed to copy link', 'error');
    }
    
    document.body.removeChild(textarea);
}

// Share to WhatsApp
function shareToWhatsApp() {
    const text = encodeURIComponent(`${currentShareData.postTitle}\n\n${currentShareData.postUrl}`);
    const whatsappUrl = `https://wa.me/?text=${text}`;
    window.open(whatsappUrl, '_blank', 'noopener,noreferrer');
    $('#shareModal').modal('hide');
    showToast('Opening WhatsApp...', 'success');
}

// Share to Facebook
function shareToFacebook() {
    const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(currentShareData.postUrl)}`;
    window.open(facebookUrl, '_blank', 'noopener,noreferrer');
    $('#shareModal').modal('hide');
    showToast('Opening Facebook...', 'success');
}

// Share to Twitter
function shareToTwitter() {
    const twitterUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(currentShareData.postUrl)}&text=${encodeURIComponent(currentShareData.postTitle)}`;
    window.open(twitterUrl, '_blank', 'noopener,noreferrer');
    $('#shareModal').modal('hide');
    showToast('Opening Twitter...', 'success');
}

// Repost to profile
function repostToProfile() {
    $.ajax({
        url: '/qa/repost-to-profile/',
        type: 'POST',
        data: {
            post_id: currentShareData.postId,
            post_type: currentShareData.postType,
            csrfmiddlewaretoken: getCsrfToken()
        },
        success: function(response) {
            if (response.success) {
                showToast('Posted to your profile!', 'success');
                $('#shareModal').modal('hide');
            } else {
                showToast(response.error || 'Failed to repost', 'error');
            }
        },
        error: function(error) {
            showToast('Error reposting to profile', 'error');
            console.error('Repost error:', error);
        }
    });
}

// Open chat selector modal
function openChatSelectorModal() {
    console.log('Opening chat selector. Current share data:', currentShareData);
    
    // Validate that share data is available
    if (!currentShareData.postUrl || !currentShareData.postTitle) {
        console.error('Share data not available:', currentShareData);
        alert('Error: Post data not loaded. Please try again.');
        return;
    }
    
    $('#chatSelectorModal').modal('show');
    loadChatRecipientsForModal();
}

// Close chat selector modal
function closeChatSelectorModal() {
    $('#chatSelectorModal').modal('hide');
}

// Load chat recipients for modal
function loadChatRecipientsForModal() {
    $.ajax({
        url: '/chat/get-chat-recipients/',
        type: 'GET',
        dataType: 'json',
        timeout: 5000,
        success: function(response) {
            console.log('Chat recipients loaded:', response);
            
            // Clear lists
            document.getElementById('recentChatsList').innerHTML = '';
            document.getElementById('usersList').innerHTML = '';
            document.getElementById('groupsList').innerHTML = '';
            
            // Add recent users
            if (response.users && response.users.length > 0) {
                const recentUsers = response.users.filter(u => u.recent);
                const otherUsers = response.users.filter(u => !u.recent);
                
                if (recentUsers.length > 0) {
                    recentUsers.forEach(user => {
                        const item = createUserItem(user);
                        document.getElementById('recentChatsList').appendChild(item);
                    });
                } else {
                    document.getElementById('recentChatsSection').style.display = 'none';
                }
                
                if (otherUsers.length > 0) {
                    otherUsers.forEach(user => {
                        const item = createUserItem(user);
                        document.getElementById('usersList').appendChild(item);
                    });
                }
            }
            
            // Add groups only if they exist
            if (response.groups && response.groups.length > 0) {
                response.groups.forEach(group => {
                    const item = createGroupItem(group);
                    document.getElementById('groupsList').appendChild(item);
                });
                document.getElementById('groupsSection').style.display = 'block';
            } else {
                document.getElementById('groupsSection').style.display = 'none';
            }
        },
        error: function(xhr, status, error) {
            console.error('Error loading chat recipients:', error);
            showToast('Failed to load recipients', 'error');
        }
    });
}

// Create user item
function createUserItem(user) {
    const item = document.createElement('div');
    item.setAttribute('data-user-id', user.id);
    item.setAttribute('data-recipient-name', user.name);
    item.style.cssText = 'display: flex; align-items: center; padding: 10px 12px; border: 1px solid #e8eaed; border-radius: 6px; cursor: pointer; transition: all 0.2s ease; background: #fff;';
    item.innerHTML = `
        <i class="fas fa-user" style="font-size: 16px; color: #0084ff; margin-right: 12px; width: 20px; text-align: center;"></i>
        <div style="flex: 1;">
            <div style="font-weight: 500; color: #1a1a1a; font-size: 13px;">${user.name}</div>
            <div style="font-size: 11px; color: #999;">@${user.username}</div>
        </div>
    `;
    
    item.onmouseover = () => {
        item.style.background = '#f8f9fa';
        item.style.borderColor = '#0084ff';
    };
    item.onmouseout = () => {
        item.style.background = '#fff';
        item.style.borderColor = '#e8eaed';
    };
    
    item.onclick = () => {
        console.log('User item clicked:', user.id, user.name);
        goToChatWithLink(user.id, 'user', user.name);
    };
    
    return item;
}

// Create group item
function createGroupItem(group) {
    const item = document.createElement('div');
    item.setAttribute('data-group-id', group.id);
    item.setAttribute('data-recipient-name', group.name);
    item.style.cssText = 'display: flex; align-items: center; padding: 10px 12px; border: 1px solid #e8eaed; border-radius: 6px; cursor: pointer; transition: all 0.2s ease; background: #fff;';
    item.innerHTML = `
        <i class="fas fa-users" style="font-size: 16px; color: #667eea; margin-right: 12px; width: 20px; text-align: center;"></i>
        <div style="flex: 1;">
            <div style="font-weight: 500; color: #1a1a1a; font-size: 13px;">${group.name}</div>
            <div style="font-size: 11px; color: #999;">Group Chat</div>
        </div>
    `;
    
    item.onmouseover = () => {
        item.style.background = '#f8f9fa';
        item.style.borderColor = '#667eea';
    };
    item.onmouseout = () => {
        item.style.background = '#fff';
        item.style.borderColor = '#e8eaed';
    };
    
    item.onclick = () => {
        console.log('Group item clicked:', group.id, group.name);
        goToChatWithLink(group.id, 'group', group.name);
    };
    
    return item;
}

// Go to chat with link
function goToChatWithLink(recipientId, type, recipientName) {
    // Get post data for confirmation dialog
    const postUrl = currentShareData.postUrl;
    const postTitle = currentShareData.postTitle;
    
    console.log('Share Data:', currentShareData);
    console.log('Post URL:', postUrl);
    console.log('Post Title:', postTitle);
    
    if (!postUrl || !postTitle) {
        showToast('Error: Post link not found. URL: ' + postUrl + ', Title: ' + postTitle, 'error');
        return;
    }
    
    // Use provided recipient name or fallback
    if (!recipientName) {
        recipientName = type === 'user' ? 'this user' : 'this group';
    }
    
    // Show confirmation dialog
    const confirmMessage = `Send this post to ${recipientName}?`;
    if (!confirm(confirmMessage)) {
        return;
    }
    
    // Send link message to backend
    $.ajax({
        url: '/chat/send-link/',
        type: 'POST',
        contentType: 'application/json',
        headers: {
            'X-CSRFToken': getCsrfToken()
        },
        data: JSON.stringify({
            chat_type: type === 'user' ? 'private' : 'group',
            chat_id: recipientId,
            link_url: postUrl
        }),
        success: function(response) {
            if (response.success) {
                showToast(`Post sent successfully!`, 'success');
                $('#chatSelectorModal').modal('hide');
                $('#shareModal').modal('hide');
                // Redirect to chat after a short delay
                setTimeout(() => {
                    if (type === 'user') {
                        window.location.href = `/chat/private/${recipientId}/`;
                    } else if (type === 'group') {
                        window.location.href = `/chat/group/${recipientId}/`;
                    }
                }, 800);
            } else {
                showToast(response.error || 'Failed to send', 'error');
            }
        },
        error: function(xhr, status, error) {
            console.error('Send error:', error, xhr.responseText);
            showToast('Error sending post: ' + error, 'error');
        }
    });
}

// Get CSRF token from cookie
function getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Show toast notification
function showToast(message, type = 'info') {
    const container = document.querySelector('.toast-container');
    const toast = document.createElement('div');
    toast.className = `toast-message ${type}`;
    toast.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center;">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}" style="margin-right: 12px; font-size: 18px;"></i>
                <span>${message}</span>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; cursor: pointer; color: #999; font-size: 18px;">
                ×
            </button>
        </div>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Add slideOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Search functionality for chat selector
document.addEventListener('DOMContentLoaded', function() {
    const searchBox = document.getElementById('chatSearchBox');
    if (searchBox) {
        searchBox.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            
            // Filter recent chats
            const recentItems = document.querySelectorAll('#recentChatsList > div');
            recentItems.forEach(item => {
                const name = item.getAttribute('data-recipient-name') || '';
                item.style.display = name.toLowerCase().includes(searchTerm) ? 'flex' : 'none';
            });
            
            // Filter users
            const userItems = document.querySelectorAll('#usersList > div');
            userItems.forEach(item => {
                const name = item.getAttribute('data-recipient-name') || '';
                item.style.display = name.toLowerCase().includes(searchTerm) ? 'flex' : 'none';
            });
            
            // Filter groups
            const groupItems = document.querySelectorAll('#groupsList > div');
            groupItems.forEach(item => {
                const name = item.getAttribute('data-recipient-name') || '';
                item.style.display = name.toLowerCase().includes(searchTerm) ? 'flex' : 'none';
            });
        });
    }
});
