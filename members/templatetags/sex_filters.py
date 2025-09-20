from django import template
from django.db.models import QuerySet

from members.models import Person

register = template.Library()


@register.filter
def is_male(obj: Person | QuerySet[Person]) -> bool | QuerySet[Person]:
    """
    Проверяет, является ли объект мужчиной.
    Работает как с отдельными объектами, так и с QuerySet.
    """
    if isinstance(obj, QuerySet):
        # Для QuerySet возвращаем отфильтрованный QuerySet
        return obj.filter(sex='male')
    else:
        # Для отдельных объектов возвращаем boolean
        return hasattr(obj, 'sex') and obj.sex == 'male'


@register.filter
def is_female(obj: Person | QuerySet[Person]) -> bool | QuerySet[Person]:
    """
    Проверяет, является ли объект женщиной.
    Работает как с отдельными объектами, так и с QuerySet.
    """
    if isinstance(obj, QuerySet):
        return obj.filter(sex='female')
    else:
        return hasattr(obj, 'sex') and obj.sex == 'female'
