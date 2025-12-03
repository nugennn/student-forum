from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from taggit.models import Tag
import datetime
from django.utils import timezone
from datetime import timedelta
from .models import TagBadge
from qa.models import Question

def badges(request):
    tags_list = TagBadge.objects.filter(preBuild=True).exclude(awarded_to_user__isnull=False)
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(tags_list, 15)  # Show 15 badges per page
    
    try:
        tags = paginator.page(page)
    except PageNotAnInteger:
        tags = paginator.page(1)
    except EmptyPage:
        tags = paginator.page(paginator.num_pages)

    recentsEarned_badges = TagBadge.objects.filter(preBuild=False).order_by('-date')

    context = {
        'tags': tags,
        'recentsEarned_badges': recentsEarned_badges,
    }
    return render(request, 'tagbadge/badges.html', context)

# It will show only tags which are posted by user_id
def taggedItems(request, tag_id, user_id):
    tag = Tag.objects.get(id=tag_id)

    getAllQuestions = Question.objects.filter(post_owner=user_id, tags=tag)

    context = {'tag':tag,'getAllQuestions':getAllQuestions,}
    return render(request, 'profile/taggedItems_ofUser.html', context)


def taggedItemsFrom_All(request, tag_id):
    tag = Tag.objects.get(id=tag_id)

    questions = Question.objects.filter(tags=tag)

    context = {'tag':tag,'questions':questions,'count_questions':questions.count()}
    return render(request, 'qa/taggedItemsFrom_All.html', context)

