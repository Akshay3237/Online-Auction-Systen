from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .forms import EditProfileForm
from .models import AuctionItem
from django.urls import reverse
from django.utils import timezone
from datetime import datetime
from decimal import Decimal
from .models import Image
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.forms import formset_factory
from .forms import EditProfileForm
from .forms import AuctionItemForm,ImageForm
from .models import AuctionItem,Image,Bid
from . import models
from django.db.models import Q


def home(request):
    username = request.user.username

    items = AuctionItem.objects.order_by('-id')[:5]
    images = Image.objects.filter(item__in=items)
    items_reversed = reversed(items)
    item_image_pairs = zip(items_reversed, images)
    context = {
        'main_user': username,
        'item_image_pairs': item_image_pairs,
    }
    return render(request,'index.html',context)

def item(request, item_id):
    item = get_object_or_404(AuctionItem, pk=item_id)
    images = Image.objects.filter(item=item)
    current_time = timezone.now()  # Retrieve all images associated with the AuctionItem
    return render(request, 'show.html', {'item': item, 'images': images, 'current_time': current_time})  # Pass images to the template

from django.shortcuts import render
from .models import Bid, AuctionItem

def profile(request):
    user = request.user
    bids = Bid.objects.filter(bidder=user)
    won_auctions = []
    
    for bid in bids:
        auction = bid.auction
        if bid.bid_amount == auction.highest_bid and auction.seller.email != user.email:
            seller_email = auction.seller.email
            won_auctions.append({
                'item_name': auction.name,
                'base_price': auction.base_price,
                'winning_bid': bid.bid_amount,
                'seller_email': seller_email
            })
    
    return render(request, 'profile.html', {'won_auctions': won_auctions})


def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the profile page after saving changes
    else:
        form = EditProfileForm(instance=request.user)
    
    return render(request, 'edit_profile.html', {'form': form})

def my_auctions(request):
    user = request.user
    user_auctions = AuctionItem.objects.filter(seller=user)
    context = {
        'user' : user,
        'user_auctions' : user_auctions,
    }
    return render(request, 'my_auctions.html', context)

@login_required
def create_auction(request):
    if request.method == 'POST':
        auction_form = AuctionItemForm(request.POST)
        if auction_form.is_valid():
            auction = auction_form.save(commit=False)
            auction.seller = request.user  # Assign the seller
            auction.save()
            return redirect('add_image', auction_id=auction.pk)  # Redirect to add_images page with auction ID
    else:
        auction_form = AuctionItemForm()
    return render(request, 'create_auction.html', {'auction_form': auction_form})

ImageFormSet = formset_factory(ImageForm, extra=5)
def add_image(request, auction_id):
    if request.method == 'POST':
        formset = ImageFormSet(request.POST, request.FILES, prefix='images')

        if formset.is_valid():
            auction = AuctionItem.objects.get(pk=auction_id)

            for form in formset:
                if form.cleaned_data.get('image'):
                    image = form.save(commit=False)
                    image.item = auction
                    image.save()

            return HttpResponseRedirect(reverse('my_auctions'))
    else:
        formset = ImageFormSet(prefix='images')

    return render(request, 'add_image.html', {'formset': formset})

def auction_detail(request, pk):
    auction = get_object_or_404(AuctionItem, pk=pk)
    # You can perform any necessary logic here, such as fetching additional data
    # or processing the auction item before rendering it in the template
    return render(request, 'auction_detail.html', {'auction': auction})
from django.utils import timezone

def handle_bid(request, auction_id):
    if request.method == 'POST':
        auction = get_object_or_404(AuctionItem, pk=auction_id)
        bid_amount = request.POST.get('bid_amount')
        with transaction.atomic():
            # Validate bid amount
            if bid_amount:
                try:
                    bid_amount = Decimal(bid_amount)
                    if bid_amount >= auction.base_price:
                        if bid_amount > auction.highest_bid:
                            auction.highest_bid = bid_amount
                            auction.save()
                            Bid.objects.create(auction=auction, bidder=request.user, bid_amount=bid_amount)
                            messages.success(request, 'Your bid has been placed successfully.')
                        else:
                            messages.error(request, 'Bid amount must be higher than the current highest bid.')
                    else:
                        messages.error(request, 'Bid amount must be higher than the base price.')
                except ValueError:
                    messages.error(request, 'Invalid bid amount.')
            else:
                messages.error(request, 'Bid amount is required.')

    return redirect('item', item_id=auction_id )


def bid_history(request):
    user = request.user
    bids = Bid.objects.filter(bidder=user)
    bid_history = []
    for bid in bids:
        item_name = bid.auction.name
        base_price = bid.auction.base_price
        my_bid = bid.bid_amount
        bid_history.append({'item_name': item_name, 'base_price': base_price, 'my_bid': my_bid})
    return render(request, 'bid_history.html', {'bid_history': bid_history})

def see_more(request):
    items = AuctionItem.objects.all()
    images = Image.objects.filter(item__in=items)
    item_image_pairs = zip(items, images)
    context = {
        'item_image_pairs': item_image_pairs,
    }
    return render(request, 'see_more.html', context)
from django.shortcuts import render
from django.db.models import Max
from .models import AuctionItem, Bid

from django.db.models import Max

def auction_reports(request):
    # Retrieve all completed auctions for the current user
    completed_auctions = AuctionItem.objects.filter(
        seller=request.user, end_time__lt=timezone.now()
    )

    # Fetch the highest bid and bidder for each completed auction item
    for auction in completed_auctions:
        highest_bid_tuple = Bid.objects.filter(auction=auction).aggregate(Max('bid_amount'))
        highest_bid_amount = highest_bid_tuple['bid_amount__max']
        highest_bidder = Bid.objects.filter(auction=auction, bid_amount=highest_bid_amount).first()
        
        auction.highest_bid = highest_bid_amount
        auction.highest_bidder_username = highest_bidder.bidder.username if highest_bidder else None
        auction.highest_bidder_email = highest_bidder.bidder.email if highest_bidder else None

    return render(request, 'auction_reports.html', {'completed_auctions': completed_auctions})

def search_products(request):
    query = request.GET.get('q')
    if query:
        results = AuctionItem.objects.filter(
            Q(name__icontains=query) | Q(category__iexact=query)
        )
        results_count = results.count()
        # Pass 'results' to the template for rendering
    else:
        results = None
        results_count = 0
    return render(request, 'search_results.html', {'results': results,'query':query,'results_count': results_count})
