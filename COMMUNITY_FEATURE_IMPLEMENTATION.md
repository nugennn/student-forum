# Community Feature Implementation

## Overview
The Community feature allows users to organize discussions into communities, enabling better content organization and community engagement. Users can create communities, join communities of interest, and post questions to specific communities.

## Features Implemented

### 1. **Create Community**
- Users can create new communities from the "Create Community" button on the discussions page
- Communities have:
  - Name (unique, required)
  - Description (with rich text editor)
  - Icon (optional image)
  - Banner (optional image)
  - Private/Public toggle
- Creator automatically becomes admin of the community

### 2. **Browse Communities**
- Dedicated community listing page at `/community/`
- Search functionality to find communities by name or description
- Community cards showing:
  - Community icon/banner
  - Name and description preview
  - Member count
  - Join/View buttons
- Pagination for large community lists

### 3. **Community Details & Preview**
- View community information without joining
- See community description and guidelines
- View recent members
- Join button for non-members
- Leave button for members
- Admin options for community creators

### 4. **Join/Leave Communities**
- Users can join public communities with one click
- Leave communities anytime (except last admin cannot leave)
- Automatic member count updates
- Join status tracking

### 5. **My Communities**
- Personal dashboard at `/community/my-communities/`
- View all communities user has joined
- Quick access to community details

### 6. **Community Members**
- View all community members
- See member roles (Admin, Moderator, Member)
- See join dates
- Pagination for large member lists

### 7. **Post Questions to Communities**
- New community selection field in question creation form
- Users can select from their joined communities
- Community selection is optional
- Questions can be filtered by community

## Database Models

### Community
```python
- name (CharField, unique)
- slug (SlugField, unique)
- description (MartorField - rich text)
- icon (ImageField, optional)
- banner (ImageField, optional)
- creator (ForeignKey to User)
- created_at (DateTimeField)
- updated_at (DateTimeField)
- member_count (IntegerField)
- is_private (BooleanField)
- is_active (BooleanField)
```

### CommunityMember
```python
- community (ForeignKey to Community)
- user (ForeignKey to User)
- role (CharField: admin, moderator, member)
- joined_at (DateTimeField)
- is_active (BooleanField)
```

### CommunityCategory
```python
- name (CharField, unique)
- slug (SlugField, unique)
- description (TextField)
- icon (CharField - Font Awesome class)
```

### Question (Updated)
```python
- community (ForeignKey to Community, optional)
```

## API Endpoints

### Community Management
- `GET /community/` - List all communities
- `GET /community/my-communities/` - View user's joined communities
- `GET /community/create/` - Create community form
- `POST /community/create/` - Create new community
- `GET /community/<slug>/` - View community details
- `GET /community/<slug>/members/` - View community members

### Community Membership
- `POST /community/<slug>/join/` - Join community
- `POST /community/<slug>/leave/` - Leave community

## Templates

### Community Templates
- `templates/community/community_list.html` - Browse all communities
- `templates/community/community_detail.html` - View community details
- `templates/community/create_community.html` - Create community form
- `templates/community/my_communities.html` - User's communities
- `templates/community/community_members.html` - Community members list

### Modified Templates
- `templates/qa/Questions_List.html` - Added "Create Community" button
- `templates/qa/new_question.html` - Added community selection field

## File Structure

```
community/
├── __init__.py
├── models.py           # Community, CommunityMember, CommunityCategory
├── views.py            # All community views
├── forms.py            # CommunityForm
├── urls.py             # URL routing
├── admin.py            # Admin interface
├── apps.py             # App configuration
└── migrations/
    └── 0001_initial.py # Initial migration

templates/community/
├── community_list.html
├── community_detail.html
├── create_community.html
├── my_communities.html
└── community_members.html
```

## Key Features

### 1. Community Discovery
- Browse all communities
- Search by name or description
- See member counts and recent activity
- Preview before joining

### 2. Community Management
- Create communities with rich descriptions
- Customize with icons and banners
- Set privacy levels
- Track member count

### 3. User Engagement
- Join communities of interest
- View community guidelines
- See community members
- Post questions to communities

### 4. Content Organization
- Questions can be organized by community
- Better content discovery
- Topic-specific discussions
- Community-focused engagement

## Security Features

- `@login_required` on all views
- CSRF protection on all POST requests
- User authorization checks
- Community membership validation
- Admin-only operations protected

## Styling

- Modern card-based UI
- Responsive design (mobile-friendly)
- Gradient backgrounds
- Smooth transitions and hover effects
- Consistent with existing KHEC Forum theme

## Usage Examples

### Create a Community
1. Click "+ Create Community" button on discussions page
2. Fill in community name, description, icon, and banner
3. Click "Create Community"
4. You become the admin automatically

### Join a Community
1. Go to Communities page (`/community/`)
2. Browse or search for communities
3. Click "Join" button on community card
4. You're now a member!

### Post Question to Community
1. Click "Ask Question"
2. Fill in title, body, and tags
3. Select a community from the dropdown (optional)
4. Submit question
5. Question appears in community feed

### View Community Details
1. Click on community card or name
2. See description, members, and stats
3. Click "Join" to become a member
4. Access community-specific features

## Future Enhancements

- Community roles (Admin, Moderator, Member)
- Moderation tools
- Community rules/guidelines enforcement
- Community-specific tags
- Community activity feed
- Community statistics and analytics
- Invite members to communities
- Community announcements
- Community events
- Community reputation system

## Testing

All features have been tested:
- ✅ Community creation
- ✅ Community browsing
- ✅ Join/Leave functionality
- ✅ Community details view
- ✅ Member management
- ✅ Question-community association
- ✅ Search functionality
- ✅ Pagination
- ✅ Security checks
- ✅ Error handling

## Deployment Notes

1. Run migrations: `python manage.py migrate community`
2. Run migrations for qa: `python manage.py migrate qa`
3. Restart Django server
4. Community feature is ready to use!

## Support

For issues or questions about the community feature, please contact the development team.
