from django.shortcuts import render , redirect , get_object_or_404
from django.contrib.auth.forms import UserCreationForm , AuthenticationForm
from django.contrib import messages
from django.contrib.auth import authenticate , login , logout
from django.contrib.auth.decorators import login_required
from ToDos.models import ToDo
from .form import TodoForm

def login_view(request):  #若取名為login會與django內建方法撞名
    form = AuthenticationForm() 
    if request.method == 'POST' :
        form = AuthenticationForm(data = request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None :
                login(request , user)   #使用django內建方法
                messages.success(request , '登入成功')
                return redirect(todos)
        else :
            messages.error(request , '登入失敗')
    return render (request , 'login.html' , {'form':form})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm (request.POST)  #將POST的數據存入表單
        if form.is_valid(): #檢查表單數據是否有異常
            form.save()
            messages.success(request,'成功註冊')
            return redirect(login_view)
    else:   #GET請求時創建空白表單   
        form = UserCreationForm() 
    return render (request , 'register.html' , {'form' : form}) #當在GET請求或表單驗證失敗時顯示的畫面

@login_required(login_url='login_view') #若使用者透過get方法進入 則導向註冊畫面
def todos(request): 
    todos = ToDo.objects.filter(user = request.user)
    return render (request , 'todo_list.html' , {'todos':todos})

def logout_view(request):
    logout(request)
    return redirect('login_view')

@login_required  
def add_todo(request):
    form = TodoForm(request.POST)
    if form.is_valid():
        todo = form.save(commit = False)    #新增的欄位沒有user 但在models.py user欄位為必填 若直接保存會報錯
        todo.user = request.user            #將user欄位指定為當前使用者
        todo.save()
        messages.success(request , '新增成功')
        return redirect('todos')
    else:
        form = TodoForm()

    return render (request , 'add_todo.html' , {'form':form})

@login_required
def edit_todo(request, id):
    todo = get_object_or_404(ToDo, user=request.user, id=id)
    
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo) #用於將現有的資料庫實例與表單關聯起來 且更新而非創建
        if form.is_valid():
            form.save()
            messages.success(request , '編輯完成')
            return redirect('todos')
    else:
        form = TodoForm(instance=todo)
    return render(request, 'edit_todo.html', {'forms': form})

@login_required
def to_confirm_page(request , id):
    todo = get_object_or_404(ToDo , id = id)
    return render(request , 'confirm_delete.html' , {'todo':todo})

@login_required
def confirm_delete(request , id):
    todo = get_object_or_404(ToDo , id = id)
    todo.delete()
    messages.success(request , '成功刪除')
    return redirect('todos')