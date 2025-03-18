import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ToDos.models import ToDo
from django.contrib import messages

class TodoTests(TestCase):
    def setUp(self):
        # 初始化測試環境
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')

        # 為 user1 創建多個待辦事項
        self.todo1 = ToDo.objects.create(
            user=self.user1,
            title='學習',
            description='完成作業',
            due_date=datetime.date(2025, 3, 20),
            priority='high',
            completed=False
        )
        self.todo2 = ToDo.objects.create(
            user=self.user1,
            title='會議',
            description='參加會議',
            due_date=datetime.date.today() - datetime.timedelta(days=1),  # 過期
            priority='medium',
            completed=False
        )
        self.todo3 = ToDo.objects.create(
            user=self.user1,
            title='閱讀',
            description='閱讀書本',
            due_date=datetime.date(2025, 3, 25),
            priority='low',
            completed=True
        )

    # 功能性測試
    def test_toggle_todo(self):
        # 測試標記完成功能
        self.client.login(username='user1', password='testpass123')
        # 初始狀態為未完成
        response = self.client.get(reverse('todos'))
        self.assertContains(response, '未完成')
        # 標記為完成
        response = self.client.post(reverse('toggle_todo', args=[self.todo1.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '已完成')
        self.todo1.refresh_from_db()
        self.assertTrue(self.todo1.completed)
        # 再次標記為未完成
        response = self.client.post(reverse('toggle_todo', args=[self.todo1.id]), follow=True)
        self.assertContains(response, '未完成')
        self.todo1.refresh_from_db()
        self.assertFalse(self.todo1.completed)

    def test_filter_todos(self):
        # 測試過濾功能
        self.client.login(username='user1', password='testpass123')
        # 過濾未完成
        response = self.client.get(reverse('todos') + '?filter=incomplete')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '學習')
        self.assertNotContains(response, '閱讀')
        # 過濾已完成
        response = self.client.get(reverse('todos') + '?filter=completed')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '閱讀')
        self.assertNotContains(response, '學習')
        # 過濾全部
        response = self.client.get(reverse('todos') + '?filter=all')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '學習')
        self.assertContains(response, '閱讀')

    def test_date_highlighting(self):
        # 測試日期高亮（過期未完成事項）
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('todos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'table-danger')  # 確認過期事項高亮
        self.assertContains(response, 'table-danger', count=1)
    # 邊界情況測試
    def test_no_todos(self):
        # 測試無待辦事項時的行為
        ToDo.objects.all().delete()
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('todos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '尚無待辦事項')

    def test_invalid_date(self):
        # 測試無效日期輸入
        self.client.login(username='user1', password='testpass123')
        response = self.client.post(reverse('add_todo'), {
            'title': '無效日期',
            'description': '測試',
            'due_date': 'invalid-date',  # 無效日期
            'priority': 'high'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '請填寫這個欄位。')  # 假設表單驗證會顯示錯誤

    def test_many_todos(self):
        # 測試大量待辦事項（模擬分頁基礎）
        for i in range(15):
            ToDo.objects.create(
                user=self.user1,
                title=f'任務{i}',
                description=f'描述{i}',
                due_date=datetime.date(2025, 3, 20),
                priority='medium',
                completed=False
            )
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('todos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '任務0')
        self.assertContains(response, '任務14')  # 確認多筆資料顯示

    # 安全性測試
    def test_csrf_protection_toggle(self):
        # 測試標記完成的 CSRF 保護
        self.client.login(username='user1', password='testpass123')
        client_no_csrf = Client(enforce_csrf_checks=True)
        client_no_csrf.login(username='user1', password='testpass123')
        response = client_no_csrf.post(reverse('toggle_todo', args=[self.todo1.id]), follow=True)
        self.assertEqual(response.status_code, 403)  # 應返回 403 Forbidden

    def test_unauthorized_toggle(self):
        # 測試未授權標記（user2 嘗試標記 user1 的待辦事項）
        self.client.login(username='user2', password='testpass123')
        response = self.client.post(reverse('toggle_todo', args=[self.todo1.id]), follow=True)
        self.assertIn(response.status_code, [403, 404])  # 應返回 403 或 404

    def test_data_isolation_filter(self):
        # 測試過濾時的資料隔離
        ToDo.objects.create(
            user=self.user2,
            title='user2任務',
            description='user2描述',
            due_date=datetime.date(2025, 3, 20),
            priority='high',
            completed=False
        )
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('todos') + '?filter=all')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '學習')
        self.assertNotContains(response, 'user2任務')

    def test_password_security(self):
        # 測試密碼是否加密儲存
        self.assertNotEqual(self.user1.password, 'testpass123')  # 密碼不應是明文
        self.assertTrue(self.user1.password.startswith('pbkdf2_sha256$'))  # 應使用 Django 的密碼哈希