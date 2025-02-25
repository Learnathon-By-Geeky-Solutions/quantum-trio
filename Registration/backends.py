# custom authenticate function for both user and shop login
from django.contrib.auth.backends import BaseBackend
from shop_profile.models import ShopProfile
from user_profile.models import UserProfile
class Authenticate(BaseBackend):
    def authenticate(self, request, username=None, password=None, type=None, **kwargs):
        try:
            if type == 'user':
                # Look up user by email (username in this case)
                user = UserProfile.objects.get(email=username)
                if user.check_password(password):
                    return user

            elif type == 'shop':
                # Look up shop by email (username in this case)
                shop = ShopProfile.objects.get(email=username)
                if shop.check_password(password):
                    return shop  

        except UserProfile.DoesNotExist:
            return None  # if user not found
        except ShopProfile.DoesNotExist:
            return None  # if shop not found

        return None  # if any other exception occurs or no match is found
