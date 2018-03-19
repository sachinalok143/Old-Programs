from django.shortcuts import render
from .forms import *
from .models import *
from .backends import *
from django.contrib.auth import (
	authenticate,
	get_user_model,
	login,
	logout,
	)
from django.http import HttpResponseRedirect



Category_set=Category.objects.all().order_by("Name")

def postReview(request):
	review=Review()
	temp=request.POST.get("star",5)
	temp=20*int(temp)
	review.Ratings=temp
	review.Book_id=request.POST.get("bookEdition"," ")
	if not Customer.objects.filter(user_id=request.user.id).count()>0:
		return HttpResponseRedirect('../accounts/logout')
	customer=Customer.objects.get(user_id=request.user.id)
	review.Customer_id=customer.id
	review.Content=request.POST.get("content"," nice")	
	review.save()
	# print(review.Book_id)
	allReviews=Review.objects.filter(Book_id=review.Book_id).order_by("-Created_at")
	class reviewDetail:
		def __init__(self, review=None, customer=None,user=None):
			self.review = review
			self.customer = customer
			self.user=user
	
	reviewList=[]

	for aReview in allReviews:
		customer=Customer.objects.get(id=aReview.Customer_id)
		user=User.objects.get(id=customer.user_id)
		reviewList.append(reviewDetail( aReview,customer,user))
	return render(request,"commentView.html",{"categories":Category_set,"reviewList":reviewList})



def deleteReview(request,id=None,Book_id=None):
	review=Review.objects.get(id=id)
	review.delete()
	allReviews=Review.objects.filter(Book_id=Book_id).order_by("-Created_at")
	class reviewDetail:
		def __init__(self, review=None, customer=None,user=None):
			self.review = review
			self.customer = customer
			self.user=user
	
	reviewList=[]

	for aReview in allReviews:
		customer=Customer.objects.get(id=aReview.Customer_id)
		user=User.objects.get(id=customer.user_id)
		reviewList.append(reviewDetail( aReview,customer,user))
	return render(request,"commentView.html",{"categories":Category_set,"reviewList":reviewList})


def addToCart(request,Book_id=None):
	# check=1
	# if request.POST :
	# print (request.user.id)
	if not Customer.objects.filter(user_id=request.user.id).count()>0:
		return HttpResponseRedirect('../accounts/logout')
	customer=Customer.objects.get(user_id=request.user.id)

	cartObj=Cart.objects.filter(Book_id=Book_id,Customer_id=customer.id)
	Quantity=1;
	if  cartObj :
		# cartObj[0].Quantity+=1
		Quantity=cartObj[0].Quantity+1
		cartObj.update(Quantity=cartObj[0].Quantity+1)
		check =1
	else :
		cartObject=Cart()
		cartObject.Customer_id=customer.id
		cartObject.Quantity=1;
		cartObject.Book_id=Book_id
		cartObject.save()
		check=0
	return render(request,"Notifications/dummy.html" ,{"check":check,"Quantity":Quantity})


def cartView(request):
	if not Customer.objects.filter(user_id=request.user.id).count()>0:
		return HttpResponseRedirect('../accounts/logout')
	customer=Customer.objects.get(user_id=request.user.id)
	cartObjects=Cart.objects.filter(Customer_id=customer.id)
	class cartObjectDetail(object):
		def __init__(self, cartObject=None, bookEdition=None):
			self.cartObject = cartObject
			self.bookEdition = bookEdition
	cartObjectList=[]
	totalPrice=0
	for cartObject in cartObjects:
		bookEdition=BookEdition.objects.get(id=cartObject.Book_id)
		cartObjectList.append(cartObjectDetail(cartObject,bookEdition))
		# print (cartObjectList.count)
		totalPrice+=(cartObject.Quantity*bookEdition.Price)
	totalPrice+=150
	return render(request,"cartView.html",{"totalPrice":totalPrice,
	 "Customer":customer,"cartObjectList":cartObjectList, "categories":Category_set})





def decQuantityInCart(request,id=None):
	c=Cart.objects.filter(id=id)
	if not c[0].Quantity==1:
		c.update(Quantity=c[0].Quantity-1)
	else :
		return render(request,"Notifications/cartdec.html" ,{"dec":2,"Quantity":c[0].Quantity})
	return render(request,"Notifications/cartdec.html" ,{"dec":1,"Quantity":c[0].Quantity})




def incQuantityInCart(request,id=None):
	c=Cart.objects.filter(id=id)
	c.update(Quantity=c[0].Quantity+1)
	return render(request,"Notifications/cartdec.html" ,{"dec":0,"Quantity":c[0].Quantity})


def deleteBookFromCart(request,id=None):
	book=Cart.objects.get(id=id)
	book.delete()
	if not Customer.objects.filter(user_id=request.user.id).count()>0:
		return HttpResponseRedirect('../accounts/logout')
	customer=Customer.objects.get(user_id=request.user.id)
	cartObjects=Cart.objects.filter(Customer_id=customer)
	class cartObjectDetail(object):
		def __init__(self, cartObject=None, bookEdition=None):
			self.cartObject = cartObject
			self.bookEdition = bookEdition
	cartObjectList=[]
	totalPrice=0
	for cartObject in cartObjects:
		bookEdition=BookEdition.objects.get(id=cartObject.Book_id)
		cartObjectList.append(cartObjectDetail(cartObject,bookEdition))
		totalPrice+=(cartObject.Quantity*bookEdition.Price)
	totalPrice+=150
	return render(request,"cartIndividualView.html",{"totalPrice":totalPrice,
	 "Customer":customer,"cartObjectList":cartObjectList})
# def orederViewDetail(request):




def placeOrder(request,flag=None):
	if not Customer.objects.filter(user_id=request.user.id).count()>0:
		return HttpResponseRedirect('../accounts/logout')
	customer=Customer.objects.get(user_id=request.user.id)
	cartObjects=Cart.objects.filter(Customer_id=customer)
	
	class orderObjectDetail(object):
		def __init__(self, orderObject=None, bookEdition=None):
			self.orderObject = orderObject
			self.bookEdition = bookEdition
	orderObjectList=[]
	totalPrice=0
	# print (flag)
	# print (request.user.id)
	if int(flag)==int(request.user.id):
		for cartObject in cartObjects:
			Ordr=Order()
			Ordr.Quantity=cartObject.Quantity
			Ordr.Book_id=cartObject.Book_id
			Ordr.Customer_id=cartObject.Customer_id
			Ordr.save()
			cartObject.delete()
	orderObjects=Order.objects.filter(Customer_id=customer)
	for orderObject in orderObjects:
		bookEdition=BookEdition.objects.get(id=orderObject.Book_id)
		orderObjectList.append(orderObjectDetail(orderObject,bookEdition))
		# print (ordertObjectList.count)
		totalPrice+=(orderObject.Quantity*bookEdition.Price)
	totalPrice+=150

	return render(request,"orderView.html",{"totalPrice":totalPrice,
	 "Customer":customer,"orderObjectList":orderObjectList, "categories":Category_set})

	# result = Book.objects.filter(string__icontains='%'Keyword+'%')
	
# class SearchProductView(ListView):
def getSearchResult(request):
	C="Search"
	query=request.POST.get('Search', )
	if query is not None:
		# print (query)
		books=Book.objects.filter(Title__icontains=query)
		class completeBookDetail(object):
			def __init__(self, book=None, bookEdition=None,discountedPrice=None):
				self.book = book
				self.bookEdition = bookEdition
				self.discountedPrice=discountedPrice
		bookDetailList=[]
		for book in books:
			bookEditions=BookEdition.objects.filter(Book_id=book.id)
			if bookEditions.count()>0:
				# print (book.Title)
				for bookEdition in bookEditions :
					d=bookEdition.Price*bookEdition.Discount/100
					d=bookEdition.Price-d
					bookDetailList.append(completeBookDetail(book,bookEdition,d))
		return render(request,"categoryView.html",{"bookDetailList":bookDetailList,
			"categories":Category_set,"CategoryName":C})
	else :
		return HttpResponseRedirect('')

def getBookBySeller(request,id=None):
	seller=Seller.objects.get(User_id=id)
	C="Seller"
	if str(id)==str(request.user.id):
		bookEditions=BookEdition.objects.filter(Seller_id=seller.id)
		class completeBookDetail(object):
			def __init__(self, book=None, bookEdition=None,discountedPrice=None):
				self.book = book
				self.bookEdition = bookEdition
				self.discountedPrice=discountedPrice
		bookDetailList=[]
		if bookEditions.count()>0:
			for bookEdition in bookEditions :
				book=Book.objects.get(id=bookEdition.Book_id)
				d=bookEdition.Price*bookEdition.Discount/100
				d=bookEdition.Price-d
				bookDetailList.append(completeBookDetail(book,bookEdition,d))
		return render(request,"Seller/categoryView.html",{"bookDetailList":bookDetailList,
			"categories":Category_set,"CategoryName":C})
		return HttpResponseRedirect('')
def deleteBook(request,Book_id=None,id=None):
	if str(id)==str(request.user.id):
		bookEdition=BookEdition.objects.get(id=Book_id)
		bookEdition.delete()
		seller=Seller.objects.get(User_id=id)
		C="Seller"
		if str(id)==str(request.user.id):
			bookEditions=BookEdition.objects.filter(Seller_id=seller.id)
			class completeBookDetail(object):
				def __init__(self, book=None, bookEdition=None,discountedPrice=None):
					self.book = book
					self.bookEdition = bookEdition
					self.discountedPrice=discountedPrice
			bookDetailList=[]
			if bookEditions.count()>0:
				for bookEdition in bookEditions :
					book=Book.objects.get(id=bookEdition.Book_id)
					d=bookEdition.Price*bookEdition.Discount/100
					d=bookEdition.Price-d
					bookDetailList.append(completeBookDetail(book,bookEdition,d))
			return render(request,"Seller/categoryIndividualView.html",{"bookDetailList":bookDetailList,
				"categories":Category_set,"CategoryName":C})
	return HttpResponseRedirect('')

def getSellerSingleBook(request,id=None):
	form=ReviewForm(request.POST or None)
	bookEdition=BookEdition.objects.get(id=id)
	book=Book.objects.get(id=bookEdition.Book_id)
	class completeBookDetail(object):
		def __init__(self, book=None, bookEdition=None,discountedPrice=None,categories=None):
			self.book = book
			self.bookEdition = bookEdition
			self.discountedPrice=discountedPrice
			self.categories=categories
	d=bookEdition.Price*bookEdition.Discount/100
	d=bookEdition.Price-d
	Cs=BookCategory.objects.filter(Book_id=book.id)
	C=[]
	for x in Cs:
		y=Category.objects.get(id=x.Category_id)
		C.append(str(y.Name))
	bookDetail=completeBookDetail(book,bookEdition,d,C)
		# print (bookDetailList)\

	allReviews=Review.objects.filter(Book_id=book.id).order_by("-Created_at")
	class reviewDetail:
		def __init__(self, review=None, customer=None,user=None):
			self.review = review
			self.customer = customer
			self.user=user
	
	reviewList=[]

	for aReview in allReviews:
		customer=Customer.objects.get(id=aReview.Customer_id)
		user=User.objects.get(id=customer.user_id)
		reviewList.append(reviewDetail( aReview,customer,user))
	
	return render(request,"Seller/singleView.html",
		{"bookDetail":bookDetail,"categories":Category_set,"form":form,"reviewList":reviewList})
def aboutUs(request):
	return render(request,"Notifications/aboutUs.html",{})
def faqsView(request):
	return render(request,"Notifications/faqs.html",{})
