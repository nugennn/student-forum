# Chat System - Quick Reference Guide

## 🚀 Quick Start

### Access Chat
1. Click **💬 Chat** button in navbar
2. View all your conversations
3. Click any chat to open it

### Send Private Message
1. Visit user's profile
2. Click **Send Message** button
3. Start typing and send

### Create Group Chat
1. Go to Chat page
2. Click **New Group** button
3. Enter name and select members
4. Group created!

---

## 📍 Navigation

| Location | Action | Result |
|----------|--------|--------|
| Navbar | Click Chat button | Go to `/chat/` |
| User Profile | Click Send Message | Open private chat |
| Chat List | Click conversation | Open chat |
| Chat List | Click New Group | Create group |

---

## 💬 Message Types

### Text
- Type message and press Send
- Supports emoji and special characters

### Image
- Click 📷 button
- Select image file
- Preview displays inline

### File
- Click 📎 button
- Select any file
- Download link provided

### Link
- Click 🔗 button
- Paste URL
- Metadata auto-extracts (title, description, image)

---

## 👥 Group Management

### Create Group
1. Chat page → New Group
2. Enter name
3. Select members
4. Create

### Add Member
1. Open group chat
2. Click Info button
3. (Creator only) Add member

### Remove Member
1. Open group chat
2. Click Info button
3. (Creator only) Click Remove

### Update Group
1. Open group chat
2. Click Info button
3. (Creator only) Change name/photo

---

## 🔔 Notifications

### Unread Badge
- Shows count on Chat button
- Updates every 30 seconds
- Click to view messages

### Message Notifications
- Auto-created when message sent
- Marked as read when chat opened
- Tracked in database

---

## 📱 Responsive Design

- ✅ Desktop (1200px+)
- ✅ Tablet (768px - 1199px)
- ✅ Mobile (< 768px)

---

## 🔒 Security

- Login required for all chats
- CSRF protection on forms
- User authorization verified
- File uploads validated

---

## ⚙️ Settings

### Database
- SQLite (default)
- PostgreSQL (production)
- MySQL (alternative)

### Media
- Images: `media/chat_images/`
- Files: `media/chat_files/`
- Photos: `media/group_chat_photos/`

### Configuration
- `MEDIA_ROOT`: Where files stored
- `MEDIA_URL`: How to access files

---

## 🐛 Troubleshooting

### Chat button not showing badge
- Clear browser cache
- Refresh page
- Check if messages unread

### Images not uploading
- Check file size
- Verify file format (jpg, png, gif)
- Check MEDIA_ROOT setting

### Link metadata not showing
- Check internet connection
- Verify URL is valid
- Try different URL

### Group creation fails
- Select at least 1 member
- Enter group name
- Check permissions

---

## 📊 Database

### Models
- `PrivateChat` - One-on-one chats
- `GroupChat` - Group chats
- `Message` - All messages
- `MessageReaction` - Emoji reactions
- `ChatNotification` - Unread tracking

### Migrations
```bash
python manage.py makemigrations chat
python manage.py migrate
```

---

## 🔌 API Reference

### Send Message
```
POST /chat/send-message/
{
  "chat_type": "private",
  "chat_id": 1,
  "content": "Hello!"
}
```

### Send Image
```
POST /chat/send-image/
FormData:
  chat_type: "private"
  chat_id: 1
  image: <file>
```

### Send Link
```
POST /chat/send-link/
{
  "chat_type": "private",
  "chat_id": 1,
  "link_url": "https://example.com"
}
```

### Create Group
```
POST /chat/create-group/
{
  "name": "My Group",
  "member_ids": [1, 2, 3]
}
```

### Get Unread Count
```
GET /chat/unread-count/
Response: {"unread_count": 5}
```

---

## 📁 File Locations

### Backend
- Models: `chat/models.py`
- Views: `chat/views.py`
- URLs: `chat/urls.py`
- Admin: `chat/admin.py`

### Frontend
- Chat List: `templates/chat/chat_list.html`
- Private Chat: `templates/chat/private_chat.html`
- Group Chat: `templates/chat/group_chat.html`

### Configuration
- Settings: `main/settings.py`
- URLs: `main/urls.py`

---

## 🎯 Features

### Private Chat
- ✅ One-on-one messaging
- ✅ Message history
- ✅ Media sharing
- ✅ Unread tracking

### Group Chat
- ✅ Multi-user messaging
- ✅ Member management
- ✅ Group customization
- ✅ Media sharing

### Media
- ✅ Image preview
- ✅ File download
- ✅ Link metadata
- ✅ Inline display

### UI
- ✅ Chat list
- ✅ Message view
- ✅ Member list
- ✅ Responsive design

---

## 💡 Tips & Tricks

1. **Quick Access**: Bookmark `/chat/` for quick access
2. **Mobile**: Use mobile-friendly view for better experience
3. **Links**: Paste URLs to auto-extract metadata
4. **Groups**: Creator can manage all members
5. **Notifications**: Check badge regularly for new messages

---

## 📞 Support

### Documentation
- Full guide: `CHAT_SYSTEM_IMPLEMENTATION.md`
- Overview: `IMPLEMENTATION_SUMMARY.md`
- Status: `CHAT_DEPLOYMENT_STATUS.md`

### Common Issues
- See CHAT_SYSTEM_IMPLEMENTATION.md → Troubleshooting
- Check Django logs for errors
- Verify database migrations applied

---

## ✅ Checklist

Before going live:
- [ ] Dependencies installed
- [ ] Migrations applied
- [ ] Static files collected
- [ ] Media folder created
- [ ] Settings configured
- [ ] URLs included
- [ ] Templates in place
- [ ] Server tested

---

**Version**: 1.0  
**Last Updated**: November 23, 2025  
**Status**: ✅ Production Ready
