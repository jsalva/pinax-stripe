import decimal

from django.core import management
from django.test import TestCase

from django.contrib.auth import get_user_model

from mock import patch, Mock

from ..proxies import CustomerProxy, PlanProxy


class CommandTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="patrick")

    @patch("stripe.Customer.retrieve")
    @patch("stripe.Customer.create")
    def test_init_customer_creates_customer(self, CreateMock, RetrieveMock):
        cu = CreateMock()
        cu.account_balance = 0
        cu.delinquent = False
        cu.default_source = "card_178Zqj2eZvKYlo2Cr2fUZZz7"
        cu.currency = "usd"
        cu.id = "cus_XXXXX"
        management.call_command("init_customers")
        customer = CustomerProxy.get_for_user(self.user)
        self.assertEquals(customer.stripe_id, "cus_XXXXX")

    @patch("stripe.Plan.all")
    def test_plans_create(self, PlanAllMock):
        plan_mock = Mock()
        plan_mock.id = "entry-monthly"
        plan_mock.amount = 954
        plan_mock.interval = "monthly"
        plan_mock.interval_count = 1
        plan_mock.currency = None
        plan_mock.statement_descriptor = None
        plan_mock.trial_period_days = None
        plan_mock.name = "Pro"
        PlanAllMock().data = [
            plan_mock
        ]
        management.call_command("sync_plans")
        self.assertEquals(PlanProxy.objects.count(), 1)
        self.assertEquals(PlanProxy.objects.all()[0].stripe_id, "entry-monthly")
        self.assertEquals(PlanProxy.objects.all()[0].amount, decimal.Decimal("9.54"))

    @patch("stripe.Customer.retrieve")
    @patch("pinax.stripe.actions.syncs.sync_customer")
    @patch("pinax.stripe.actions.syncs.sync_invoices_for_customer")
    @patch("pinax.stripe.actions.syncs.sync_charges_for_customer")
    def test_sync_customers(self, SyncChargesMock, SyncInvoicesMock, SyncMock, RetrieveMock):
        user2 = get_user_model().objects.create_user(username="thomas")
        get_user_model().objects.create_user(username="altman")
        CustomerProxy.objects.create(stripe_id="cus_XXXXX", user=self.user)
        CustomerProxy.objects.create(stripe_id="cus_YYYYY", user=user2)
        management.call_command("sync_customers")
        self.assertEqual(SyncChargesMock.call_count, 2)
        self.assertEqual(SyncInvoicesMock.call_count, 2)
        self.assertEqual(SyncMock.call_count, 2)
