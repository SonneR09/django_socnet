from django.http import response
from django.test import TestCase, Client
from django.urls import reverse

from .models import User, Post, Follow


class ProfileTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create(
            username="John", password="qwe123qwe123", email="qwe@gmail.com"
        )

        self.post = Post.objects.create(
            text="Primary text of the post", author=self.user
        )

        self.urls = (
            reverse("index"),
            reverse("profile", kwargs={"username": self.user.username}),
            reverse(
                "post", kwargs={"username": self.user.username, "post_id": self.post.pk}
            ),
        )

        self.user1 = User.objects.create(
            username="Kate", password="qwe123q22we123", email="qw212e@gmail.com"
        )

        self.user2 = User.objects.create(
            username="Bob", password="qwe123q22we123", email="qw213232e@gmail.com"
        )

    def test_anon_cant_post(self):
        self.client.logout()
        response = self.client.post(reverse("new_post"), data={"text": "test_text"})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/auth/login/?next=/new_post/")

    def test_profile_page(self):
        response = self.client.get(
            reverse("profile", kwargs={"username": self.user.username})
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["author"], User)
        self.assertEqual(response.context["author"].username, self.user.username)

    def test_auth_can_post(self):
        self.client.force_login(user=self.user)
        self.client.post(reverse("new_post"), data={"text": "test_text"})

        response = self.client.get(
            reverse("profile", kwargs={"username": self.user.username})
        )
        self.assertEqual(response.context["author"].posts.count(), 2)

        for url in self.urls:
            response = self.client.get(url)
            self.assertContains(response, self.post.text)

    def test_auth_can_edit(self):
        self.client.force_login(user=self.user)
        new_text = "Changed text of post"
        response = self.client.post(
            reverse(
                "post_edit",
                kwargs={"username": self.user.username, "post_id": self.post.pk},
            ),
            data={"text": new_text},
            follow=True,
        )
        self.post = Post.objects.get(pk=self.post.pk)
        self.assertEqual(self.post.text, new_text)

        for url in self.urls:
            response = self.client.get(url)
            self.assertContains(response, self.post.text)

    def test_page404(self):
        response = self.client.get("/3132qwqqwdwe/")
        self.assertTemplateUsed(response, "misc/404.html")

    def test_profile_follow_and_unfollow(self):
        self.client.force_login(user=self.user)
        response = self.client.get(
            reverse("profile_follow", kwargs={"username": self.user1.username})
        )

        followers = Follow.objects.filter(user=self.user, author=self.user1).count()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(followers, 1)

        response = self.client.get(
            reverse("profile_unfollow", kwargs={"username": self.user1.username})
        )
        followers = Follow.objects.filter(user=self.user, author=self.user1).count()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(followers, 0)

    def test_follower_see_post_nofollower_dont(self):
        self.client.force_login(user=self.user1)
        self.client.get(
            reverse("profile_follow", kwargs={"username": self.user.username})
        )
        response = self.client.get(reverse("follow_index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Primary text of the post")

        self.client.force_login(user=self.user2)
        response = self.client.get(reverse("follow_index"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Primary text of the post")

    def test_only_auth_can_comment(self):
        self.client.force_login(user=self.user1)
        response = self.client.post(
            reverse(
                "add_comment",
                kwargs={"username": self.user.username, "post_id": self.post.pk},
            ),
            data={"text": "test_text"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test_text")

        self.client.logout()
        response = self.client.post(
            reverse(
                "add_comment",
                kwargs={"username": self.user.username, "post_id": self.post.pk},
            ),
            data={"text": "test_text_unlog"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "test_text_unlog")
