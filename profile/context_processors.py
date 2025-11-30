from django.shortcuts import render, redirect
import datetime
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Count, Min, Sum, Q
from qa.models import Question
from notification.models import PrivRepNotification, Notification
from chat.models import Message
from community.models import Community

def top_questions(request):
	questionsHome = Question.objects.filter(
							is_deleted=False, is_bountied=False).order_by(
							'-date')[:50]
	return {
			'questionsHome':questionsHome
		}

def count_all_bounties(request):
	bounties = Question.objects.filter(is_bountied=True)

	return {
		'count_bounty': bounties.count()
	}

def count_unread_chat_messages(request):
	unread_messages = Message.objects.filter(read=False, recipient=request.user).count()
	return {
		'unread_messages': unread_messages
	}

def user_communities(request):
	"""Add user's joined communities to all templates"""
	if request.user.is_authenticated:
		communities = Community.objects.filter(members__user=request.user).order_by('name')
		return {
			'communities': communities
		}
	return {
		'communities': []
	}