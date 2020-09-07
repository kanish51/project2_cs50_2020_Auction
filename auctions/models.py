from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator

class User(AbstractUser):
    pass

class Category(models.Model):
	categoryName=models.CharField(max_length=20)

	def __str__(self):
		return f"{self.categoryName}"

class AuctionListing(models.Model):
	image=models.URLField(max_length=300)
	productName=models.CharField(max_length=120)
	price=models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(0.00),MaxValueValidator(9999999.99)])
	description=models.CharField(max_length=1000)
	datetime=models.DateTimeField(auto_now_add=True)
	active=models.BooleanField(default=True)
	listerName=models.ForeignKey(User,on_delete=models.CASCADE,related_name="myListings")
	category=models.ForeignKey(Category,on_delete=models.PROTECT,related_name="similarListings")
	wonby=models.ForeignKey(User,on_delete=models.CASCADE,related_name="bidswon",blank=True,null=True)
	watchlist=models.ManyToManyField(User,blank=True,related_name="mywatchlist")

	def __str__(self):
		return f"{self.productName} | Price {self.price}Rs | ({self.listerName.username})"

class Comment(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="myComments")
	comment=models.CharField(max_length=300)
	listing=models.ForeignKey(AuctionListing,on_delete=models.CASCADE,related_name="commentsmade")


	def __str__(self):
		return f"{self.user.username} | {self.listing.productName} | {self.comment}"

class Bid(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="myBids")
	bidValue=models.DecimalField(max_digits=9, decimal_places=2)
	listing=models.ForeignKey(AuctionListing,on_delete=models.CASCADE,related_name="bidsmade")

	def __str__(self):
		return f"{self.user.username} | {self.listing.productName} | {self.bidValue}"


