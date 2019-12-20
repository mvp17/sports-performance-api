from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic


class LogIn(LoginRequiredMixin, generic.CreateView):
    # form_class = SignUpForm
    success_url = reverse_lazy('home')
    template_name = 'registration/login.html'

