from model_bakery import baker
from rest_framework.test import APIClient
import pytest

from students.models import Student, Course


@pytest.fixture
def client():
	return APIClient()


@pytest.fixture
def student_factory():
	def factory(*args, **kwargs):
		return baker.make(Student, *args, **kwargs)
	return factory


@pytest.fixture
def course_factory():
	def factory(*args, **kwargs):
		return baker.make(Course, *args, **kwargs)
	return factory


@pytest.mark.django_db
def test_get_courses_retrieve(client, course_factory):
	courses = course_factory(_quantity=1)
	response = client.get(f'/api/v1/courses/{courses[0].pk}/')
	assert response.status_code == 200
	assert response.json()['name'] == courses[0].name


@pytest.mark.django_db
def test_get_course_list(client, course_factory):
	courses = course_factory(_quantity=10)
	response = client.get('/api/v1/courses/')
	assert response.status_code == 200
	data = response.json()
	assert len(data) == len(courses)
	for i, course in enumerate(data):
		assert course['name'] == courses[i].name


@pytest.mark.django_db
def test_courses_filter_pk(client, course_factory):
	courses = course_factory(_quantity=5)
	response = client.get(f'/api/v1/courses/', data={'id': courses[1].pk})
	assert response.status_code == 200
	assert len(response.json()) == 1
	assert response.json()[0]['name'] == courses[1].name


@pytest.mark.django_db
def test_courses_filter_name(client, course_factory):
	courses = course_factory(_quantity=5)
	target_course_name = courses[2].name
	response = client.get(f'/api/v1/courses/', data={'name': target_course_name})
	assert response.status_code == 200
	assert response.json()[0]['id'] == courses[2].pk


@pytest.mark.django_db
def test_course_create(client):
	count = Course.objects.count()
	response = client.post('/api/v1/courses/', data={'name': 'New test course'})
	assert response.status_code == 201
	assert Course.objects.count() == count + 1
	assert Course.objects.get(id=response.json()['id']).name == response.json()['name']


@pytest.mark.django_db
def test_course_update(client, course_factory):
	new_course = Course.objects.create(name='test_courses_update')
	response = client.put(f'/api/v1/courses/{new_course.id}/', data={'name': 'test_courses_update_new'})
	assert response.status_code == 200
	assert Course.objects.get(id=response.json()['id']).name == 'test_courses_update_new'


@pytest.mark.django_db
def test_course_delete(client):
	count = Course.objects.count()
	new_course = Course.objects.create(name='test_courses_delete')
	response = client.delete(f'/api/v1/courses/{new_course.id}/')
	assert response.status_code == 204
	assert Course.objects.count() == count
