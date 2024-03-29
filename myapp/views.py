from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from .forms import EditProfileForm, AuctionItemForm, ImageForm
from .models import AuctionItem, Image, Bid
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from django.db import transaction
from django.contrib import messages
from django.forms import formset_factory
from django.db.models import Q, Max


def home(request):
    username = request.user.username

    items = AuctionItem.objects.order_by('-id')[:5]
    item_image_pairs = []

    for item in items:
        image = Image.objects.filter(item=item).first()
        item_image_pairs.append((item, image))
        
    context = {
        'main_user': username,
        'item_image_pairs': item_image_pairs,
    }
    return render(request,'index.html',context)

def item(request, item_id):
    item = get_object_or_404(AuctionItem, pk=item_id)
    images = Image.objects.filter(item=item)
    current_time = timezone.now()
    return render(request, 'show.html', {'item': item, 'images': images, 'current_time': current_time})  # Pass images to the template

def profile(request):
    return render(request, 'profile.html')


def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user)
    
    return render(request, 'edit_profile.html', {'form': form})

def my_auctions(request):
    user = request.user
    current_time = timezone.now()
    user_auctions = AuctionItem.objects.filter(seller=user, end_time__gt=current_time)
    context = {
        'user' : user,
        'user_auctions' : user_auctions,
    }
    return render(request, 'my_auctions.html', context)

def create_auction(request):
    if request.method == 'POST':
        auction_form = AuctionItemForm(request.POST)
        if auction_form.is_valid():
            auction = auction_form.save(commit=False)
            auction.seller = request.user
            auction.save()
            return redirect('add_image', auction_id=auction.pk)
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

def handle_bid(request, auction_id):
    if request.method == 'POST':
        auction = get_object_or_404(AuctionItem, pk=auction_id)
        bid_amount = request.POST.get('bid_amount')
        with transaction.atomic():
            if bid_amount:  
                try:
                    bid_amount = Decimal(bid_amount)
                    if bid_amount >= auction.base_price:
                        if bid_amount > auction.highest_bid:
                            auction.highest_bid = bid_amount
                            auction.save()
                            Bid.objects.create(auction=auction, bidder=request.user, bid_amount=bid_amount)
                            messages.success(request,'Your bid has been placed successfully.')
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
        auction = bid.auction 
        item_name = auction.name
        base_price = auction.base_price
        my_bid = bid.bid_amount
        highest_bid = Bid.objects.filter(auction=auction).aggregate(Max('bid_amount'))['bid_amount__max']
        status = "WON" if highest_bid == my_bid else "LOST"

        bid_history.append({
            'item_name': item_name,
            'base_price': base_price,
            'my_bid': my_bid,
            'highest_bid': highest_bid,
            'status': status,
        })

    return render(request, 'bid_history.html', {'bid_history': bid_history})


def see_more(request):
    items = AuctionItem.objects.all()
    item_image_pairs = []

    for item in items:
        image = Image.objects.filter(item=item).first()
        item_image_pairs.append((item, image))

    context = {
        'item_image_pairs': item_image_pairs,
    }
    return render(request, 'see_more.html', context)

def auction_reports(request):
    completed_auctions = AuctionItem.objects.filter(
        seller=request.user, end_time__lt=timezone.now()
    )

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
    else:
        results = None
        results_count = 0
    return render(request, 'search_results.html', {'results': results,'query':query,'results_count': results_count})
