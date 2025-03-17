import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ToDos.models import ToDo  # 確保這裡是 ToDo（與模型名稱一致）

class TodoTests(TestCase):
    def setUp(self):
        # 初始化測試環境
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')

        # 為 user1 創建一個待辦事項
        self.todo = ToDo.objects.create(
            user=self.user1,
            title='學習',
            description='完成作業',
            due_date=datetime.date(2025, 3, 20),
            priority='high',
            completed=False
        )

    # 功能性測試
    def test_add_todo(self):
        # 測試新增待辦事項
        self.client.login(username='user1', password='testpass123')
        response = self.client.post(reverse('add_todo'), {
            'title': '會議',
            'description': '參加會議',
            'due_date': '2025-03-21',
            'priority': 'medium'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '會議')
        self.assertContains(response, '新增成功')

    def test_view_todo_list(self):
        # 測試讀取待辦清單
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('todos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '學習')  # 確認是否顯示待辦事項
        self.assertContains(response, 'user1')  # 確認是否顯示使用者名稱

    def test_edit_todo(self):
        # 測試編輯待辦事項
        self.client.login(username='user1', password='testpass123')
        response = self.client.post(reverse('edit_todo', args=[self.todo.id]), {
            'title': '學習（更新）',
            'description': '完成作業（更新）',
            'due_date': '2025-03-21',
            'priority': 'low'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '學習（更新）')
        self.assertContains(response, '編輯完成')

    def test_delete_todo(self):
        # 測試刪除待辦事項
        self.client.login(username='user1', password='testpass123')
        # 訪問確認頁面
        response = self.client.get(reverse('to_confirm_page', args=[self.todo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '確定要刪除「學習」嗎？')
        # 執行刪除
        response = self.client.post(reverse('confirm_delete', args=[self.todo.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '學習')
        self.assertFalse(ToDo.objects.filter(id=self.todo.id).exists())

    def test_unauthenticated_access(self):
        # 測試未登入訪問限制
        self.client.logout()
        response = self.client.get(reverse('todos'))
        self.assertEqual(response.status_code, 302)  # 應重定向到登入頁面
        self.assertTrue(response.url.startswith(reverse('login_view')))

    # 安全性測試
    def test_csrf_protection(self):
        # 測試 CSRF 保護
        self.client.login(username='user1', password='testpass123')
        client_no_csrf = Client(enforce_csrf_checks=True)
        client_no_csrf.login(username='user1', password='testpass123')
        response = client_no_csrf.post(reverse('add_todo'), {
            'title': '會議',
            'description': '參加會議',
            'due_date': '2025-03-21',
            'priority': 'medium'
        }, follow=True)
        self.assertEqual(response.status_code, 403)  # 應返回 403 Forbidden

    def test_unauthorized_access(self):
        # 測試未授權訪問（user2 嘗試編輯 user1 的待辦事項）
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('edit_todo', args=[self.todo.id]))
        self.assertIn(response.status_code, [403, 404])  # 應返回 403 或 404

    def test_data_isolation(self):
        # 測試資料隔離（user2 不應看到 user1 的待辦事項）
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('todos'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '學習')  # user2 不應看到 user1 的待辦事項

    def test_password_security(self):
        # 測試密碼是否加密儲存
        self.assertNotEqual(self.user1.password, 'testpass123')  # 密碼不應是明文
        self.assertTrue(self.user1.password.startswith('pbkdf2_sha256$'))  # 應使用 Django 的密碼哈希