from http import client
from unicodedata import name
from urllib import response
from django.test import TestCase, Client
from django.urls import reverse
from home.models import Project, Category, Expense
import json


class TestViews(TestCase):



    def setUp(self) -> None:
        self.client = Client()
        self.list_url = reverse('list')
        self.detail_url = reverse('detail', args=['plotly_django'])
        self.project1 = Project.objects.create(
            name='project1',
            budget=10000
        )
        self.category1 = Category.objects.create(
            project=self.project1,
            name='development'
        )
        self.expense1 = {
            'title': 'expense1',
            'amount': 10000,
            'category': 'development'
        }

    def test_project_list_GET(self):
        response = self.client.get(self.list_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'budget/project-list.html')

    def test_project_detail_GET(self):
        response = self.client.get(self.detail_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'budget/project-detail.html')

    def test_project_detail_POST_add_new_expense(self):
        response = self.client.post(self.detail_url, self.expense1)

        self.assertEquals(response.status_code, 302)
        self.assertEquals(self.project1.expenses.first().title, 'expense1')

    def test_project_detail_POST_no_data(self):
        response = self.client.post(self.detail_url)

        self.assertEquals(response.status_code, 302)
        self.assertEquals(self.project1.expenses.count(), 0)
