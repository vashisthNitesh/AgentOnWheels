import datetime as dt
from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from core import models as m
from core.services import expire_statuses, fleet_snapshot


class FixesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", verbosity=0)

    def test_invoice_dates_and_tax_from_rule(self):
        for inv in m.Invoice.objects.all():
            self.assertEqual(inv.due_date, inv.invoice_date + dt.timedelta(days=inv.customer.payment_terms_days))
            self.assertEqual(inv.tax_rate, Decimal("5.00"))  # UAE VAT on AED, not 18% GST
            self.assertEqual(inv.total, inv.base_amount + inv.tax_amount)
            self.assertTrue(inv.invoicing_company)

    def test_passcodes_hashed(self):
        d = m.Driver.objects.first()
        self.assertTrue(d.passcode_hash.startswith(("pbkdf2", "argon2", "scrypt")))
        with self.assertRaises(Exception):
            d.set_passcode("123456")

    def test_expiry(self):
        b = m.Bid.objects.first()
        m.Bid.objects.filter(pk=b.pk).update(status="pending", bid_end=timezone.now() - dt.timedelta(hours=1), bid_start=timezone.now() - dt.timedelta(days=1))
        m.BidResponse.objects.filter(bid=b).delete()
        expire_statuses()
        b.refresh_from_db(); self.assertEqual(b.status, "expired")
        self.assertFalse(m.LeaseOrder.objects.filter(end_date__lt=timezone.localdate(), status__in=["created", "active"]).exists())

    def test_completed_orders_have_committed_vehicles(self):
        for o in m.Order.objects.filter(status="completed"):
            self.assertGreaterEqual(o.vehicles_committed, 1)

    def test_fleet_counts_consistent(self):
        f = fleet_snapshot()
        self.assertEqual(f["idle"], len(f["idle_vehicles"]))
        self.assertEqual(f["drivers_active"], m.Driver.objects.filter(status="active").count())
