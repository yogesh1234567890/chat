from django.shortcuts import  render, redirect
# from .forms import NewUserForm
from django.contrib.auth import login #add this
from django.contrib import messages,auth
from django.contrib.auth.forms import AuthenticationForm #add this

# Create your views here.
# def index(request):
# 	context={'user':request.user}
# 	return render(request, 'chat.html',context)

#create django login
def login_request(request):
	if request.method == "POST":
		username=request.POST.get('username')
		password=request.POST.get('password')
		user = auth.authenticate(username=username, password=password)
		if user is not None:
			login(request, user)
			messages.info(request, f"You are now logged in as {username}.")
			print(f"You are now logged in as {username}.")
			return redirect("interaction:index1")
		else:
			messages.error(request,"Invalid username or password.")
			print("Invalid username or password.")
	return render(request=request, template_name="sign-in.html")



