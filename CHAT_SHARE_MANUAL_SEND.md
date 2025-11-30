# Send via Chat - Manual Link Sharing ✅

## Overview

Users can now select a user or group chat from a dropdown, then manually paste the post link in the chat before sending.

---

## Features

### 1. **Smart Dropdown with Optgroups**

**Recent Users** (at top, sorted by most recent message)
- Shows users you've recently chatted with
- Sorted by most recent message timestamp
- Appears first for quick access

**All Other Users**
- Shows all users except those in Recent
- Excludes current user
- Alphabetically organized

**Group Chats** (only if you have any)
- Shows groups you're a member of
- Only displayed if groups exist
- No empty optgroup if no groups

### 2. **Manual Send Flow**

```
1. User clicks "Send via Chat" button in Share modal
2. Dropdown loads with recent users, all users, and groups
3. User selects a user or group
4. User clicks "Go to Chat" button
5. Redirects to chat page with link in URL parameters
6. User manually pastes link in message input
7. User clicks Send in chat
```

### 3. **URL Parameters**

When redirecting to chat, link is passed as URL parameters:
```
/chat/private/123/?link=https://...&title=Post%20Title
/chat/group/456/?link=https://...&title=Post%20Title
```

---

## Backend Changes

### `chat/views.py` - `get_chat_recipients()`

**Recent Users Logic:**
- Queries PrivateChat objects for current user
- Annotates with most recent message timestamp
- Orders by `-last_message` (newest first)
- Limits to 20 recent chats
- Extracts other participant from each chat
- Marks with `recent: True`

**Other Users:**
- Gets all users except current user
- Excludes users already in recent list
- Marks with `recent: False`

**Group Chats:**
- Filters GroupChat by current user membership
- Only returned if any exist
- Returns id, name, type

**Response Format:**
```json
{
    "users": [
        {"id": "user_1", "type": "user", "name": "John", "username": "john", "recent": true},
        {"id": "user_2", "type": "user", "name": "Jane", "username": "jane", "recent": false}
    ],
    "groups": [
        {"id": "group_5", "type": "group", "name": "Study Group"}
    ]
}
```

---

## Frontend Changes

### `templates/partials/share_modal.html`

**Send via Chat Section:**
- Dropdown with id `chatRecipientSelect`
- "Go to Chat" button calls `goToChatWithLink()`
- Displays optgroups: Recent, Users, Group Chats

### `static/qa/js/share-post.js`

**New Functions:**

1. **`loadChatRecipients()`**
   - Fetches from `/chat/get-chat-recipients/`
   - Separates recent and other users
   - Creates optgroups dynamically
   - Only shows Group Chats optgroup if groups exist

2. **`goToChatWithLink()`**
   - Gets selected value from dropdown
   - Parses user_ID or group_ID format
   - Redirects to appropriate chat page
   - Passes link and title as URL parameters

---

## User Experience

### Step 1: Open Share Modal
```
Click Share button on question/answer
```

### Step 2: Select Recipient
```
Dropdown shows:
- Recent (John, Jane, Bob)
- Users (Alice, Charlie, David)
- Group Chats (Study Group, Project Team)
```

### Step 3: Click "Go to Chat"
```
Redirects to chat page with link in URL
```

### Step 4: Paste Link Manually
```
Link appears in message input (if implemented in chat template)
User can edit or add text
User clicks Send
```

---

## Data Flow

```
Share Modal Opens
    ↓
loadChatRecipients() called
    ↓
GET /chat/get-chat-recipients/
    ↓
Backend queries:
  - Recent chats (PrivateChat with messages)
  - All other users
  - Group chats (if any)
    ↓
Returns JSON with users and groups
    ↓
JavaScript creates optgroups:
  - Recent (if any)
  - Users
  - Group Chats (only if exist)
    ↓
Dropdown populated and ready
    ↓
User selects recipient
    ↓
User clicks "Go to Chat"
    ↓
goToChatWithLink() called
    ↓
Redirects to /chat/private/ID/?link=...
    or /chat/group/ID/?link=...
    ↓
Chat page loads with link in URL
    ↓
User manually pastes link in message
    ↓
User sends message
```

---

## Dropdown Display

### With Recent Chats:
```
Select user or group...

Recent
  John Doe
  Jane Smith
  Bob Johnson

Users
  Alice Brown
  Charlie Davis
  David Evans

Group Chats
  Study Group
  Project Team
```

### Without Recent Chats:
```
Select user or group...

Users
  Alice Brown
  Charlie Davis
  David Evans

Group Chats
  Study Group
  Project Team
```

### Without Group Chats:
```
Select user or group...

Recent
  John Doe
  Jane Smith

Users
  Alice Brown
  Charlie Davis
```

---

## Implementation Details

### Recent Chat Sorting
- Uses `Max('messages__created_at')` to find most recent message
- Orders by `-last_message` (descending)
- Limits to 20 most recent
- Ensures users you chat with most appear first

### Group Chat Filtering
- Only shows groups where user is a member
- Uses `GroupChat.objects.filter(members=request.user)`
- Empty if user has no groups
- Optgroup not displayed if no groups

### URL Parameter Encoding
- Link URL: `encodeURIComponent(postUrl)`
- Title: `encodeURIComponent(postTitle)`
- Prevents URL breaking with special characters

---

## Error Handling

**No Recent Chats:**
- Recent optgroup not created
- Users optgroup shown instead

**No Group Chats:**
- Group Chats optgroup not created
- Only Users optgroup shown

**No Selection:**
- Toast error: "Please select a user or group"
- Prevents redirect

**Backend Error:**
- Toast error: "Failed to load recipients"
- Dropdown remains empty

---

## Files Modified

### Backend
- `chat/views.py` - Updated `get_chat_recipients()`

### Frontend
- `templates/partials/share_modal.html` - Updated Send via Chat section
- `static/qa/js/share-post.js` - New functions, updated openShareModal

---

## Status: ✅ COMPLETE

The "Send via Chat" feature now:
- ✅ Shows recent users at top (sorted by most recent)
- ✅ Shows all other users below
- ✅ Shows group chats (only if they exist)
- ✅ Uses dropdown with optgroups
- ✅ Manual send (user pastes link manually)
- ✅ Redirects to chat page with link in URL
- ✅ Proper error handling

**Ready for production use.**
