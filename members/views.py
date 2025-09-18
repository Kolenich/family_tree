from django.db.models import Q
from django.views.generic import DetailView, ListView

from .models import Person


# Create your views here.
class PersonListView(ListView):
    context_object_name = 'persons'
    template_name = 'person_list.html'

    def get_queryset(self):
        queryset = Person.objects.order_by('date_of_birth')

        if self.request.GET.get('q'):
            q = self.request.GET.get('q')
            criteria = Q(last_name__icontains=q) | Q(first_name__icontains=q) | Q(middle_name__icontains=q)
            queryset = queryset.filter(criteria)

        if self.request.GET.get('order_by'):
            order_by = self.request.GET.get('order_by')
            queryset = queryset.order_by(order_by)

        return queryset


class PersonDetailView(DetailView):
    model = Person
    template_name = 'person_detail.html'
