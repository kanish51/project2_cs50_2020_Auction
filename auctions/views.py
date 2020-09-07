from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.forms import ModelForm
from django.db.models import Max
from decimal import Decimal

from .models import User,Category,AuctionListing,Bid,Comment


class CreateListingEntryForm(ModelForm):
    class Meta:
        model=AuctionListing
        fields = ['image', 'productName', 'price', 'description','category']

class PlaceBidForm(forms.Form):
    bidval= forms.DecimalField(label="Your Bid Value",max_digits=9,decimal_places=2)

class PlaceCommentForm(forms.Form):
    commentval= forms.CharField(label="Your Comment",max_length=300)

def index(request):
    return render(request, "auctions/index.html",{
        "auctionlist":AuctionListing.objects.all()
        })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            if "next" in request.POST:
                return HttpResponseRedirect(request.POST.get("next"))
            else:
                return HttpResponseRedirect(reverse("index"))
        else:
            if "next" in request.POST:
                url=reverse("login")
                return redirect(url+"?next="+request.POST.get("next"))
            else:
                return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        if request.META.get('HTTP_REFERER')!=None and "next" in request.META.get('HTTP_REFERER'):
            return render(request, "auctions/login.html",{
                "message": "Invalid username and/or password."
                })
        else:
            return render(request, "auctions/login.html")
        


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def CreateListing(request):
    if request.method == "POST":
        formReceived=CreateListingEntryForm(request.POST)
        if formReceived.is_valid():
            product=AuctionListing(image=formReceived.cleaned_data["image"],
                productName=formReceived.cleaned_data["productName"],
                price=formReceived.cleaned_data["price"],
                description=formReceived.cleaned_data["description"],
                active=True,listerName=request.user,category=formReceived.cleaned_data["category"])
            product.save()
            return HttpResponseRedirect(reverse("view_listing",kwargs={'productid':product.id}))
        else:
            return render(request,"auctions/createlisting.html",{
                "form":formReceived
                })
    return render(request, "auctions/createlisting.html",{
        "form":CreateListingEntryForm()
        })



def ViewListing(request,productid):
    item=AuctionListing.objects.get(id=productid)
    totalbids=item.bidsmade.all()
    totalcomments=item.commentsmade.all()
    if not totalbids:
        maxbiduser=item.listerName
        maxbid=item.price
    else:
        maxbidobj=totalbids.order_by('-bidValue').first()
        maxbiduser=maxbidobj.user
        maxbid=maxbidobj.bidValue

    if request.method=="POST":
        usr=request.user
        if "watchlist" in request.POST:
            if usr.username!=item.listerName.username and item.active ==True:
                if not usr.mywatchlist.filter(id=productid):
                    item.watchlist.add(request.user)
                    return redirect("view_listing",productid=productid)
                else:
                    item.watchlist.remove(request.user)
                    return redirect("view_listing",productid=productid)
            else:
                return redirect("view_listing",productid=productid)
        elif "placebidform" in request.POST:
            formReceived=PlaceBidForm(request.POST)
            if formReceived.is_valid() and formReceived.cleaned_data["bidval"]>maxbid and usr.username!=item.listerName.username and item.active == True:
                bidobj=Bid(user=request.user,bidValue=formReceived.cleaned_data["bidval"],listing=AuctionListing.objects.get(id=productid)) 
                bidobj.save()
                return redirect("view_listing",productid=productid)
            else:
                if not usr.mywatchlist.filter(id=productid):
                    return render(request, "auctions/viewlisting.html",{
                    "product":item,
                    "watchlistdata":'Add to Watchlist',
                    "highestbid":maxbid,
                    "placebiderror":"Error bid value should be greater than current highest bid value or you are not allowed.",
                    "placebidform":formReceived,
                    "placecommentform":PlaceCommentForm(),
                    "bids":totalbids,
                    "comments":totalcomments
                    })
                else:
                    return render(request, "auctions/viewlisting.html",{
                    "product":item,
                    "watchlistdata":'Remove from Watchlist',
                    "highestbid":maxbid,
                    "placebiderror":"Error bid value should be greater than current highest bid value or you are not allowed.",
                    "placebidform":formReceived,
                    "placecommentform":PlaceCommentForm(),
                    "bids":totalbids,
                    "comments":totalcomments
                    })
        elif "placecommentform" in request.POST:
            formReceived=PlaceCommentForm(request.POST)
            if formReceived.is_valid() and item.active == True:
                commentobj=Comment(user=request.user,comment=formReceived.cleaned_data["commentval"],listing=AuctionListing.objects.get(id=productid)) 
                commentobj.save()
                return redirect("view_listing",productid=productid)
            else:
                if not usr.mywatchlist.filter(id=productid):
                    return render(request, "auctions/viewlisting.html",{
                    "product":item,
                    "watchlistdata":'Add to Watchlist',
                    "highestbid":maxbid,
                    "placebidform":PlaceBidForm(),
                    "placecommentform":formReceived,
                    "bids":totalbids,
                    "comments":totalcomments
                    })
                else:
                    return render(request, "auctions/viewlisting.html",{
                    "product":item,
                    "watchlistdata":'Remove from Watchlist',
                    "highestbid":maxbid,
                    "placebidform":PlaceBidForm(),
                    "placecommentform":formReceived,
                    "bids":totalbids,
                    "comments":totalcomments
                    })
        elif "close" in request.POST:
            if usr.username == item.listerName.username:
                item.active=False
                item.wonby=maxbiduser
                item.save()
                redirect("view_listing",productid=productid)
            else:
                return redirect("view_listing",productid=productid)

    if request.user.is_authenticated:
        usr=request.user
        if not usr.mywatchlist.filter(id=productid):
            return render(request, "auctions/viewlisting.html",{
            "product":item,
            "watchlistdata":'Add to Watchlist',
            "highestbid":maxbid,
            "placebidform":PlaceBidForm(),
            "bids":totalbids,
            "placecommentform":PlaceCommentForm(),
            "comments":totalcomments
            })
        else:
            return render(request, "auctions/viewlisting.html",{
            "product":item,
            "watchlistdata":'Remove from Watchlist',
            "highestbid":maxbid,
            "placebidform":PlaceBidForm(),
            "bids":totalbids,
            "placecommentform":PlaceCommentForm(),
            "comments":totalcomments
            })
    return render(request, "auctions/viewlisting.html",{
        "product":item,
        "highestbid":maxbid,
        "bids":totalbids,
        "comments":totalcomments
        })

@login_required
def Watchlist(request):
    return render(request, "auctions/index.html",{
        "auctionlist":request.user.mywatchlist.all()
        })


def Categories(request): 
    if "q" in request.GET:
        categorylist=Category.objects.all().values_list('categoryName', flat=True)
        query=request.GET.get("q")
        if query in categorylist:
            return render(request,"auctions/index.html",{
                "catname":query,
                "auctionlist":Category.objects.get(categoryName=query).similarListings.all()
                })
        else:
            return redirect("index")

    
    return render(request, "auctions/viewcategories.html",{
        "categorylist":Category.objects.all()
        })
