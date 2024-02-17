from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.http import HttpResponse
from django.utils import timezone
from django.db import IntegrityError
from .models import Task
from django.contrib.auth.decorators import login_required
from .forms import TaskForm
def signup(request):

    if request.method=="GET":
        return render(request, "signup.html",{
        'form': UserCreationForm
    })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                #Register user
                user =User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request,user)
                return redirect('tasks')
            except IntegrityError:
                 return render(request, "signup.html",{
                'form': UserCreationForm,
                "error" : "Username already exists"
                })
        return render(request, "signup.html",{
                'form': UserCreationForm,
                "error" : "Password do not match"
                })


def signin(request):

    if request.method == "GET":
        return render(request, 'signin.html',
                  {'form':AuthenticationForm})
    
    else:
       user= authenticate(request,username=request.POST['username'],password=request.POST['password'])
       if user is None:
           return render(request, 'signin.html',
                  {'form':AuthenticationForm,
                   'error':"Username or password is incorrect"})
       else:
           login(request,user)

           return redirect('tasks')
@login_required           
def signout(request):
    logout(request)
    return redirect('home')

@login_required
def tasks(request):

    
    tasks=Task.objects.filter(user=request.user,datecompleted__isnull=True)

    return render(request,'tasks.html', {'tasks':tasks})
    
def home(request):

    return render(request, "home.html")

@login_required
def create_task(request):
    Tasks= TaskForm
    if request.method == "GET":
    
        return render(request,'create_task.html',
                    {'Task': Tasks})
    
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user=request.user #Asociación con el usuario que creo la tarea
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request,'create_task.html',
                    {'Task': Tasks,
                     'error':"Please provide valida data"})

@login_required
def task_detail(request,id):

    if request.method=="GET":
        task=get_object_or_404(Task,pk=id, user=request.user)
        form=TaskForm(instance=task)
        return render(request, 'task_detail.html',
                    {'task':task,
                     'form':form})

    else:
        try:
            task=get_object_or_404(Task,pk=id,user=request.user)
            form=TaskForm(request.POST, instance=task)
            form.save()

            return redirect('tasks')
        except ValueError:    
            return render(request, 'task_detail.html',
                        {'task':task,
                        'form':form,
                        'error':'Error Update Task'})


@login_required
def complete_task(request,id):   
    task=get_object_or_404(Task,pk=id,user=request.user)
    if request.method=="POST":
        task.datecompleted = timezone.now()
        task.save()

        return redirect('tasks')
    
@login_required
def delete_task(request,id):   
    task=get_object_or_404(Task,pk=id,user=request.user)
    if request.method=="POST":
        task.delete()

        return redirect('tasks')

@login_required
def tasks_completed(request):

    
    tasks=Task.objects.filter(user=request.user,datecompleted__isnull=False).order_by('-datecompleted')

    return render(request,'tasks.html', {'tasks':tasks})