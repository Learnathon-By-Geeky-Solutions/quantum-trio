# import pytest
# from datetime import date, time
# from booking.models import BookingSlot
# from my_app.models import Item
# from user_profile.models import UserProfile
# from shop_profile.models import ShopProfile, ShopWorker

# @pytest.mark.django_db
# def test_booking_creation():
#     user = UserProfile.objects.create(user_id=1)
#     shop = ShopProfile.objects.create(name="Test Shop")
#     worker = ShopWorker.objects.create(name="John", shop=shop)
#     item = Item.objects.create(name="Haircut", price=15.0)

#     booking = BookingSlot.objects.create(
#         user=user,
#         shop=shop,
#         worker=worker,
#         item=item,
#         date=date.today(),
#         time=time(10, 0),
#         notes="Testing"
#     )

#     assert booking.status == "pending"

# @pytest.mark.django_db
# def test_auto_complete_booking():
#     user = UserProfile.objects.create(user_id=2)
#     shop = ShopProfile.objects.create(name="Auto Complete Shop")
#     worker = ShopWorker.objects.create(name="Jane", shop=shop)
#     item = Item.objects.create(name="Shave", price=10.0)

#     booking = BookingSlot.objects.create(
#         user=user,
#         shop=shop,
#         worker=worker,
#         item=item,
#         date=date.today(),
#         time=time(12, 0)
#     )

#     booking.user_end = True
#     booking.shop_end = True
#     booking.save()

#     assert booking.status == "completed"
