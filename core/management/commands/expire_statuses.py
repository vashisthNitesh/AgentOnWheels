from django.core.management.base import BaseCommand
from core.services import expire_statuses


class Command(BaseCommand):
    help = "Auto-expire bids, leases, contracts, quotations and RFQs. Schedule every 5-15 min (cron/systemd/Neon-friendly)."

    def add_arguments(self, p):
        p.add_argument("--loop", type=int, default=0, help="Run forever, sleeping N seconds between runs")

    def handle(self, *a, loop=0, **kw):
        import time
        while True:
            self.stdout.write(str(expire_statuses()))
            if not loop:
                break
            time.sleep(loop)
