from django.contrib import admin

from .models import Person


# Register your models here.
@admin.register(Person)
class PersonAdminForm(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'father':
            kwargs['queryset'] = Person.objects.filter(sex='male')
        elif db_field.name == 'mother':
            kwargs['queryset'] = Person.objects.filter(sex='female')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
