from django.db.models import Q
from django.views.generic import DetailView, ListView

from .models import Person


# Create your views here.
class PersonListView(ListView):
    model = Person
    context_object_name = 'persons'
    template_name = 'person_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.GET.get('q'):
            q = self.request.GET.get('q')
            criteria = Q(last_name__icontains=q) | Q(first_name__icontains=q) | Q(middle_name__icontains=q)
            queryset = queryset.filter(criteria)

        return queryset


class PersonDetailView(DetailView):
    model = Person
    context_object_name = 'person'
    template_name = 'person_detail.html'
