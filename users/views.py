from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model


from .forms import CreationForm

User = get_user_model()


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'
