from django.test import TestCase
from django.contrib.auth.models import Group, User
from django.db.models.signals import post_save, post_delete, m2m_changed
from cities_light.models import City, Country

from meetup.constants import MEMBER, ORGANIZER
from meetup.models import MeetupLocation
from meetup.signals import (manage_meetup_location_groups, remove_meetup_location_groups,
                            add_meetup_location_members, add_meetup_location_organizers,
                            delete_meetup_location_members, delete_meetup_location_organizers)
from users.models import SystersUser


class SignalsTestCase(TestCase):
    def setUp(self):
        post_save.connect(manage_meetup_location_groups, sender=MeetupLocation,
                          dispatch_uid="manage_groups")
        post_delete.connect(remove_meetup_location_groups, sender=MeetupLocation,
                            dispatch_uid="remove_groups")
        m2m_changed.connect(add_meetup_location_members, sender=MeetupLocation.members.through,
                            dispatch_uid="add_members")
        m2m_changed.connect(add_meetup_location_organizers,
                            sender=MeetupLocation.organizers.through,
                            dispatch_uid="add_organizers")
        m2m_changed.connect(delete_meetup_location_members, sender=MeetupLocation.members.through,
                            dispatch_uid="delete_members")
        m2m_changed.connect(delete_meetup_location_organizers,
                            sender=MeetupLocation.organizers.through,
                            dispatch_uid="delete_organizers")

    def test_manage_meetup_location_groups(self):
        """Test addition of groups when saving a Meetup Location object"""
        country = Country.objects.create(name='Bar', continent='AS')
        location = City.objects.create(name='Baz', display_name='Baz', country=country)
        meetup_location = MeetupLocation.objects.create(    # noqa
            name="Foo", slug="foo", location=location,
            description="It's a test meetup location")
        groups_count = Group.objects.count()
        self.assertEqual(groups_count, 2)

    def test_remove_community_groups(self):
        """Test the removal of groups when a Meetup Location is deleted"""
        country = Country.objects.create(name='Bar', continent='AS')
        location = City.objects.create(name='Baz', display_name='Baz', country=country)
        meetup_location = MeetupLocation.objects.create(
            name="Foo", slug="foo", location=location,
            description="It's a test meetup location")
        groups_count = Group.objects.count()
        self.assertEqual(groups_count, 2)
        meetup_location.delete()
        groups_count = Group.objects.count()
        self.assertEqual(groups_count, 0)

    def test_add_meetup_location_members(self):
        """Test addition of permissions to a user when she is made a meetup location member"""
        user = User.objects.create(username='foo', password='foobar')
        systers_user = SystersUser.objects.get(user=user)
        country = Country.objects.create(name='Bar', continent='AS')
        location = City.objects.create(name='Baz', display_name='Baz', country=country)
        meetup_location = MeetupLocation.objects.create(
            name="Foo", slug="foo", location=location,
            description="It's a test meetup location")
        meetup_location.members.add(systers_user)
        members_group = Group.objects.get(name=MEMBER.format(meetup_location.name))
        self.assertEqual(user.groups.get(), members_group)

    def test_add_meetup_location_organizers(self):
        """Test addition of permissions to a user when she is made a meetup location organizer"""
        user = User.objects.create(username='foo', password='foobar')
        systers_user = SystersUser.objects.get(user=user)
        country = Country.objects.create(name='Bar', continent='AS')
        location = City.objects.create(name='Baz', display_name='Baz', country=country)
        meetup_location = MeetupLocation.objects.create(
            name="Foo", slug="foo", location=location,
            description="It's a test meetup location")
        meetup_location.organizers.add(systers_user)
        organizers_group = Group.objects.get(name=ORGANIZER.format(meetup_location.name))
        self.assertEqual(user.groups.get(), organizers_group)

    def test_delete_meetup_location_members(self):
        """Test removal of permissions from a user when she is removed as a meetup location
        member"""
        user = User.objects.create(username='foo', password='foobar')
        systers_user = SystersUser.objects.get(user=user)
        country = Country.objects.create(name='Bar', continent='AS')
        location = City.objects.create(name='Baz', display_name='Baz', country=country)
        meetup_location = MeetupLocation.objects.create(
            name="Foo", slug="foo", location=location,
            description="It's a test meetup location")
        members_group = Group.objects.get(name=MEMBER.format(meetup_location.name))
        meetup_location.members.add(systers_user)
        self.assertEqual(user.groups.get(), members_group)
        meetup_location.members.remove(systers_user)
        self.assertEqual(len(user.groups.all()), 0)

    def test_delete_meetup_location_organizers(self):
        """Test removal of permissions from a user when she is removed as a meetup location
        organizer"""
        user = User.objects.create(username='foo', password='foobar')
        systers_user = SystersUser.objects.get(user=user)
        country = Country.objects.create(name='Bar', continent='AS')
        location = City.objects.create(name='Baz', display_name='Baz', country=country)
        meetup_location = MeetupLocation.objects.create(
            name="Foo", slug="foo", location=location,
            description="It's a test meetup location")
        organizers_group = Group.objects.get(name=ORGANIZER.format(meetup_location.name))
        meetup_location.organizers.add(systers_user)
        self.assertEqual(user.groups.get(), organizers_group)
        meetup_location.organizers.remove(systers_user)
        self.assertEqual(len(user.groups.all()), 0)
