from django import template
from qa.models import Reputation,Question,BookmarkQuestion,Answer
from django.db.models import Count,BooleanField, ExpressionWrapper, Q,Exists, OuterRef,Avg, Min,Max, Sum,F, IntegerField, FloatField,Case, Value, When
from tagbadge.models import TagBadge
from django.utils import timezone
from datetime import timedelta
import re

register = template.Library()

"""This template tag is now useless, Because i built this for-
ordering items in loop without having multiple queries in rendering view
but it was showing "Duplicate results", so i decided
to build every query in view instead of using this.
Not Working -- Never used in any of app's templates.
"""
@register.filter
def sort_by(queryset, order):
    return queryset.order_by(order)
    # Tried "return queryset.distinct().order_by(order)" But it was still showing duplicate items.

@register.filter
def percentage(value):
    return format(100*value/10)

@register.filter
def advanced_percentage(queryset, from_how_much):
    return format(100*queryset/from_how_much)

@register.filter
def advanced_percentage_without_profile(from_how_much):
    return format(100*from_how_much/300)

@register.filter
def calculate_remaining_time(queryset):
    from_7_days = timezone.now() - timedelta(days=7)
    return queryset - from_7_days

"""
This template tag (calculate_reputation) is for display user's reputation in for (template) loop.
Working -- Fine
"""
@register.filter
def calculate_reputation(user_id):
    if user_id.is_authenticated:
        getAlltheReputation = Reputation.objects.filter(
                                awarded_to=user_id).aggregate(
                                    Sum('answer_rep_C'),Sum('question_rep_C'))
        Q_rep = getAlltheReputation['question_rep_C__sum']
        final_Q_Rep = getAlltheReputation['question_rep_C__sum'] if Q_rep else 0
        A_rep = getAlltheReputation['answer_rep_C__sum']
        final_A_Rep = getAlltheReputation['answer_rep_C__sum'] if A_rep else 0
        return final_Q_Rep + final_A_Rep


# It will count and show all "Gold Badges" on profile right corner.
@register.filter
def calculateGoldBadges(user_id):
    if user_id.is_authenticated:
        getAllTheGoldBadges = TagBadge.objects.filter(awarded_to_user=user_id,badge_type="GOLD").count()
        return getAllTheGoldBadges


# It will count and show all "Bronze Badges" on profile right corner.
@register.filter
def calculateBronzeBadges(user_id):
    if user_id.is_authenticated:
        getAllTheBronzeBadges = TagBadge.objects.filter(awarded_to_user=user_id,badge_type="BRONZE").count()
        return getAllTheBronzeBadges


# It will count and show all "Silver Badges" on profile right corner.
@register.filter
def calculatSilvereBadges(user_id):
    if user_id.is_authenticated:
        getAllTheSilverBadges = TagBadge.objects.filter(awarded_to_user=user_id,badge_type="SILVER").count()
        return getAllTheSilverBadges


@register.filter
def calculateEarned_Badge_Users(tag):
    countBadge = TagBadge.objects.filter(id=tag).annotate(Count('awarded_to_user'))
    return countBadge


@register.filter
def count_questions_by_tag(user_id,tag):
    count_questions = Question.objects.filter(post_owner=user_id,tags=tag).count()
    return count_questions


@register.filter
def count_questions_by_tag_without_user(tag):
    count_questions_by_tagUser = Question.objects.filter(tags=tag).count()
    return count_questions_by_tagUser


@register.filter
def count_all_bookmarkers(user_id):
    countBookmarks = BookmarkQuestion.objects.filter(bookmarked_by=user_id).count()
    return countBookmarks

@register.filter
def count_answers_by_user(user_id):
    countAnswers = Answer.objects.filter(answer_owner=user_id).count()
    return countAnswers

@register.filter
def count_questions_by_user(user_id):
    countQuestions = Question.objects.filter(post_owner=user_id).count()
    return countQuestions

@register.filter
def count_questions_all():
    counted_question_from_all = Question.objects.filter(is_deleted=False).count()
    return counted_question_from_all

# I don't know why but it is not working and will cover in next update.
@register.filter
def count_question_from_tag(tag):
    count_questions_from_tag = Question.objects.filter(tags__name__icontains=tag)
    return count_questions_from_tag.count()

@register.filter
def fix_markdown_images(html_content):
    """
    Fix markdown image URLs by ensuring they point to /media/martor_uploads/.
    Handles various image URL formats and ensures consistent display.
    """
    if not html_content:
        return html_content
    
    # Fix image src attributes - convert relative paths to proper media URLs
    def fix_img_src(match):
        img_tag = match.group(0)
        src_match = re.search(r'src=["\']([^"\']+)["\']', img_tag)
        
        if not src_match:
            return img_tag
        
        src = src_match.group(1)
        original_src = src
        
        # Skip if it's a data URL or external URL
        if src.startswith('data:') or src.startswith('http://') or src.startswith('https://'):
            return img_tag
        
        # If already has correct /media/martor_uploads/ path, return as is
        if src.startswith('/media/martor_uploads/'):
            return img_tag
        
        # If has /media/ but not martor_uploads, fix it
        if src.startswith('/media/'):
            # Check if it's already a martor upload
            if 'martor_uploads' not in src:
                # Extract filename and rebuild path
                filename = src.split('/')[-1]
                src = f'/media/martor_uploads/{filename}'
        # If relative path without /media/
        elif not src.startswith('/'):
            # Check if it looks like a martor upload filename
            if '_' in src and '.' in src:  # Likely a martor upload (has timestamp_uuid_name format)
                src = f'/media/martor_uploads/{src}'
            else:
                src = f'/media/{src}'
        else:
            # Absolute path without /media/
            src = f'/media{src}'
        
        # Replace src in the img tag
        new_img_tag = img_tag.replace(original_src, src)
        
        # Add error handling and fallback styling
        if 'onerror' not in new_img_tag:
            new_img_tag = new_img_tag.replace('>', ' onerror="this.style.display=\'none\'" />', 1)
        
        return new_img_tag
    
    # Find and fix all img tags
    html_content = re.sub(r'<img[^>]*/?>', fix_img_src, html_content)
    
    # Clean up any double slashes in media paths
    html_content = html_content.replace('/media//media/', '/media/')
    html_content = html_content.replace('/media//', '/media/')
    html_content = html_content.replace('/media/martor_uploads//', '/media/martor_uploads/')
    
    return html_content


@register.filter
def ensure_image_urls(html_content):
    """
    Additional filter to ensure all image URLs are properly formatted.
    Use this as a fallback or in combination with fix_markdown_images.
    """
    if not html_content:
        return html_content
    
    # Find all img tags and ensure they have proper src attributes
    def ensure_img_src(match):
        img_tag = match.group(0)
        
        # Check if img tag has src attribute
        if 'src=' not in img_tag:
            return ''  # Remove img tags without src
        
        # Extract src value
        src_match = re.search(r'src=["\']([^"\']+)["\']', img_tag)
        if not src_match:
            return ''  # Remove img tags without valid src
        
        src = src_match.group(1)
        
        # If src is empty or just whitespace, remove the img tag
        if not src or src.isspace():
            return ''
        
        # If src doesn't contain /media/, it's likely a broken/invalid image
        if '/media/' not in src:
            return ''
        
        # Add loading="lazy" for better performance
        if 'loading=' not in img_tag:
            img_tag = img_tag.replace('>', ' loading="lazy">', 1)
        
        # Add alt text if missing
        if 'alt=' not in img_tag:
            img_tag = img_tag.replace('>', ' alt="Image">', 1)
        
        return img_tag
    
    html_content = re.sub(r'<img[^>]*/?>', ensure_img_src, html_content)
    
    return html_content