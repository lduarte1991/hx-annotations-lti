"""
hx_annotations/annotationsx/hx_lti_initializer/tests.py

Documentation URL/Ref#: TODO
Test Script for app hx_lti_initializer

Original purpose of this app: This app should take a request from a tool
consumer, authorize the user, log them in, and kickstart the lti tool.

Normal Test Case:
    1. Tool receives HTTP request
    2. Tool determines whether the user is authorized to access the product
    3. User account is either retrieved or created (if first time)
    4. User is logged in and sent to either the introduction page or the
       reference link passed in

Corner Cases Found:
    1. User tries to refresh page
    2. User tries to reach page via URL while logged in recently
    3. User tries to reach page via URL while not logged in
    4. User tries to view "Share" page while not logged in.
"""
import sys
from io import StringIO
from .utils import create_new_user
from .views import *
from .models import LTICourse, LTIProfile
from .forms import CourseForm
from .test_helper import (TEST_CONSUMER_KEY, TEST_SECRET_KEY)
from contextlib import contextmanager

from django.utils import six
from django.contrib.auth.models import User
from django.urls import resolve
from django.test.client import RequestFactory
from django.test import TestCase, override_settings, Client
from django.core.exceptions import PermissionDenied
from django.core.servers.basehttp import get_internal_wsgi_application
from mock import patch
from lti import ToolConfig


@contextmanager
def capture_err(command, *args, **kwargs):
    err, sys.stderr = sys.stderr, six.StringIO()
    command(*args, **kwargs)
    sys.stderr.seek(0)
    yield sys.stderr.read()
    sys.stderr = err

def create_user_for_test(self, **kwargs):
    anon_id = kwargs.get('anon_id', 'AnOnYmOuSiD')
    external_user_id = kwargs.get('username', 'FakeUsername')
    user_scope = kwargs.get('scope', 'course_or_consumer:123')
    display_name = kwargs.get('display_name', external_user_id)
    roles = kwargs.get('roles', ['Learner'])

    user, lti_profile = create_new_user(
        anon_id=anon_id,
        username=external_user_id,
        display_name=display_name,
        roles=roles,
        scope=user_scope
    )

    return user, lti_profile


class LTIInitializerModelsTests(TestCase):
    """
    Focuses on models and static methods found in hx_lti_initializer/models.py
    """

    createFakeUser = create_user_for_test

    def setUp(self):
        """
        This creates a user to test the LTIProfile autocreation
        """
        self.user, self.lti_profile = self.createFakeUser()

    def tearDown(self):
        """
        Deletes user variable created
        """
        del self.user

    def test_LTIProfile_create(self):
        """
        Checks that an LTIProfile object was automatically created
        as soon as a user object was created in setup.
        """
        instructor = LTIProfile.objects.get(user=self.user)
        self.assertTrue(isinstance(instructor, LTIProfile))
        self.assertEqual(instructor.__unicode__(), instructor.user.username)

    def test_LTICourse_create_course(self):
        """
        Checks that you can make a course given a course id and an instructor
        """
        instructor = LTIProfile.objects.get(user=self.user)
        course_object = LTICourse.create_course('test_course_id', instructor)
        self.assertTrue(isinstance(course_object, LTICourse))
        self.assertEqual(
            course_object.__unicode__(),
            course_object.course_name
        )

    def test_LTICourse_get_course_by_id(self):
        """
        Checks that you can get a course given an id.
        """
        instructor = LTIProfile.objects.get(user=self.user)
        course_object = LTICourse.create_course('test_course_id', instructor)
        course_to_test = LTICourse.get_course_by_id('test_course_id')
        self.assertTrue(isinstance(course_to_test, LTICourse))
        self.assertEqual(course_object, course_to_test)
        self.assertEqual(course_to_test.course_id, 'test_course_id')

    def test_LTICourse_get_courses_of_admin(self):
        """
        Checks that it returns a list of all the courses for that admin.
        """
        instructor = LTIProfile.objects.get(user=self.user)
        course_object = LTICourse.create_course('test_course_id', instructor)
        list_of_courses = LTICourse.get_courses_of_admin(instructor)
        self.assertTrue(isinstance(list_of_courses, list))
        self.assertTrue(len(list_of_courses) == 1)
        self.assertTrue(course_object in list_of_courses)

        course_object2 = LTICourse.create_course('test_course_id2', instructor)
        list_of_courses2 = LTICourse.get_courses_of_admin(instructor)
        self.assertTrue(len(list_of_courses2) == 2)
        self.assertTrue(course_object2 in list_of_courses2)

    def test_LTICourse_get_all_courses(self):
        """
        Checks that all courses are returned regardless of admin user
        """
        user2, lti_profile2 = self.createFakeUser(username="FakeUsername2", anon_id="AnOnYmOuSiD2")
        instructor1 = LTIProfile.objects.get(user_id=self.user.pk)
        instructor2 = LTIProfile.objects.get(user_id=user2.pk)
        list_of_courses = LTICourse.get_all_courses()
        self.assertTrue(isinstance(list_of_courses, list))
        self.assertTrue(len(list_of_courses) == 0)

        LTICourse.create_course('test_course_id', instructor1)
        list_of_courses2 = LTICourse.get_all_courses()
        self.assertTrue(isinstance(list_of_courses2, list))
        self.assertTrue(len(list_of_courses2) == 1)

        LTICourse.create_course('test_course_id2', instructor2)
        list_of_courses3 = LTICourse.get_all_courses()
        self.assertTrue(isinstance(list_of_courses3, list))
        self.assertTrue(len(list_of_courses3) == 2)


class LTIInitializerViewsTests(TestCase):
    """
    Focuses on the views methods found within hx_lti_initializer/views.py
    """
    createFakeUser = create_user_for_test

    def setUp(self):
        rf = RequestFactory()
        self.good_request = rf.post('/launch_lti/', {
            "lti_message_type": "basic-lti-launch-request",
            "oauth_consumer_key": TEST_CONSUMER_KEY,
            "lti_version": "LTI-1p0",
            "resource_link_id": "c28ddcf1b2b13c52757aed1fe9b2eb0a4e2710a3",
            "lis_result_sourcedid": "261-154-728-17-784",
            "lis_outcome_service_url": "http://localhost/lis_grade_passback",
            "launch_presentation_return_url": "http://example.com/lti_return",
            "custom_param1": "custom1",
            "custom_param2": "custom2",
            "oauth_signature": "aVQIRM6OkBku6yk3Guqyz+VUdgU=",
            "user_id": "234jfhrwekljrsfw8abcd35cseddda",
            "ext_lti_message_type": "extension-lti-launch",
            "roles": "Learner,Instructor,Observer",
            "lis_person_sourcedid": "fakeusername",
        })
        self.bad_request = rf.post('/launch_lti/', {
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "LTI-1p0",
            "resource_link_id": "c28ddcf1b2b13c52757aed1fe9b2eb0a4e2710a3",
            "lis_result_sourcedid": "261-154-728-17-784",
            "lis_outcome_service_url": "http://localhost/lis_grade_passback",
            "launch_presentation_return_url": "http://example.com/lti_return",
            "custom_param1": "custom1",
            "custom_param2": "custom2",
            "oauth_signature": "aVQIRM6OkBku6yk3Guqyz+VUdgU=",
            "user_id": "234jfhrwekljrsfw8abcd35cseddda",
            "ext_lti_message_type": "extension-lti-launch",
            "roles": "Learner,Instructor,Observer",
            "lis_person_sourcedid": "fakeusername",
        })
        self.small_request = rf.post('/launch_lti/', {
            "test": "one",
            "oauth_consumer_key": TEST_CONSUMER_KEY,
            "user_id": "234jfhrwekljrsfw8abcd35cseddda",
            "lis_person_sourcedid": "fakeusername",
        })
        self.missing_user_id = rf.post('/launch_lti/', {
            "test": "one",
            "oauth_consumer_key": TEST_CONSUMER_KEY,
            "lis_person_sourcedid": "fakeusername",
        })
        self.missing_username = rf.post('/launch_lti/', {
            "test": "one",
            "oauth_consumer_key": TEST_CONSUMER_KEY,
            "user_id": "234jfhrwekljrsfw8abcd35cseddda",
        })

    def tearDown(self):
        """
        Deletes variables created in set up
        """
        del self.good_request
        del self.bad_request
        del self.small_request
        del self.missing_user_id
        del self.missing_username

    def test_create_new_user(self):
        """
        Checks to see that a user and its linking LTIProfile are created.
        """
        username = self.good_request.POST["lis_person_sourcedid"]
        user_id = self.good_request.POST["user_id"]
        roles = self.good_request.POST["roles"]
        newuser, newprofile = self.createFakeUser(
            username=username,
            anon_id=user_id,
            roles=roles.split(",")
        )
        self.assertIsInstance(newuser, User)
        self.assertIsInstance(newprofile, LTIProfile)
        self.assertEqual(newuser.username, username)
        self.assertEqual(newprofile.user.username, username)
        self.assertEqual(newprofile.anon_id, user_id)

    def test_lti_config(self):
        client = Client()
        response = client.get('/lti/config')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response._headers['content-type'], ('Content-Type', 'text/xml'))


class LTIInitializerUrlsTests(TestCase):
    """
    """

    def test_urls(self):
        url = resolve('/lti_init/launch_lti/')
        self.assertEqual(str(url.view_name), 'hx_lti_initializer:launch_lti')


class LTIInitializerWSGITests(TestCase):
    """
    """
    def test_success(self):
        """
        If ``WSGI_APPLICATION`` is a dotted path, the referenced object is
        returned.
        """
        app = get_internal_wsgi_application()

        from annotationsx.wsgi import application

        self.assertIs(app, application)


class LTIInitializerCourseFormTests(TestCase):
    def setUp(self):
        # Create users
        users = []
        profiles = []
        names = ('Sally Singer', 'Bob Brown', 'Jimmy Kim', 'Jimmy Jam') # intentionally unordered
        for name in names:
            first, last = name.split(' ')
            username = name.replace(' ', '').lower()
            user = User(username=username, first_name=first, last_name=last, email="%s@localhost" % username)
            user.save()
            users.append(user)
            profiles.append(LTIProfile.objects.create(user=user))

        # Create course with admins
        course = LTICourse(course_id=1)
        course.save()
        for profile in profiles:
            course.add_admin(profile)

        # Add instance reference to course and form
        self.course_admins = profiles
        self.course = course
        self.course_form = CourseForm(instance=course)

    def tearDown(self):
        LTIProfile.objects.filter(pk__in=[p.pk for p in self.course_admins]).delete()
        self.course.delete()

    def test_course_form_admins(self):
        queryset = self.course_form.get_course_admins().all()

        expected_names = sorted([(profile.user.first_name, profile.user.last_name) for profile in self.course_admins], key=lambda user: user[0] + user[1])
        actual_names = sorted([(profile.user.first_name, profile.user.last_name) for profile in queryset], key=lambda user: user[0] + user[1])

        self.assertEqual(len(expected_names), len(actual_names))
        self.assertEqual(expected_names, actual_names)
