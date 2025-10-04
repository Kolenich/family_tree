from django.db.models import Q
from django.views.generic import DetailView, ListView

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

    def get_queryset(self):
        return (
            Person.objects
            .select_related(
                'father',
                'father__father',
                'father__father__mother',
                'father__father__father',
                'father__mother',
                'father__mother__father',
                'father__mother__mother',
                'mother',
                'mother__mother',
                'mother__father',
                'spouse'
            ).prefetch_related(
                'father_of',
                'mother_of',
                'father_of__father_of',
                'mother_of__mother_of',
                'father_of__father_of__father_of',
                'mother_of__mother_of__mother_of'
            )
        )
