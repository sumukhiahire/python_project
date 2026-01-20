from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Student URLs
    path('students/', views.StudentListView.as_view(), name='student-list'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
    path('students/create/', views.StudentCreateView.as_view(), name='student-create'),
    path('students/<int:pk>/update/', views.StudentUpdateView.as_view(), name='student-update'),
    path('students/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student-delete'),
    
    # Meal URLs
    path('meals/', views.MealListView.as_view(), name='meal-list'),
    path('meals/<int:pk>/', views.MealDetailView.as_view(), name='meal-detail'),
    path('meals/create/', views.MealCreateView.as_view(), name='meal-create'),
    path('meals/<int:pk>/update/', views.MealUpdateView.as_view(), name='meal-update'),
    path('meals/<int:pk>/delete/', views.MealDeleteView.as_view(), name='meal-delete'),
    
    # Consumption URLs
    path('consumptions/', views.MealConsumptionListView.as_view(), name='consumption-list'),
    path('consumptions/create/', views.MealConsumptionCreateView.as_view(), name='consumption-create'),
    

    
    # Reports URLs
    path('reports/nutrition/', views.nutrition_report, name='nutrition-report'),
    path('reports/waste/', views.waste_report, name='waste-report'),

]