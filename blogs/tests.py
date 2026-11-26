from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import BlogPost

class BlogTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='author1', password='Password123!')
        self.user2 = User.objects.create_user(username='author2', password='Password123!')
        self.post1 = BlogPost.objects.create(title='Первый пост', text='Текст первого поста', owner=self.user1)
        self.post2 = BlogPost.objects.create(title='Второй пост', text='Текст второго поста', owner=self.user2)

    def test_index_ordering_and_public_access(self):
        response = self.client.get(reverse('blogs:index'))
        self.assertEqual(response.status_code, 200)
        posts = list(response.context['posts'])
        self.assertEqual(posts, [self.post2, self.post1])

    def test_empty_blog_state(self):
        BlogPost.objects.all().delete()
        response = self.client.get(reverse('blogs:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Публикаций пока нет')

    def test_anonymous_cannot_create_post(self):
        response = self.client.get(reverse('blogs:new_post'))
        self.assertEqual(response.status_code, 302)
        post_response = self.client.post(reverse('blogs:new_post'), {'title': 'Аноним', 'text': 'Текст'})
        self.assertEqual(post_response.status_code, 302)
        self.assertEqual(BlogPost.objects.count(), 2)

    def test_authenticated_can_create_post_and_owner_assigned(self):
        self.client.login(username='author1', password='Password123!')
        response = self.client.post(reverse('blogs:new_post'), {'title': 'Новый пост', 'text': 'Контент'})
        self.assertRedirects(response, reverse('blogs:index'))
        created = BlogPost.objects.get(title='Новый пост')
        self.assertEqual(created.owner, self.user1)

    def test_owner_can_edit_own_post(self):
        self.client.login(username='author1', password='Password123!')
        response = self.client.post(
            reverse('blogs:edit_post', args=[self.post1.id]),
            {'title': 'Обновлённый заголовок', 'text': 'Обновлённый текст'}
        )
        self.assertRedirects(response, reverse('blogs:index'))
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.title, 'Обновлённый заголовок')

    def test_user_cannot_edit_foreign_post(self):
        self.client.login(username='author1', password='Password123!')
        get_resp = self.client.get(reverse('blogs:edit_post', args=[self.post2.id]))
        self.assertEqual(get_resp.status_code, 404)
        post_resp = self.client.post(
            reverse('blogs:edit_post', args=[self.post2.id]),
            {'title': 'Взлом', 'text': 'Чужой текст'}
        )
        self.assertEqual(post_resp.status_code, 404)
        self.post2.refresh_from_db()
        self.assertEqual(self.post2.title, 'Второй пост')

    def test_nonexistent_id_returns_404(self):
        self.client.login(username='author1', password='Password123!')
        response = self.client.get(reverse('blogs:edit_post', args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_registration_creates_and_logs_in_user(self):
        response = self.client.post(reverse('users:register'), {
            'username': 'newblogger',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        self.assertRedirects(response, reverse('blogs:index'))
        self.assertTrue(User.objects.filter(username='newblogger').exists())

    def test_logout_post_only(self):
        self.client.login(username='author1', password='Password123!')
        get_resp = self.client.get(reverse('users:logout'))
        self.assertEqual(get_resp.status_code, 405)
        post_resp = self.client.post(reverse('users:logout'))
        self.assertRedirects(post_resp, reverse('blogs:index'))
