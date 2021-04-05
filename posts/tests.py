from django.test import TestCase, Client
from django.urls import reverse

from .models import User, Post


class ProfileTest(TestCase):

    def setUp(self):
        self.username = 'John'
        self.password = 'qwe123qwe123'
        self.email = 'qwe@gmail.com'

        self.client = Client()
        self.user = User.objects.create(
            username=self.username,
            password=self.password,
            email=self.email
            )
        self.post = Post.objects.create(text='Primary text of the post', author=self.user)
        self.urls = (
            reverse('index'),
            reverse('profile', kwargs={"username":self.username}),
            reverse('post', kwargs={"username":self.username, "post_id":self.post.pk})
        )

    def test_anon_cant_post(self):
        self.client.logout()
        response = self.client.post(
            reverse('new_post'), data={'text':'test_text'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/auth/login/?next=/new_post/')
    
    def test_profile_page(self):
        response = self.client.get(
            reverse('profile', kwargs={'username':self.user.username})
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['author'], User)
        self.assertEqual(response.context['author'].username, self.user.username)

    def test_auth_can_post(self):
        self.client.force_login(user=self.user)
        self.client.post(reverse('new_post'), data={'text':'test_text'})

        response = self.client.get(
            reverse('profile', kwargs={'username':self.user.username})
        )
        self.assertEqual(response.context['author'].posts.count(), 2)

        for url in self.urls:
            response = self.client.get(url)
            self.assertContains(response, self.post.text)

    def test_auth_can_edit(self):
        self.client.force_login(user=self.user)
        new_text = 'Changed text of post'
        response = self.client.post(
            reverse(
                    "post_edit",
                    kwargs={'username':self.username,
                            "post_id": self.post.pk}
                ),
                data={'text': new_text},
                follow=True
                )
        self.post = Post.objects.get(pk=self.post.pk)
        self.assertEqual(self.post.text, new_text)

        for url in self.urls:
            response = self.client.get(url)
            self.assertContains(response, self.post.text)

    def test_page404(self):
        response = self.client.get('/3132qwqqwdwe/')
        self.assertTemplateUsed(response, 'misc/404.html')
        