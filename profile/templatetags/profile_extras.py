from django import template
from django.db.models import Sum
from qa.models import QUpvote, QDownvote, Answer

register = template.Library()

@register.filter
def is_teacher_verified(user):
    """Check if user is a verified teacher with @khwopa.edu.np email"""
    if hasattr(user, 'profile'):
        return (user.profile.user_type == 'Teacher' and 
                user.profile.is_verified and 
                user.email.endswith('@khwopa.edu.np'))
    return False

@register.inclusion_tag('profile/verification_badge.html')
def show_verification_badge(user):
    """Display verification badge for verified teachers"""
    is_verified = False
    if hasattr(user, 'profile'):
        is_verified = (user.profile.user_type == 'Teacher' and 
                      user.profile.is_verified and 
                      user.email.endswith('@khwopa.edu.np'))
    return {'is_verified': is_verified}

@register.filter
def calculate_reputation(user):
    """
    Calculate user's total reputation based on:
    - Question upvotes/downvotes
    - Answer upvotes/downvotes
    - Accepted answers
    """
    if not user.is_authenticated:
        return 0
        
    reputation = 0
    
    # Calculate from questions
    question_upvotes = QUpvote.objects.filter(upvote_question_of__post_owner=user).count()
    question_downvotes = QDownvote.objects.filter(downvote_question_of__post_owner=user).count()
    
    # Calculate from answers
    answer_upvotes = 0
    answer_downvotes = 0
    
    # Get all answers by the user and count their votes
    user_answers = Answer.objects.filter(answer_owner=user)
    for answer in user_answers:
        answer_upvotes += answer.a_vote_ups.count()
        answer_downvotes += answer.a_vote_downs.count()
    
    # Calculate from accepted answers
    accepted_answers = Answer.objects.filter(answer_owner=user, accepted=True).count()
    
    # Reputation calculation
    reputation += question_upvotes * 5      # +5 for each question upvote
    reputation -= question_downvotes * 2    # -2 for each question downvote
    reputation += answer_upvotes * 10       # +10 for each answer upvote
    reputation -= answer_downvotes * 2      # -2 for each answer downvote
    reputation += accepted_answers * 15     # +15 for each accepted answer
    
    # Ensure reputation doesn't go below 1
    return max(1, reputation)
