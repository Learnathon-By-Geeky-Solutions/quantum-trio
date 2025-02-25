# custom authenticate function for both user and shop login
from django.contrib.auth.backends import BaseBackend
from shop_profile.models import shop_profile
from user_profile.models import user_profile
class Authenticate(BaseBackend):
    def authenticate(self, request, username=None, password=None, type=None, **kwargs):
        try:
            if type == 'user':
                # Look up user by email (username in this case)
                user = user_profile.objects.get(email=username)
                if user.check_password(password):  # Verify password
                    return user  # Return the user object if authenticated

            elif type == 'shop':
                # Look up shop by email (username in this case)
                shop = shop_profile.objects.get(email=username)
                if shop.check_password(password):  # Verify password
                    return shop  # Return the shop object if authenticated

        except user_profile.DoesNotExist:
            return None  # if user not found
        except shop_profile.DoesNotExist:
            return None  # if shop not found

        return None  # if any other exception occurs or no match is found
