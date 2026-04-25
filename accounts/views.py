from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .forms import RegisterForm
from .models import VerificationCode


# 🔹 LOGIN
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid data'})

    return render(request, 'accounts/login.html')


# 🔹 LOGOUT
def logout_view(request):
    logout(request)
    return redirect('login')


# 🔹 HOME
def home_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    return render(request, 'accounts/home.html')


# 🔹 REGISTER
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']

            code = str(random.randint(100000, 999999))

            VerificationCode.objects.create(email=email, code=code)

            send_mail(
                'Verification Code',
                f'Your code is: {code}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            request.session['user_data'] = form.cleaned_data
            return redirect(f'/verify/?email={email}')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


# 🔹 VERIFY
def verify_view(request):
    email = request.GET.get('email')

    if request.method == "POST":
        code = request.POST.get('code')

        try:
            record = VerificationCode.objects.get(email=email, code=code)

            data = request.session.get('user_data')

            User.objects.create_user(
                username=data['username'],
                email=email,
                password=data['password']
            )

            record.delete()
            return redirect('login')

        except VerificationCode.DoesNotExist:
            return render(request, 'accounts/verify.html', {'error': 'Invalid code'})

    return render(request, 'accounts/verify.html')