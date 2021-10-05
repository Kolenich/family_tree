# Create your tests here.
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from .models import Person


class PersonTest(TestCase):
    def setUp(self):
        minor_past = timezone.now().date() - timedelta(days=30)
        self.person = Person.objects.create(first_name='John', last_name='Peters', sex='male', date_of_birth=minor_past)

    def test_person_age_is_positive(self):
        self.assertTrue(self.person.age >= 0)
