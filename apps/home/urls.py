# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.IndexView.as_view(), name='home'),

    # Matches any html file
    #re_path(r'^.*\.*', views.pages, name='pages'),
    #path('profile/<username>', views.Profile.as_view(), name = 'profile'),
    path('expense/add', views.CreateExpenseView.as_view(), name='expense-add'),
    path('income/add', views.CreateIncomeView.as_view(), name='income-add'),
    path('project/add', views.CreateProject.as_view(), name='project-add'),
    path('expense/all', views.AllExpensesView.as_view(), name='all-expenses'),
    path('income/all', views.AllIncomesView.as_view(), name='all-incomes'),
    path('project/all', views.ProjectList.as_view(), name='all-projects'),
    path('expense/<str:pk>', views.ExpenseDetailView.as_view(), name='expense-detail'),
    path('income/<str:pk>', views.IncomeDetailView.as_view(), name='income-detail'),
    path('project/<str:pk>', views.ProjectDetail.as_view(), name='project-detail'),
    path('expense/<str:pk>/update', views.UpdateExpenseView.as_view(), name='expense-update'),
    path('income/<str:pk>/update', views.UpdateIncomeView.as_view(), name='income-update'),
    path('project/<str:pk>/update', views.UpdateProject.as_view(), name='project-update'),
    path('expense/<str:pk>/delete', views.DeleteExpenseView.as_view(), name='expense-delete'),
    path('income/<str:pk>/delete', views.DeleteIncomeView.as_view(), name='income-delete'),
    path('project/<str:pk>/delete', views.DeleteProject.as_view(), name='project-delete'),
    path('charts/', views.charts_view, name='charts'),
    path('chart/expense/filter-options/', views.get_expense_filter_options, name='expense-chart-filter-options'),
    path('chart/income/filter-options/', views.get_income_filter_options, name='income-chart-filter-options'),
    path('chart/expense/year/<int:year>/', views.get_expense_year_chart, name='expense-chart-year'),
    

]
