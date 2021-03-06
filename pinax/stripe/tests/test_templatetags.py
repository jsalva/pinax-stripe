from django.test import TestCase
from django.utils import timezone

from django.contrib.auth import authenticate, login, get_user_model

from mock import Mock

from ..proxies import SubscriptionProxy, CustomerProxy, PlanProxy
from ..templatetags.pinax_stripe_tags import change_plan_form, subscribe_form

from .test_middleware import DummySession


class PinaxStripeTagTests(TestCase):

    def test_change_plan_form(self):
        request = Mock()
        request.META = {}
        request.session = DummySession()
        user = get_user_model().objects.create_user(username="patrick")
        user.set_password("eldarion")
        user.save()
        customer = CustomerProxy.objects.create(
            stripe_id="cus_1",
            user=user
        )
        plan = PlanProxy.objects.create(
            amount=10,
            currency="usd",
            interval="monthly",
            interval_count=1,
            name="Pro"
        )
        SubscriptionProxy.objects.create(
            customer=customer,
            plan=plan,
            quantity=1,
            start=timezone.now(),
            status="active",
            cancel_at_period_end=False
        )
        user = authenticate(username="patrick", password="eldarion")
        login(request, user)
        context = {
            "request": request
        }
        change_plan_form(context)
        self.assertTrue("form" in context)

    def test_subscribe_form(self):
        context = {}
        subscribe_form(context)
        self.assertTrue("form" in context)
