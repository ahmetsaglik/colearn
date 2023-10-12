from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage, FileSystemStorage
from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm, AccountDeleteForm
from blog.models import BlogPost
from account.models import Account
from django.core import files

import os
import cv2
import json
import base64

TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"

def registration_view(request):
    context = {}

    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            account = authenticate(email=email, password=raw_password)
            login(request, account)
            return redirect('home')
        else:
            context['registration_form'] = form
    else:
        form = RegistrationForm()
        context['registration_form'] = form
    
    return render(request, 'account/register.html', context)


def logout_view(request):
    logout(request)
    return redirect('home')


def login_view(request):
    context = {}

    user = request.user
    if user.is_authenticated:
        return redirect('home')

    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                return redirect('home')
    else:
        form = AccountAuthenticationForm()

    context['login_form'] = form
    return render(request, 'account/login.html', context)


@login_required
def account_view(request, *args, **kwargs):
    context = {}

    if not request.user.is_authenticated:
        return redirect('must-authenticate')
    
    user_id = kwargs.get('user_id')
    try:
        account = Account.objects.get(pk=user_id)
    except Account.DoesNotExist:
        return HttpResponse('User not found!')
    
    if account:
        context['id'] = account.id
        context['username'] = account.username
        context['email'] = account.email
        context['first_name'] = account.first_name
        context['last_name'] = account.last_name
        context['profile_image'] = account.profile_image
        
    try:
        posts = BlogPost.objects.all().filter(author = account)
    except BlogPost.DoesNotExist:
        posts = []
    context['posts'] = posts

    is_self = True
    
    user = request.user
    if user.is_authenticated and user != account:
        is_self = False
    
    context['is_self'] = is_self
    return render(request, 'account/account.html', context)


@login_required
def edit_account_view(request, *args, **kwargs):
    context = {}

    if not request.user.is_authenticated:
        return redirect('must-authenticate')

    user_id = kwargs.get('user_id')
    try:
        account = Account.objects.get(pk=user_id)
    except Account.DoesNotExist:
        return HttpResponse('Something went wrong..')
    
    if account.pk != request.user.pk:
        return HttpResponse("You cannot edit someone else's profile!")
    
    if request.POST:
        form = AccountUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('account', user_id=account.pk)
        else:
            form = AccountUpdateForm(request.POST, instance=request.user,
            initial={
                "id" : account.pk,
                "email" : account.email,
                "username" : account.username,
                "first_name" : account.first_name,
                "last_name" : account.last_name,
                'profile_image' : account.profile_image
            })
    else:
        form = AccountUpdateForm(
                initial= {
                    "id" : account.pk,
                    "email" : account.email,
                    "username" : account.username,
                    "first_name" : account.first_name,
                    "last_name" : account.last_name,
                    'profile_image' : account.profile_image
                }    
            )
    context['form'] = form
    return render(request, 'account/edit_account.html', context)

@login_required
def delete_account_view(request):
    if request.method == 'POST':
        delete_form = AccountDeleteForm(request.POST, instance=request.user)
        user = request.user
        user.delete()
        messages.info(request, 'Your account has been deleted.')
        return redirect('home')
    else:
        delete_form = AccountDeleteForm(instance=request.user)

    context = {
        'delete_form': delete_form,
    }

    return render(request, 'account/delete_account.html', context)


def must_authenticate_view(request):
    context = {}
    return render(request, 'account/must_authenticate.html', context)


def save_temp_profile_image_from_base64String(imageString, user):
	INCORRECT_PADDING_EXCEPTION = "Incorrect padding"
	try:
		if not os.path.exists(settings.TEMP):
			os.mkdir(settings.TEMP)
		if not os.path.exists(settings.TEMP + "/" + str(user.pk)):
			os.mkdir(settings.TEMP + "/" + str(user.pk))
		url = os.path.join(settings.TEMP + "/" + str(user.pk),TEMP_PROFILE_IMAGE_NAME)
		storage = FileSystemStorage(location=url)
		image = base64.b64decode(imageString)
		with storage.open('', 'wb+') as destination:
			destination.write(image)
			destination.close()
		return url
	except Exception as e:
		print("exception: " + str(e))
		# workaround for an issue I found
		if str(e) == INCORRECT_PADDING_EXCEPTION:
			imageString += "=" * ((4 - len(imageString) % 4) % 4)
			return save_temp_profile_image_from_base64String(imageString, user)
	return None


def crop_image(request, *args, **kwargs):
	payload = {}
	user = request.user
	if request.POST and user.is_authenticated:
		try:
			imageString = request.POST.get("image")
			url = save_temp_profile_image_from_base64String(imageString, user)
			img = cv2.imread(url)

			cropX = int(float(str(request.POST.get("cropX"))))
			cropY = int(float(str(request.POST.get("cropY"))))
			cropWidth = int(float(str(request.POST.get("cropWidth"))))
			cropHeight = int(float(str(request.POST.get("cropHeight"))))
			if cropX < 0:
				cropX = 0
			if cropY < 0: # There is a bug with cropperjs. y can be negative.
				cropY = 0
			crop_img = img[cropY:cropY+cropHeight, cropX:cropX+cropWidth]

			cv2.imwrite(url, crop_img)

			# delete the old image
			user.profile_image.delete()

			# Save the cropped image to user model
			user.profile_image.save("profile_image.png", files.File(open(url, 'rb')))
			user.save()

			payload['result'] = "success"
			payload['cropped_profile_image'] = user.profile_image.url

			# delete temp file
			os.remove(url)
			
		except Exception as e:
			payload['result'] = "error"
			payload['exception'] = str(e)
	return HttpResponse(json.dumps(payload), content_type="application/json")