from django.shortcuts import render
from shop_profile.models import ShopProfile, ShopWorker, ShopService

# Create your views here.
def index(request):
    if request.method == 'POST':
        # Retrieve form data
        item_id = request.POST.get('item_id')
        item_price = request.POST.get('item_price')
        shop_id = request.POST.get('shop_id')

        shop = ShopProfile.objects.filter(id=shop_id).first()
        service = ShopService.objects.filter(shop=shop_id, id=item_id).first()
        #service_name = service.item 
        workers = ShopWorker.objects.filter(shop=shop_id)
        

    return render(request, 'app/booking/book_step_1.html',{
        "shop": shop, 
        "service": service,
        # "shop_workers": workers, 
    })