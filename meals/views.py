from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Avg, Sum, Count
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from .models import Student, Meal, MealConsumption
from .forms import StudentForm, MealForm, MealConsumptionForm, MealSearchForm, StudentSearchForm

# Dashboard Views
def dashboard(request):
    # Get counts for summary statistics
    total_students = Student.objects.count()
    total_meals = Meal.objects.count()
    total_consumptions = MealConsumption.objects.count()
    
    # Calculate total waste
    total_waste = MealConsumption.objects.aggregate(Sum('waste_weight'))['waste_weight__sum'] or 0
    
    # Get recent meals (last 7 days)
    recent_date = timezone.now().date() - timedelta(days=7)
    recent_meals = Meal.objects.filter(serving_date__gte=recent_date).order_by('-serving_date')
    
    context = {
        'total_students': total_students,
        'total_meals': total_meals,
        'total_consumptions': total_consumptions,
        'total_waste': round(total_waste, 2),
        'recent_meals': recent_meals,
    }
    
    return render(request, 'meals/dashboard.html', context)

# Student Views
class StudentListView(ListView):
    model = Student
    template_name = 'meals/student_list.html'
    context_object_name = 'students'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = StudentSearchForm(self.request.GET or None)
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        form = StudentSearchForm(self.request.GET or None)
        
        if form.is_valid():
            name = form.cleaned_data.get('name')
            grade = form.cleaned_data.get('grade')
            
            if name:
                queryset = queryset.filter(name__icontains=name)
            if grade:
                queryset = queryset.filter(grade__icontains=grade)
                
        return queryset

class StudentDetailView(DetailView):
    model = Student
    template_name = 'meals/student_detail.html'
    context_object_name = 'student'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        
        # Get student's meal consumption history
        context['consumptions'] = MealConsumption.objects.filter(student=student).order_by('-consumed_at')
        
        return context

class StudentCreateView(CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'meals/student_form.html'
    success_url = reverse_lazy('student-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Student created successfully!')
        return super().form_valid(form)

class StudentUpdateView(UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'meals/student_form.html'
    success_url = reverse_lazy('student-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Student updated successfully!')
        return super().form_valid(form)

class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'meals/student_confirm_delete.html'
    success_url = reverse_lazy('student-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Student deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Meal Views
class MealListView(ListView):
    model = Meal
    template_name = 'meals/meal_list.html'
    context_object_name = 'meal_list'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = MealSearchForm(self.request.GET or None)
        
        # Calculate calories for each meal (4cal/g protein & carbs, 9cal/g fat)
        for meal in context['meal_list']:
            meal.calories = 4 * (meal.protein + meal.carbohydrates) + 9 * meal.fats
        
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        form = MealSearchForm(self.request.GET or None)
        
        if form.is_valid():
            meal_type = form.cleaned_data.get('meal_type')
            date_from = form.cleaned_data.get('date_from')
            date_to = form.cleaned_data.get('date_to')
            
            if meal_type:
                queryset = queryset.filter(meal_type=meal_type)
            if date_from:
                queryset = queryset.filter(serving_date__gte=date_from)
            if date_to:
                queryset = queryset.filter(serving_date__lte=date_to)
                
        return queryset.order_by('-serving_date')

class MealDetailView(DetailView):
    model = Meal
    template_name = 'meals/meal_detail.html'
    context_object_name = 'meal'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        meal = self.get_object()
        
        # Get consumption data for this meal
        consumptions = MealConsumption.objects.filter(meal=meal)
        context['consumptions'] = consumptions
        
        # Calculate consumption statistics
        total_consumptions = consumptions.count()
        if total_consumptions > 0:
            avg_portion = consumptions.aggregate(Avg('portion_consumed'))['portion_consumed__avg']
            total_waste = consumptions.aggregate(Sum('waste_weight'))['waste_weight__sum'] or 0
        else:
            avg_portion = 0
            total_waste = 0
            
        context['total_consumptions'] = total_consumptions
        context['avg_portion'] = round(avg_portion, 2) if avg_portion else 0
        context['total_waste'] = round(total_waste, 2)
        
        # Get consumption statistics for this meal
        consumptions = MealConsumption.objects.filter(meal=meal)
        context['consumptions'] = consumptions
        
        return context

class MealCreateView(CreateView):
    model = Meal
    form_class = MealForm
    template_name = 'meals/meal_form.html'
    success_url = reverse_lazy('meal-list')

    def form_valid(self, form):
        try:
            meal = form.save(commit=False)
            # Calculate calories (4cal/g protein & carbs, 9cal/g fat)
            meal.calories = int(4 * (meal.protein + meal.carbohydrates) + 9 * meal.fats)
            response = super().form_valid(form)
            messages.success(self.request, 'Meal created successfully!')
            return response
        except Exception as e:
            messages.error(self.request, f'Error saving meal: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field.title()}: {error}')
        return super().form_invalid(form)

class MealUpdateView(UpdateView):
    model = Meal
    form_class = MealForm
    template_name = 'meals/meal_form.html'
    success_url = reverse_lazy('meal-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Meal updated successfully!')
        return super().form_valid(form)

class MealDeleteView(DeleteView):
    model = Meal
    template_name = 'meals/meal_confirm_delete.html'
    success_url = reverse_lazy('meal-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Meal deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Meal Consumption Views
class MealConsumptionListView(ListView):
    model = MealConsumption
    template_name = 'meals/consumption_list.html'
    context_object_name = 'consumptions'
    ordering = ['-consumed_at']

class MealConsumptionCreateView(CreateView):
    model = MealConsumption
    form_class = MealConsumptionForm
    template_name = 'meals/consumption_form.html'
    success_url = reverse_lazy('consumption-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Meal consumption recorded successfully!')
        return super().form_valid(form)

# Reports Views
def nutrition_report(request):
    # Get all meals
    meals = Meal.objects.all()
    
    # Calculate average nutritional values
    avg_values = meals.aggregate(
        Avg('calories'),
        Avg('protein'),
        Avg('carbohydrates'),
        Avg('fats')
    )
    
    # Meal type analysis
    meal_type_analysis = meals.values('meal_type').annotate(
        avg_calories=Avg('calories'),
        avg_protein=Avg('protein'),
        avg_carbs=Avg('carbohydrates'),
        avg_fats=Avg('fats'),
        total_meals=Count('id')
    ).order_by('meal_type')
    
    context = {
        'meals': meals,
        'avg_calories': round(avg_values['calories__avg'] or 0, 1),
        'avg_protein': round(avg_values['protein__avg'] or 0, 1),
        'avg_carbs': round(avg_values['carbohydrates__avg'] or 0, 1),
        'avg_fats': round(avg_values['fats__avg'] or 0, 1),
        'meal_type_analysis': meal_type_analysis
    }
    
    return render(request, 'meals/nutrition_report.html', context)
    
    # Calculate averages by meal type
    breakfast_avg = {
        'calories': breakfast_meals.aggregate(Avg('calories'))['calories__avg'] or 0,
        'protein': breakfast_meals.aggregate(Avg('protein'))['protein__avg'] or 0,
        'carbs': breakfast_meals.aggregate(Avg('carbohydrates'))['carbohydrates__avg'] or 0,
        'fats': breakfast_meals.aggregate(Avg('fats'))['fats__avg'] or 0,
    }
    
    lunch_avg = {
        'calories': lunch_meals.aggregate(Avg('calories'))['calories__avg'] or 0,
        'protein': lunch_meals.aggregate(Avg('protein'))['protein__avg'] or 0,
        'carbs': lunch_meals.aggregate(Avg('carbohydrates'))['carbohydrates__avg'] or 0,
        'fats': lunch_meals.aggregate(Avg('fats'))['fats__avg'] or 0,
    }
    
    snack_avg = {
        'calories': snack_meals.aggregate(Avg('calories'))['calories__avg'] or 0,
        'protein': snack_meals.aggregate(Avg('protein'))['protein__avg'] or 0,
        'carbs': snack_meals.aggregate(Avg('carbohydrates'))['carbohydrates__avg'] or 0,
        'fats': snack_meals.aggregate(Avg('fats'))['fats__avg'] or 0,
    }
    
    # Calculate additional nutritional metrics
    average_fiber = meals.aggregate(Avg('fiber'))['fiber__avg'] or 0
    average_sodium = meals.aggregate(Avg('sodium'))['sodium__avg'] or 0
    average_sugar = meals.aggregate(Avg('sugar'))['sugar__avg'] or 0
    average_iron = meals.aggregate(Avg('iron'))['iron__avg'] or 0

    # Prepare meal type analysis
    meal_type_analysis = [
        {
            'name': 'Breakfast',
            'avg_calories': breakfast_meals.aggregate(Avg('calories'))['calories__avg'] or 0,
            'avg_protein': breakfast_meals.aggregate(Avg('protein'))['protein__avg'] or 0,
            'avg_carbs': breakfast_meals.aggregate(Avg('carbohydrates'))['carbohydrates__avg'] or 0,
            'avg_fats': breakfast_meals.aggregate(Avg('fats'))['fats__avg'] or 0,
            'common_items': ', '.join(breakfast_meals.values_list('name', flat=True)[:3])
        },
        {
            'name': 'Lunch',
            'avg_calories': lunch_meals.aggregate(Avg('calories'))['calories__avg'] or 0,
            'avg_protein': lunch_meals.aggregate(Avg('protein'))['protein__avg'] or 0,
            'avg_carbs': lunch_meals.aggregate(Avg('carbohydrates'))['carbohydrates__avg'] or 0,
            'avg_fats': lunch_meals.aggregate(Avg('fats'))['fats__avg'] or 0,
            'common_items': ', '.join(lunch_meals.values_list('name', flat=True)[:3])
        },
        {
            'name': 'Snack',
            'avg_calories': snack_meals.aggregate(Avg('calories'))['calories__avg'] or 0,
            'avg_protein': snack_meals.aggregate(Avg('protein'))['protein__avg'] or 0,
            'avg_carbs': snack_meals.aggregate(Avg('carbohydrates'))['carbohydrates__avg'] or 0,
            'avg_fats': snack_meals.aggregate(Avg('fats'))['fats__avg'] or 0,
            'common_items': ', '.join(snack_meals.values_list('name', flat=True)[:3])
        }
    ]

    # Define dietary requirements and calculate compliance
    dietary_requirements = [
        {
            'name': 'Balanced Protein Intake',
            'compliance': min(100, (avg_protein / 50) * 100),
            'description': 'Daily protein intake should be at least 50g'
        },
        {
            'name': 'Controlled Sugar',
            'compliance': max(0, 100 - (average_sugar / 30) * 100),
            'description': 'Daily sugar intake should be below 30g'
        },
        {
            'name': 'Adequate Fiber',
            'compliance': min(100, (average_fiber / 25) * 100),
            'description': 'Daily fiber intake should be at least 25g'
        }
    ]

    context = {
        'avg_calories': round(avg_calories, 1),
        'avg_protein': round(avg_protein, 1),
        'avg_carbs': round(avg_carbs, 1),
        'avg_fats': round(avg_fats, 1),
        'breakfast_avg': {k: round(v, 1) for k, v in breakfast_avg.items()},
        'lunch_avg': {k: round(v, 1) for k, v in lunch_avg.items()},
        'snack_avg': {k: round(v, 1) for k, v in snack_avg.items()},
        'meals': meals,
        'average_fiber': round(average_fiber, 1),
        'average_sodium': round(average_sodium, 1),
        'average_sugar': round(average_sugar, 1),
        'average_iron': round(average_iron, 1),
        'meal_type_analysis': meal_type_analysis,
        'dietary_requirements': dietary_requirements
    }
    
    return render(request, 'meals/nutrition_report.html', context)

def waste_report(request):
    # Get all consumptions
    consumptions = MealConsumption.objects.all()
    
    # Calculate total waste
    total_waste = consumptions.aggregate(Sum('waste_weight'))['waste_weight__sum'] or 0
    
    # Calculate average waste per meal
    avg_waste_per_meal = consumptions.values('meal').annotate(
        avg_waste=Avg('waste_weight'),
        total_waste=Sum('waste_weight'),
        count=Count('id')
    ).order_by('-avg_waste')
    
    # Get meals with highest waste
    meals_with_waste = []
    for item in avg_waste_per_meal:
        meal = Meal.objects.get(id=item['meal'])
        meals_with_waste.append({
            'meal': meal,
            'avg_waste': round(item['avg_waste'] or 0, 2),
            'total_waste': round(item['total_waste'] or 0, 2),
            'count': item['count']
        })
    
    context = {
        'total_waste': round(total_waste, 2),
        'meals_with_waste': meals_with_waste,
        'consumptions': consumptions,
    }
    
    return render(request, 'meals/waste_report.html', context)
