from django.shortcuts import render , redirect
from django.contrib.auth.forms import UserCreationForm , AuthenticationForm
from django.contrib import messages
from django.contrib.auth import authenticate , login , logout
from django.contrib.auth.decorators import login_required

# Create your views here.
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
            return redirect(login)
    else:   #GET請求時創建空白表單   
        form = UserCreationForm() 
    return render (request , 'register.html' , {'form' : form}) #當在GET請求或表單驗證失敗時顯示的畫面

@login_required(login_url='login_view') #若使用者透過get方法進入 則導向註冊畫面
def todos(request): 
    return render(request , 'todo_list.html')

def logout_view(request):
    logout(request)
    return redirect('login_view')