from .models import SiteLogo, Contact
from useraccess.models import UserProfile

def active_logo(request):
    logo = SiteLogo.objects.filter(is_active=True).first()
    return {'active_logo': logo}


def user_profile_picture(request):
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            return {'pic': profile}
        except UserProfile.DoesNotExist:
            return {'pic': None}
    return {'pic': None}


def messages_count(request):
	texts = Contact.objects.filter(read=False).count()
	unread = Contact.objects.filter(read=False).order_by('-create_at')
	return {'texts': texts, 'unread': unread}