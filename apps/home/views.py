# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template, forms
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from urllib import request
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Expense, Income, Project
from django.shortcuts import  render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages, auth
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.db.models import Count, F, Sum, Avg
from django.db.models.functions import ExtractYear, ExtractMonth
from django.http import JsonResponse
from .charts import months, colorPrimary, colorSuccess, colorDanger, generate_color_palette, get_year_dict




# @login_required(login_url="/login/")
# def index(request):
#     context = {'segment': 'index'}

#     html_template = loader.get_template('home/index.html')
#     return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

def get_expense_filter_options(request):
    grouped_expenses = Expense.objects.filter(user=request.user).annotate(year=ExtractYear('date')).values('year').order_by('-year').distinct()
    options = [expense['year'] for expense in grouped_expenses]

    return JsonResponse({
        'options': options,
    })

def get_income_filter_options(request):
    grouped_incomes = Income.objects.filter(user=request.user).annotate(year=ExtractYear('date')).values('year').order_by('-year').distinct()
    options = [income['year'] for income in grouped_incomes]

    return JsonResponse({
        'options': options,
    })
    
def get_expense_year_chart(request, year):
    expenses = Expense.objects.filter(date__year=year)
    grouped_expenses = expenses.filter(user=request.user).annotate(Total=F('amount')).annotate(month=ExtractMonth('date'))\
        .values('month').annotate(average=Sum('amount')).values('month', 'average').order_by('month')

    expense_dict = get_year_dict()

    for group in grouped_expenses:
        expense_dict[months[group['month']-1]] = round(group['average'], 2)

    return JsonResponse({
        'title': f'Total Expense in {year}',
        'data': {
            'labels': list(expense_dict.keys()),
            'datasets': [{
                'label': 'Amount ($)',
                'backgroundColor': colorPrimary,
                'borderColor': colorPrimary,
                'data': list(expense_dict.values()),
            }]
        },
    })
    
class IndexView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'home/index.html'
    model= Expense
    #paginate_by = 4
    
    
    def get_context_data(self, **kwargs):
         # Call the base implementation first to get a context
        context=super(IndexView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all other contexts
        context['expense_list']=Expense.objects.filter(user=self.request.user).order_by('-date')[:5]
        context['income_list']=Income.objects.filter(user=self.request.user).order_by('-date')[:5]
        project_list = Project.objects.filter(user=self.request.user).order_by('-updated')
        context['project_list'] = project_list
        context['current_user']= self.request.user.first_name
        context['project_count'] = Project.objects.filter(user=self.request.user).count()
        #context[amount_spent]= amount_spent(project_name)
        return context

def charts_view(request):
    return render(request, 'home/charts.html', {})
class ExpenseDetailView(LoginRequiredMixin,generic.DetailView):
    model = Expense

class IncomeDetailView(LoginRequiredMixin,generic.DetailView):
    model = Income  

# class CreateCompany(CreateView, LoginRequiredMixin):
#     model= Company
#     fields= ['name', 'industry','code']
    
#     def form_valid(self, form):
#         form.instance.user = self.request.user
#         return super().form_valid(form)

# class AllCompany(generic.ListView, LoginRequiredMixin):
#     model= Company

# class DeleteCompany(DeleteView, LoginRequiredMixin):
#     model= Company
#     success_url= reverse_lazy('all-projects')
 
class CreateExpenseView(CreateView, LoginRequiredMixin):
    model= Expense
    fields= ['category', 'amount', 'date', 'description', 'project_name']
    
    
    def get_form_class(self):
        modelform = super().get_form_class()
        modelform.base_fields['project_name'].limit_choices_to = {'user': self.request.user}
        modelform.base_fields['date'].widget= forms.DateInput(attrs={'type': 'date'})
        modelform.base_fields['description'].widget= forms.Textarea(attrs={'rows':2, 'cols':15})
        return modelform
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
  
class Profile(generic.DetailView, LoginRequiredMixin):
    model = User

class UpdateExpenseView(UpdateView, LoginRequiredMixin):
    model= Expense
    fields= ['category', 'amount', 'date', 'description', 'project_name']
    
    def get_form_class(self):
        modelform = super().get_form_class()
        modelform.base_fields['project_name'].limit_choices_to = {'user': self.request.user}
        modelform.base_fields['date'].widget= forms.DateInput(attrs={'type': 'date'})
        modelform.base_fields['description'].widget= forms.Textarea(attrs={'rows':2, 'cols':15})
        return modelform
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
class DeleteExpenseView(DeleteView, LoginRequiredMixin):
    model= Expense
    success_url= reverse_lazy('all-expenses')
    
class CreateIncomeView(CreateView, LoginRequiredMixin):
    model= Income
    fields= ['category', 'amount', 'date', 'description', 'project_name']
    
    def get_form_class(self):
        modelform = super().get_form_class()
        modelform.base_fields['project_name'].limit_choices_to = {'user': self.request.user}
        modelform.base_fields['date'].widget= forms.DateInput(attrs={'type': 'date'})
        modelform.base_fields['description'].widget= forms.Textarea(attrs={'rows':2, 'cols':15})
        return modelform
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
class UpdateIncomeView(UpdateView, LoginRequiredMixin):
    model= Income
    fields= '__all__'
    
    def get_form_class(self):
        modelform = super().get_form_class()
        modelform.base_fields['project_name'].limit_choices_to = {'user': self.request.user}
        modelform.base_fields['date'].widget= forms.DateInput(attrs={'type': 'date'})
        modelform.base_fields['description'].widget= forms.Textarea(attrs={'rows':2, 'cols':15})
        return modelform
    
class DeleteIncomeView(DeleteView, LoginRequiredMixin):
    model= Income
    success_url= reverse_lazy('all-incomes')
    
class AllExpensesView(generic.ListView, LoginRequiredMixin):
    template_name = 'home/all_expenses.html'
    model= Expense
    paginate_by = 10
    
class AllIncomesView(generic.ListView, LoginRequiredMixin):
    template_name = 'home/all_incomes.html'
    model= Income
    paginate_by = 10
    
class CreateProject(CreateView, LoginRequiredMixin):
    model= Project
    fields= ['project_name', 'project_amount', 'start_date', 'end_date']
    
    def get_form_class(self):
        modelform = super().get_form_class()
        modelform.base_fields['start_date'].widget= forms.DateInput(attrs={'type': 'date'})
        modelform.base_fields['end_date'].widget= forms.DateInput(attrs={'type': 'date'})
        modelform.base_fields['description'].widget= forms.Textarea(attrs={'rows':2, 'cols':15})
        return modelform
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
      
    
class UpdateProject(UpdateView, LoginRequiredMixin):
    model= Project
    fields="__all__"
    
class DeleteProject(DeleteView, LoginRequiredMixin):
    model= Project
    success_url= 'all-projects'
 
class ProjectList(generic.ListView, LoginRequiredMixin):
    model= Project
    template_name= 'home/all_projects.html'  
class ProjectDetail(generic.DetailView, LoginRequiredMixin):
    model= Project
    
    