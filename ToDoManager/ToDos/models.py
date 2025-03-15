from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ToDo(models.Model):
    PRIORITY_CHOICES = [
        ('high' , '高'),
        ('medium' , '中'),
        ('low' , '低'),
    ]
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'todos')
    title = models.CharField(max_length = 100)
    description = models.TextField(blank  = True , null = True) #charfield通常用於固定長度字串 使用text更適合長文本
    due_date = models.DateField()
    priority = models.CharField(max_length = 6 , choices = PRIORITY_CHOICES)
    completed = models.BooleanField(default = False)  #沒有設定參數時 boolean預設為none
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return(self.title)