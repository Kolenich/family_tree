from django.db.models import Prefetch, Q
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
        return Person.objects.prefetch_related(
            'mother_of',
            'father_of',
            Prefetch('mother', queryset=Person.objects.prefetch_related('mother_of', 'father_of')),
            Prefetch('father', queryset=Person.objects.prefetch_related('mother_of', 'father_of')),
            'spouse'
        ).select_related(
            'mother',
            'father',
            'spouse'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person = self.object

        # Оптимизируем получение родственных связей
        related_kin_lists = {
            'Дети': person.kin_children,
            'Внуки': person.kin_grandchildren.filter(sex='male'),
            'Внучки': person.kin_grandchildren.filter(sex='female'),
            'Правнуки': person.kin_great_grandchildren.filter(sex='male'),
            'Правнучки': person.kin_great_grandchildren.filter(sex='female'),
            'Дедушки': person.kin_grandparents.filter(sex='male'),
            'Бабушки': person.kin_grandparents.filter(sex='female'),
            'Прадедушки': person.kin_great_grandparents.filter(sex='male'),
            'Прабабушки': person.kin_great_grandparents.filter(sex='female'),
            'Родные братья': person.kin_siblings.filter(sex='male'),
            'Родные сёстры': person.kin_siblings.filter(sex='female'),
            'Сводные братья': person.kin_step_siblings.filter(sex='male'),
            'Сводные сёстры': person.kin_step_siblings.filter(sex='female'),
            'Дяди': person.kin_uncles_and_aunties.filter(sex='male'),
            'Тёти': person.kin_uncles_and_aunties.filter(sex='female'),
            'Двоюродные братья': person.kin_cousins.filter(sex='male'),
            'Двоюродные сёстры': person.kin_cousins.filter(sex='female'),
            'Племянники': person.kin_nephews_and_nieces.filter(sex='male'),
            'Племянницы': person.kin_nephews_and_nieces.filter(sex='female')
        }

        # Добавляем оптимизацию для свойств модели
        for key, value in related_kin_lists.items():
            related_kin_lists[key] = value.prefetch_related(
                'mother',
                'father',
                'spouse'
            )

        context['related_kin_lists'] = related_kin_lists
        return context
