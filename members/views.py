from django.db.models import Q
from django.views.generic import DetailView, ListView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .models import Person


# Create your views here.
class PersonListView(ListView):
    context_object_name = 'persons'
    template_name = 'person_list.html'

    def get_queryset(self):
        queryset = Person.objects.order_by('date_of_birth')

        if self.request.GET.get('search'):
            search = self.request.GET.get('search')
            criteria = Q(last_name__icontains=search) | Q(first_name__icontains=search) | Q(
                middle_name__icontains=search)
            queryset = queryset.filter(criteria)

        if self.request.GET.get('order_by'):
            order_by = self.request.GET.get('order_by')
            queryset = queryset.order_by(order_by)

        return queryset


class PersonDetailView(DetailView):
    model = Person
    template_name = 'person_detail.html'

    @method_decorator(cache_page(60 * 15))  # Кэшируем на 15 минут
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
