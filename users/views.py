from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import LoginUserForm, RegisterUsersForm
from library.models import Book
from django.views.generic import CreateView
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib import messages
from .models import User
from django.contrib.auth.decorators import login_required

# Create your views here.
class LoginUser(LoginView): 
    form_class = LoginUserForm
    template_name = 'users/login.html'
    redirect_authenticated_user=True

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)

    def get_success_url(self):
        return self.request.GET.get('next') or reverse_lazy('home')


class RegisterUser(CreateView):
    form_class = RegisterUsersForm
    template_name = 'users/register.html'
    success_url = reverse_lazy("users:login")
    
    def dispatch(self, request, *args, **kwargs):
        # Redirect authenticated users to the home page (or another page)
        if request.user.is_authenticated:
            return redirect('home')  # Replace 'home' with your desired URL name
        return super().dispatch(request, *args, **kwargs)
    
    


class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset.html'  # Custom template
    email_template_name = 'users/password_reset_email.html'  # Custom email template
    success_url = reverse_lazy('users:password_reset_done')  # Redirect after submitting form



class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'  # Custom template
    success_url = reverse_lazy('users:password_reset_complete')  # Redirect after success



@login_required
def user_profile(request, username):
    # if not request.user.is_authenticated:
    #     messages.warning(request, "You need to log in to view profiles.")
        

    user = get_object_or_404(User, username=username)

    if request.user != user:
        return redirect('users:user_profile', username=request.user.username)

    return render(request, 'users/profile.html', {'user': user})