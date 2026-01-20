from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    grade = models.CharField(max_length=10)
    dietary_restrictions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.student_id})"

class Meal(models.Model):
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('snack', 'Snack')
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    serving_date = models.DateField()
    calories = models.IntegerField()
    protein = models.FloatField(help_text='Protein content in grams')
    carbohydrates = models.FloatField(help_text='Carbohydrates content in grams')
    fats = models.FloatField(help_text='Fats content in grams')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.serving_date}"

class MealConsumption(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    consumed_at = models.DateTimeField(auto_now_add=True)
    portion_consumed = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text='Portion consumed (0.0 to 1.0)'
    )
    waste_weight = models.FloatField(help_text='Food waste in grams', null=True, blank=True)

    class Meta:
        unique_together = ['student', 'meal', 'consumed_at']
