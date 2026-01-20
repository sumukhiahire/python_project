from django.contrib import admin
from .models import Student, Meal, MealConsumption

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'grade', 'dietary_restrictions', 'created_at')
    search_fields = ('student_id', 'name', 'grade')
    list_filter = ('grade', 'created_at')

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('name', 'meal_type', 'serving_date', 'calories')
    search_fields = ('name', 'description')
    list_filter = ('meal_type', 'serving_date')
    date_hierarchy = 'serving_date'

@admin.register(MealConsumption)
class MealConsumptionAdmin(admin.ModelAdmin):
    list_display = ('student', 'meal', 'consumed_at', 'portion_consumed', 'waste_weight')
    search_fields = ('student__name', 'meal__name')
    list_filter = ('consumed_at', 'portion_consumed')
    date_hierarchy = 'consumed_at'
