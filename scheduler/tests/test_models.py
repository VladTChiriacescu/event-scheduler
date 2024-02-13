from datetime import datetime

from django.test import TestCase
from scheduler.models import Employee
from django.contrib.auth.models import User


class EmployeeTest(TestCase):
    def create_user(self):
        user = User.objects.create(username="new_test_user", password='test_password')
        print(f'Created test user with id: {user.id}, username: {user.username}, password: {user.password}')
        return user

    def create_employee(self, user: User):
        employee = Employee.objects.create(name="NewTestUser", email="test_email", company="test_company", country="test_country", user=user)
        print(f'Created test employee with id: {employee.id}, name: {employee.name}, email: {employee.email}, company: {employee.company}, country: {employee.country}')
        return employee

    def test_user_creation(self):
        user = self.create_user()
        self.assertTrue(isinstance(user, User))
        employee = Employee.objects.filter(user=user.id)
        self.assertFalse(employee.exists(), msg="Employee data should not be saved when the user data is saved")

    def test_employee_creation(self):
        test_user = self.create_user()
        test_employee = self.create_employee(test_user)
        self.assertTrue(isinstance(test_employee, Employee))

    # def test_date_parsing():
    #     date_string = "01.01.24"
    #     date = datetime.strptime(date_string, '%d.%m.%y')
    #     print(f'Date: {date}; type: {type(date)}')
