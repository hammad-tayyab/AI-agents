from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.views.generic import TemplateView

def home(request):
    return HttpResponse("Welcome to MalumAI")


def index(request):
    context = {
        'title': 'Home',
        'message': 'Hello from Django!'
    }
    return render(request, 'index.html', context)


class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home'
        return context


class CustomView(View):
    def get(self, request):
        return HttpResponse("Custom GET view")
    
    def post(self, request):
        return HttpResponse("Custom POST view")
    
