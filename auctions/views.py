from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, Category, Listing, Comment, Bid

def listing(request, id):
    listing_data = Listing.objects.get(pk=id)
    is_listing_watchlist = request.user in listing_data.watchlist.all()
    is_owner = request.user.username == listing_data.owner.username
    all_comments = Comment.objects.filter(listing=listing_data)
    return render(request, "auctions/listing.html",{
        "listing": listing_data,
        "is_listing_watchlist": is_listing_watchlist,
        "all_comments":all_comments,
        "is_owner": is_owner
        
    })
    
def addBid(request,id):
    newBid = request.POST['newBid']
    listing_data = Listing.objects.get(pk=id)
    is_listing_watchlist = request.user in listing_data.watchlist.all()
    all_comments = Comment.objects.filter(listing=listing_data)
    is_owner = request.user.username == listing_data.owner.username
    if int(newBid) > listing_data.price.bid:
        updateBid = Bid(user=request.user, bid=int(newBid))
        updateBid.save()   
        listing_data.price = updateBid
        listing_data.save()
        return render(request,"auctions/listing.html",{
            "listing": listing_data,
            "message": "Bid was updated successfully",
            "update": True,
            "is_listing_watchlist": is_listing_watchlist,
            "all_comments":all_comments,
            "is_owner": is_owner,
        })
    else:
        return render(request,"auctions/listing.html",{
            "listing": listing_data,
            "message": "Bid updation Failed",
            "update": False,
            "is_listing_watchlist": is_listing_watchlist,
            "all_comments":all_comments,
            "is_owner": is_owner,
        })   
   
def closeAuction(request,id):
    listing_data = Listing.objects.get(pk=id)
    listing_data.is_active = False
    listing_data.save()
    is_owner = request.user.username == listing_data.owner.username
    is_listing_watchlist = request.user in listing_data.watchlist.all()
    all_comments = Comment.objects.filter(listing=listing_data)
    return render(request, "auctions/listing.html",{
        "listing":listing_data,
        "is_listing_watchlist": is_listing_watchlist,
        "all_comments": all_comments,
        "is_owner": is_owner,
        "update": True,
        "message":"congratulations! Your auction is closed"
        
    })
    
    
def remove_watchlist(request, id):
    listing_data = Listing.objects.get(pk=id)
    current_user = request.user
    listing_data.watchlist.remove(current_user)
    return HttpResponseRedirect(reverse("listing",args=(id, )))


def add_watchlist(request, id):
    listing_data = Listing.objects.get(pk=id)
    current_user = request.user
    listing_data.watchlist.add(current_user)
    return HttpResponseRedirect(reverse("listing",args=(id, )))

def dispaly_watchlist(request):
    current_user = request.user
    listings = current_user.listingWatchlist.all()
    return render(request,"auctions/watchlist.html",{
        "listings": listings,
    })
    

def index(request):
    active_listings = Listing.objects.filter(is_active=True)
    allcategories = Category.objects.all()
    return render(request, "auctions/index.html",{
        "Listings": active_listings,
        "category": allcategories,
    })
    
   
def comment(request,id):
    current_user = request.user
    listing_data = Listing.objects.get(pk=id)
    message = request.POST['comment']
    comment = Comment(
        author = current_user,
        listing = listing_data,
        message = message    
    )
    comment.save()
    return HttpResponseRedirect(reverse("listing",args=(id, )))
 
    
def dispaly_category(request):
    if request.method=="POST":
        cat_form =request.POST["category"]
        category = Category.objects.get(category_name=cat_form )
        active_listings = Listing.objects.filter(is_active=True, category=category)
        allcategories = Category.objects.all()
        return render(request, "auctions/index.html",{
            "Listings": active_listings,
            "category": allcategories,
        })

def create_listing (request):
    if request.method == "GET":
        allcategories = Category.objects.all()
        return render (request, "auctions/create.html",{
            "category": allcategories
        })
    else:
        # get the data from the form
        title = request.POST["title"]
        description =request.POST["description"]
        img_url =request.POST["imageurl"]
        price =request.POST["price"]
        category =request.POST["category"]
        # user 
        current_user =request.user
        # get all content about the particular category
        category_data = Category.objects.get(category_name= category)
        # Create a bid object
        bid = Bid(user=current_user, bid=int(price))
        bid.save()
        # create a new listing object
        new_listing = Listing(
            title = title,
            description = description,
            img_url = img_url,
            price = bid,
            category = category_data,
            owner = current_user                        
        )
        # insert the object in our database
        new_listing.save()
        # redirect to index page
        return HttpResponseRedirect(reverse(index))
        


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
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