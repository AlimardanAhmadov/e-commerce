from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import HttpResponse

from .forms import UserRegisterForm, LoginForm, ProfileForm, AddressForm, BecomeSellerForm, SellerLoginForm
from .models import Profile, Address, SellerRequest, ApproveSellerEmail, Seller

from main import models as mainmodels

from .tokens import account_activation_token

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def signup_success(request):
    return render(request, 'user/success.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST or None)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')
            if User.objects.filter(email=email).exists():
                messages.warning(request, 'User with this credentials already exists!', extra_tags='email')
                return redirect(reverse('register'))
            else:
                user = form.save(commit=False)
                user.is_active = False
                user.save()   

                mail_subject = 'Active Your Account!'
                current_site = get_current_site(request)
                content = render_to_string('user/account_confirmation.html', {
                    'email': email,
                    'domain': current_site,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })

                message = Mail(
                    from_email='eelimerdan752@gmail.com',
                    to_emails=email,
                    subject=mail_subject,
                    html_content=content
                )

                try:
                    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
                    response = sg.send(message)
                    print(response.status_code)
                    print(response.body)
                    print(response.headers)
                except Exception as e:
                    print(e)

            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            return redirect(reverse('signup_success'))
    else:
        form = UserRegisterForm()

    context = {
        'form': form,
    }    

    return render(request, 'user/signup.html', context)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'user/activate_account.html')
    else:
        return render(request, 'base.html')    


def login_view(request):
    if request.method == "POST":
        login_form = LoginForm(request.POST or None)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if login_form.is_valid():
            user = login_form.login(request)
            if user is not None and user.is_active:
                login(request, user)
                return redirect(reverse('home'))
        else:
            messages.warning(request, 'Password or username is not correct!', extra_tags="login_fail")
            return redirect(reverse('login_view'))
    else:
        login_form = LoginForm()

    context = {
        'login_form': LoginForm()
    }

    return render(request, 'user/login.html', context)


def my_profile(request):
    current_user = request.user
    billing_address = Address.objects.filter(owner=current_user, default=True, address_type='Billing Address')
    print(billing_address)
    shipping_address = Address.objects.filter(owner=current_user, default=True, address_type='Shipping Address')
    context = {
        'categories': mainmodels.Subcategories.objects.all(),
        'billing_address': billing_address,
        'shipping_address': shipping_address,
    }
    return render(request, 'user/profile.html', context)


def add_address(request):
    if request.method == "POST":
        address_form = AddressForm(request.POST or None)

        if address_form.is_valid():
            print("Customer is entering a new shipping address")
            address = address_form.cleaned_data.get('address')
            city = address_form.cleaned_data.get('city')
            region = address_form.cleaned_data.get('region')
            postcode = address_form.cleaned_data.get('postcode')
            flat = address_form.cleaned_data.get('flat')
            country = address_form.cleaned_data.get('country')
            address_type = address_form.cleaned_data.get('address_type')
            # default = address_form.cleaned_data.get('default')

            shipping_address = Address(
                owner=request.user,
                address=address,
                city=city,
                region=region,
                flat=flat,
                postcode=postcode,
                country=country,
                address_type=address_type,
                default=True
            )
            shipping_address.save()

            messages.success(request, f'Congratulations, your addres has been updated', extra_tags='profile')
            return redirect(reverse('my_profile'))
    else:
        address_form = AddressForm()

    context = {
        'categories': mainmodels.Subcategories.objects.all(),
        'address_form': address_form,
    }                

    return render(request, 'user/address.html', context)


def edit_address(request, pk):
    selected_address = get_object_or_404(Address, id=pk)
    if request.method == "POST":
        address_form = AddressForm(request.POST or None)

        if address_form.is_valid():
            print("Customer is updating the address")
            address = address_form.cleaned_data.get('address')
            city = address_form.cleaned_data.get('city')
            region = address_form.cleaned_data.get('region')
            postcode = address_form.cleaned_data.get('postcode')
            flat = address_form.cleaned_data.get('flat')
            country = address_form.cleaned_data.get('country')
            address_type = address_form.cleaned_data.get('address_type')
            #default = address_form.cleaned_data.get('default')

            shipping_address = Address.objects.get(
                owner=selected_address.owner,
                address=selected_address.address,
                city=selected_address.city,
                region=selected_address.region,
                flat=selected_address.flat,
                postcode=selected_address.postcode,
                country=selected_address.country,
                address_type=selected_address.address_type,
                default=selected_address.default
            )
            shipping_address.owner = request.user
            shipping_address.address = address
            shipping_address.city = city
            shipping_address.region = region
            shipping_address.flat = flat
            shipping_address.postcode = postcode
            shipping_address.country = country
            shipping_address.address_type = address_type
            shipping_address.default = True
            shipping_address.save()

            messages.success(request, f'Congratulations, your addres has been updated', extra_tags='profile')
            return redirect(reverse('my_profile'))
    else:
        address_form = AddressForm()

    context = {
        'categories': mainmodels.Subcategories.objects.all(),
        'address_form': address_form,
        'selected_address': selected_address,
    }                

    return render(request, 'user/update_address.html', context)


def personal_information(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)

    if request.method == "POST":
        p_update = ProfileForm(request.POST, instance=request.user.profile)
        
        if p_update.is_valid():
            p_update.save()
            return redirect(reverse('my_profile'))
    else:
        p_update = ProfileForm(instance=request.user.profile)

    context = {
        'categories': mainmodels.Subcategories.objects.all(),
        'p_update': p_update,
        'profile': profile,
    }            

    return render(request, 'user/personal_information.html', context)


def become_vendor(request):
    current_user = request.user

    try:
        seller_profile = current_user.seller
        context = {
            'categories': mainmodels.Subcategories.objects.all(),
            'seller_profile': seller_profile
        }
        
        return render(request, 'user/become_seller.html', context)
    except Seller.DoesNotExist:
        print('You do not have a seller account!')

    return render(request, 'user/become_seller.html', {'categories': mainmodels.Subcategories.objects.all(),})


def seller_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST or None)
        p_reg_form = BecomeSellerForm(request.POST or None)
        if form.is_valid() and p_reg_form.is_valid():
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                messages.warning(request, 'Customer or seller account with this email already exists!', extra_tags='email')
                return redirect(reverse('seller_register'))    
            phone_number = p_reg_form.cleaned_data.get('phone_number')

            user = form.save(commit=False)
            user.is_active = False
            user.save()

            profile = p_reg_form.save(commit=False)
            profile.user = user
            profile.email = user.email
            profile.save()
            messages.success(request, f'Your account has been sent for approval!', extra_tags="seller_confirm")

            # send confirmation email 
            mail_subject = 'Active Your Account!'
            current_site = get_current_site(request)
            content = render_to_string('user/seller_account_confirmation.html', {
                'email': email,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            message = Mail(
                from_email='eelimerdan752@gmail.com',
                to_emails=email,
                subject=mail_subject,
                html_content=content
            )

            try:
                sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                print(e)
            # return redirect('login')
    else:
        form = UserRegisterForm()
        p_reg_form = BecomeSellerForm()

    context = {
        'categories': mainmodels.Subcategories.objects.all(),
        'form': form,
        'p_reg_form': p_reg_form
    }
    return render(request, 'user/seller_register.html', context)

    
def seller_login_view(request):
    if request.method == "POST":
        login_form = SellerLoginForm(request.POST or None)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if login_form.is_valid():
            user = login_form.login(request)
            try:
                if user is not None and user.is_active and user.seller:
                    login(request, user)
                    return redirect(reverse('vendor_dashboard'))
            except Seller.DoesNotExist:
                messages.warning(request, 'Seller account with this credentials does not exists', extra_tags="no_seller")
        else:
            messages.warning(request, 'Password or username is not correct!', extra_tags="seller_login")
            return redirect(reverse('seller_login_view'))
    else:
        login_form = SellerLoginForm()

    context = {
        'categories': mainmodels.Subcategories.objects.all(),
        'login_form': LoginForm()
    }

    return render(request, 'user/seller_login.html', context)


def vendor_dashboard(request):
    return render(request, 'user/vendor_dashboard.html', {'categories': mainmodels.Subcategories.objects.all(),})