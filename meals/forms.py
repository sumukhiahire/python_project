from django import forms
from .models import Student, Meal, MealConsumption

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_id', 'name', 'grade', 'dietary_restrictions']
        widgets = {
            'dietary_restrictions': forms.Textarea(attrs={'rows': 3}),
        }

class MealForm(forms.ModelForm):
    meal_type = forms.ChoiceField(
        choices=Meal.MEAL_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    protein = forms.FloatField(min_value=0)
    carbohydrates = forms.FloatField(min_value=0)
    fats = forms.FloatField(min_value=0)

    class Meta:
        model = Meal
        fields = ['name', 'meal_type', 'serving_date', 'description', 'protein', 'carbohydrates', 'fats']
        widgets = {
            'meal_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'serving_date': forms.DateInput(attrs={'type': 'date', 'required': True}),
            'name': forms.TextInput(attrs={'required': True}),
        }
        error_messages = {
            'name': {'required': 'Meal name is required'},
            'serving_date': {'required': 'Serving date is required'}
        }

class MealConsumptionForm(forms.ModelForm):
    class Meta:
        model = MealConsumption
        fields = ['student', 'meal', 'portion_consumed', 'waste_weight']
        widgets = {
            'portion_consumed': forms.NumberInput(attrs={'step': '0.1', 'min': '0', 'max': '1'}),
            'waste_weight': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
        }



class MealSearchForm(forms.Form):
    meal_type = forms.ChoiceField(
        choices=[('', 'All')] + Meal.MEAL_TYPES,
        required=False
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

class StudentSearchForm(forms.Form):
    grade = forms.CharField(required=False)
    name = forms.CharField(required=False)