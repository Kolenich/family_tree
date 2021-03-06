from django.db import models, transaction
from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils import timezone


# Create your models here.

class Person(models.Model):
    """Член дерева."""

    SEX = (
        ('male', 'Муж.'),
        ('female', 'Жен.'),
    )

    last_name = models.CharField('Фамилия', max_length=64)
    first_name = models.CharField('Имя', max_length=64)
    middle_name = models.CharField('Отчество', max_length=64, blank=True, null=True)
    date_of_birth = models.DateField('Дата рождения')
    date_of_death = models.DateField('Дата смерти', blank=True, null=True)
    sex = models.CharField('Пол', choices=SEX, max_length=6)
    avatar = models.ImageField('Аватар', blank=True, null=True)
    # Семейные связи первого уровня
    mother = models.ForeignKey('self', verbose_name='Мать', on_delete=models.SET_NULL, blank=True, null=True,
                               related_name='mother_of')
    father = models.ForeignKey('self', verbose_name='Отец', on_delete=models.SET_NULL, blank=True, null=True,
                               related_name='father_of')
    spouse = models.OneToOneField('self', verbose_name='Супруг/супруга', on_delete=models.SET_NULL, null=True,
                                  blank=True)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Член дерева'
        verbose_name_plural = 'Члены дерева'
        db_table = 'persons'

    @property
    def age(self):
        delta = timezone.now().date() - self.date_of_birth
        if self.date_of_death:
            delta = self.date_of_death - self.date_of_birth
        return (delta / 365.25).days

    @property
    def full_name(self):
        if self.middle_name:
            return f'{self.last_name} {self.first_name} {self.middle_name}'
        return f'{self.last_name} {self.first_name}'

    @property
    def short_name(self):
        if self.middle_name:
            return f'{self.last_name} {self.first_name[0]}.{self.middle_name[0]}.'
        return f'{self.last_name} {self.first_name[0]}.'

    @property
    def kin(self):
        queryset = Person.objects.none()

        for prop in filter(lambda x: not x.startswith('_') and x not in ('kin', 'objects'), dir(self)):
            instance = getattr(self, prop)
            if isinstance(instance, QuerySet):
                queryset |= instance

        return queryset

    @property
    def children(self):
        return Person.objects.none() | self.father_of.all() | self.mother_of.all()

    @property
    def grandchildren(self):
        queryset = Person.objects.none()
        for child in self.children:
            queryset |= child.children
        return queryset

    @property
    def great_grandchildren(self):
        queryset = Person.objects.none()
        for grandchild in self.grandchildren:
            queryset |= grandchild.children
        return queryset

    @property
    def parents(self):
        return Person.objects.filter(Q(pk=self.mother_id) | Q(pk=self.father_id))

    @property
    def grandparents(self):
        queryset = Person.objects.none()
        for parent in self.parents:
            queryset |= parent.parents
        return queryset

    @property
    def great_grandparents(self):
        queryset = Person.objects.none()
        for grandparent in self.grandparents:
            queryset |= grandparent.parents
        return queryset

    @property
    def siblings(self):
        return Person.objects \
            .filter(mother=self.mother, mother__isnull=False, father=self.father, father__isnull=False) \
            .exclude(pk=self.pk)

    @property
    def step_siblings(self):
        queryset = Person.objects.none()
        if self.father:
            queryset = queryset | self.father.children
        if self.mother:
            queryset = queryset | self.mother.children
        return queryset.exclude(pk__in=[*self.siblings.values_list('pk', flat=True), self.pk])

    @property
    def uncles_and_aunties(self):
        queryset = Person.objects.none()
        if self.father:
            queryset = queryset | self.father.siblings | self.father.step_siblings
        if self.mother:
            queryset = queryset | self.mother.siblings | self.mother.step_siblings
        return queryset

    @property
    def cousins(self):
        queryset = Person.objects.none()
        for person in self.uncles_and_aunties:
            queryset |= person.children
        return queryset

    @property
    def second_cousins(self):
        queryset = Person.objects.none()
        for cousin in self.cousins:
            queryset |= cousin.children
        return queryset

    @property
    def nephews_and_nieces(self):
        queryset = Person.objects.none()
        for person in [*self.siblings, *self.step_siblings]:
            queryset |= person.children
        return queryset

    @transaction.atomic
    def mary(self, person):
        """
        Добавление супруга/супруги.

        :param person: добавляемый человек
        :return:
        """
        assert self.sex != person.sex, 'No single sex marriage allowed'
        assert self.spouse is None, f'You must first divorce with {self.spouse}'
        assert self.spouse != person, f'{self} and {person} already married'
        assert person.spouse is None, f'{person} already married on {person.spouse}'
        assert person not in self.kin, 'Cannot mary your kin'

        self.spouse = person
        person.spouse = self

        self.save(update_fields=['spouse'])
        person.save(update_fields=['spouse'])
