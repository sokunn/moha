from django.views.generic import FormView
from django.views.generic import TemplateView


class SearchResultView(TemplateView):
    template_name = '404.html'
