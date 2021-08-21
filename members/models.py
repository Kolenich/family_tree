from django.db import models, transaction
from django.db.models import Q
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
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None

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
    def children(self):
        return Person.objects.filter(Q(mother=self.pk) | Q(father=self.pk))

    @property
    def grandchildren(self):
        return Person.objects.none().union(*[child.children for child in self.children])

    @property
    def great_grandchildren(self):
        return Person.objects.none().union(*[grandchild.children for grandchild in self.grandchildren])

    @property
    def siblings(self):
        queryset = Person.objects.none()
        if self.father:
            queryset = queryset | self.father.children
        if self.mother:
            queryset = queryset | self.mother.children
        return queryset.exclude(pk=self.pk)

    @property
    def uncles_and_aunties(self):
        queryset = Person.objects.none()
        if self.father:
            queryset = queryset | self.father.siblings
        if self.mother:
            queryset = queryset | self.mother.siblings
        return queryset

    @property
    def cousins(self):
        return Person.objects.none().union(*[person.children for person in self.uncles_and_aunties])

    @property
    def nephews_and_nieces(self):
        return Person.objects.none().union(*[person.children for person in self.siblings])

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
        assert person not in [self.mother, self.father], 'Cannot mary your parent'
        assert person not in self.children, 'Cannot mary your child'
        assert person not in self.grandchildren, 'Cannot mary your grandchild'
        assert person not in self.great_grandchildren, 'Cannot mary your great-grandchild'
        assert person not in self.siblings, 'Cannot mary your sibling'
        assert person not in self.cousins, 'Cannot mary your cousin'
        assert person not in self.uncles_and_aunties, 'Cannot mary your uncle/auntie'
        assert person not in self.nephews_and_nieces, 'Cannot mary your nephew/niece'

        self.spouse = person
        person.spouse = self

        self.save(update_fields=['spouse'])
        person.save(update_fields=['spouse'])
