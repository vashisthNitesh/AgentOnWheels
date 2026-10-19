"""Business services: automatic status expiry + KPI engine (single source of truth)."""
import datetime as dt
from collections import defaultdict
from decimal import Decimal

from django.db.models import Count, Q, Sum
from django.utils import timezone

from . import models as m


def expire_statuses(now=None):
    """Time-based transitions ATS never did. Idempotent; run via `manage.py expire_statuses` (cron) and lazily."""
    now = now or timezone.now()
    today = timezone.localdate(now)
    res = {}
    # Bids: window passed -> expired (no responses) / closed (responses awaiting award); window open -> active
    res["bids_active"] = m.Bid.objects.filter(status="pending", bid_start__lte=now, bid_end__gt=now).update(status="active")
    past = m.Bid.objects.filter(status__in=["pending", "active"], bid_end__lte=now)
    res["bids_closed"] = m.Bid.objects.filter(pk__in=past.filter(responses__isnull=False).values("pk")).update(status="closed")
    res["bids_expired"] = m.Bid.objects.filter(status__in=["pending", "active"], bid_end__lte=now).update(status="expired")
    # Leases
    res["leases_active"] = m.LeaseOrder.objects.filter(status="created", start_date__lte=today, end_date__gte=today).update(status="active")
    res["leases_completed"] = m.LeaseOrder.objects.filter(status__in=["created", "active"], end_date__lt=today).update(status="completed")
    # Contracts
    for model in (m.CustomerContract, m.VendorContract):
        k = model.__name__
        res[k + "_expired"] = model.objects.exclude(status="expired").filter(end_date__lt=today).update(status="expired")
        res[k + "_active"] = model.objects.filter(status="pending", start_date__lte=today, end_date__gte=today).update(status="active")
    # Quotations
    res["quotations_expired"] = m.Quotation.objects.filter(status__in=["draft", "sent"], valid_till__lt=today).update(status="expired")
    # RFQs
    m.RFQ.objects.filter(status="scheduled", cycle1_start__lte=today).update(status="active")
    m.RFQ.objects.filter(status="active", contract_expiry__lt=today).update(status="completed")
    return res


def _period(params):
    today = timezone.localdate()
    preset = params.get("range", "30d")
    if params.get("from") and params.get("to"):
        start, end = dt.date.fromisoformat(params["from"]), dt.date.fromisoformat(params["to"])
    elif preset == "mtd":
        start, end = today.replace(day=1), today
    else:
        days = int(preset.rstrip("d")) if preset.rstrip("d").isdigit() else 30
        start, end = today - dt.timedelta(days=days - 1), today
    length = (end - start).days + 1
    return start, end, start - dt.timedelta(days=length), start - dt.timedelta(days=1)


def _orders(params, start, end):
    qs = m.Order.objects.filter(order_date__range=(start, end)).exclude(status__in=["cancelled", "rejected"])
    if params.get("branch"):
        qs = qs.filter(branch_id=params["branch"])
    if params.get("customer"):
        qs = qs.filter(customer_id=params["customer"])
    if params.get("job_type"):
        qs = qs.filter(job_type=params["job_type"])
    return qs


def _trips(params, start, end):
    qs = m.Trip.objects.filter(order__in=_orders(params, start, end)).exclude(status="cancelled")
    return qs


def _core(params, start, end):
    orders = _orders(params, start, end)
    trips = _trips(params, start, end)
    revenue = orders.aggregate(s=Sum("sell_rate"))["s"] or Decimal(0)
    cost = trips.aggregate(s=Sum("buy_rate"))["s"] or Decimal(0)
    done = [t for t in trips.filter(status="completed")]
    on_time = [t for t in done if t.delay_minutes <= 15]
    days = (end - start).days + 1
    own_fleet = m.Vehicle.objects.filter(vendor__isnull=True).exclude(status="inactive")
    if params.get("branch"):
        own_fleet = own_fleet.filter(branch_id=params["branch"])
    fleet_n = own_fleet.count()
    # utilisation = distinct (vehicle, day) pairs with an own-fleet trip / (own vehicles x days)
    busy = set()
    for t in trips.filter(vehicle__in=own_fleet).exclude(actual_start__isnull=True):
        s = timezone.localdate(t.actual_start)
        e = timezone.localdate(t.actual_end) if t.actual_end else s
        d = s
        while d <= e:
            if start <= d <= end:
                busy.add((t.vehicle_id, d))
            d += dt.timedelta(days=1)
    util = round(100 * len(busy) / (fleet_n * days), 1) if fleet_n else 0
    return dict(orders=orders.count(), trips_completed=len(done),
                on_time_pct=round(100 * len(on_time) / len(done), 1) if done else None,
                late_trips=len(done) - len(on_time),
                revenue=float(revenue), cost=float(cost),
                margin_pct=round(100 * float(revenue - cost) / float(revenue), 1) if revenue and cost else None,
                cost_coverage_pct=round(100 * trips.filter(buy_rate__gt=0).count() / trips.count(), 1) if trips.exists() else None,
                fleet_utilisation_pct=util)


def _delta(a, b):
    if a is None or b in (None, 0):
        return None
    return round(100 * (a - b) / b, 1)


def fleet_snapshot(branch=None):
    """One definition of fleet counts, reused by dashboard, control tower and lists."""
    v = m.Vehicle.objects.filter(vendor__isnull=True)
    d = m.Driver.objects.all()
    if branch:
        v, d = v.filter(branch_id=branch), d.filter(branch_id=branch)
    busy_ids = set(m.Trip.objects.filter(status="in_progress", vehicle__in=v).values_list("vehicle", flat=True))
    on_trip = len(busy_ids)
    idle_qs = v.filter(status="active").exclude(pk__in=busy_ids)
    today = timezone.localdate()
    soon = today + dt.timedelta(days=30)
    return dict(own_vehicles=v.exclude(status="inactive").count(), in_maintenance=v.filter(status="maintenance").count(),
                on_lease=v.filter(status="on_lease").count(), on_trip=on_trip, idle=idle_qs.count(), idle_vehicles=list(idle_qs.values("id", "plate_number", "branch__name")),
                drivers_active=d.filter(status="active").count(),
                drivers_present_today=m.DriverAttendance.objects.filter(date=today, present=True, driver__in=d).count(),
                trailers=m.Trailer.objects.exclude(status="inactive").count(),
                documents_expiring_30d=m.AssetDocument.objects.filter(expiry_date__range=(today, soon)).count(),
                documents_expired=m.AssetDocument.objects.filter(expiry_date__lt=today).count())


def dashboard(params):
    expire_statuses()
    start, end, pstart, pend = _period(params)
    cur, prev = _core(params, start, end), _core(params, pstart, pend)
    kpis = {k: {"value": v, "previous": prev[k], "delta_pct": _delta(v, prev[k]) if isinstance(v, (int, float)) else None} for k, v in cur.items()}
    orders = _orders(params, start, end)
    trips = _trips(params, start, end)

    # daily series
    series = defaultdict(lambda: {"orders": 0, "revenue": 0.0, "cost": 0.0, "trips": 0})
    for o in orders.values("order_date", "sell_rate"):
        s = series[o["order_date"].isoformat()]; s["orders"] += 1; s["revenue"] += float(o["sell_rate"])
    for t in trips.select_related("order").values("order__order_date", "buy_rate"):
        s = series[t["order__order_date"].isoformat()]; s["trips"] += 1; s["cost"] += float(t["buy_rate"])
    days, d = [], start
    while d <= end:
        days.append({"date": d.isoformat(), **series[d.isoformat()]}); d += dt.timedelta(days=1)

    funnel = dict(orders.values_list("status").annotate(n=Count("id")))
    by_customer = [dict(customer=r["customer__company_name"], orders=r["n"], revenue=float(r["rev"]))
                   for r in orders.values("customer__company_name").annotate(n=Count("id"), rev=Sum("sell_rate")).order_by("-rev")[:5]]
    by_job = [dict(job_type=r["job_type"], orders=r["n"], revenue=float(r["rev"])) for r in orders.values("job_type").annotate(n=Count("id"), rev=Sum("sell_rate"))]
    own = trips.filter(vehicle__isnull=False).count(); market = trips.filter(vendor__isnull=False).count()
    lanes = []
    for r in trips.filter(status="completed").values("order__lane").annotate(n=Count("id")).order_by("-n")[:8]:
        lt = [t for t in trips.filter(status="completed", order__lane=r["order__lane"])]
        lane = m.Lane.objects.get(pk=r["order__lane"])
        late = sum(1 for t in lt if t.delay_minutes > 15)
        lanes.append(dict(lane=str(lane), trips=len(lt), on_time_pct=round(100 * (len(lt) - late) / len(lt), 1),
                          avg_delay_min=round(sum(t.delay_minutes for t in lt) / len(lt))))
    branches = []
    for b in m.Branch.objects.all():
        c = _core({**params, "branch": b.id}, start, end)
        if c["orders"]:
            branches.append(dict(branch=b.name, currency=b.currency, **c))
    today = timezone.localdate()
    inv = m.Invoice.objects.all()
    unbilled = m.Order.objects.filter(status__in=["completed", "ready_for_invoice"])
    finance = dict(
        unbilled_value=float(unbilled.aggregate(s=Sum("sell_rate"))["s"] or 0), unbilled_orders=unbilled.count(),
        invoiced_value=float(inv.filter(invoice_date__range=(start, end)).aggregate(s=Sum("total"))["s"] or 0),
        overdue_value=float(inv.filter(status__in=["sent", "accepted"], due_date__lt=today).aggregate(s=Sum("total"))["s"] or 0),
        overdue_count=inv.filter(status__in=["sent", "accepted"], due_date__lt=today).count())
    bids = m.Bid.objects.filter(bid_start__date__range=(start, end))
    invited = sum(b.vendors_invited.count() for b in bids); responded = m.BidResponse.objects.filter(bid__in=bids).count()
    ri = m.RateInquiry.objects.filter(created_at__date__range=(start, end))
    commercial = dict(
        bid_response_rate_pct=round(100 * responded / invited, 1) if invited else None,
        rate_hit_rate_pct=round(100 * ri.filter(rate_found=True).count() / ri.count(), 1) if ri.exists() else None,
        contract_coverage_pct=round(100 * orders.filter(contract__isnull=False).count() / orders.count(), 1) if orders.exists() else None,
        outsourced_pct=round(100 * market / (own + market), 1) if own + market else None,
        confirmed_without_truck=m.Order.objects.filter(status="confirmed").exclude(trips__vehicle__isnull=False).exclude(trips__vendor__isnull=False).count())
    return dict(period=dict(start=start, end=end, prev_start=pstart, prev_end=pend), currency=_currency(params),
                kpis=kpis, series=days, funnel=funnel, top_customers=by_customer, by_job_type=by_job,
                fleet_mix=dict(own=own, market=market), lanes=lanes, branches=branches, finance=finance,
                commercial=commercial, fleet=fleet_snapshot(params.get("branch")), attention=attention())


def _currency(params):
    if params.get("branch"):
        return m.Branch.objects.get(pk=params["branch"]).currency
    cur = set(m.Branch.objects.values_list("country__currency", flat=True))
    return cur.pop() if len(cur) == 1 else "MIXED"


def attention():
    now = timezone.now()
    in_prog = m.Trip.objects.filter(status="in_progress")
    return dict(
        late=[t.number for t in in_prog if t.delay_minutes > 15],
        no_eta=list(in_prog.filter(eta__isnull=True).values_list("number", flat=True)),
        stale=list(in_prog.filter(actual_start__lt=now - dt.timedelta(days=3)).values_list("number", flat=True)),
        gps_silent=list(in_prog.filter(Q(last_gps_at__isnull=True) | Q(last_gps_at__lt=now - dt.timedelta(minutes=30))).values_list("number", flat=True)),
        need_truck_24h=list(m.Trip.objects.filter(status="unassigned", planned_start__lte=now + dt.timedelta(hours=24)).values_list("number", flat=True)),
        stuck_orders=list(m.Order.objects.filter(status__in=["pending", "confirmed"], updated_at__lt=now - dt.timedelta(hours=48)).values_list("number", flat=True)),
    )


def trip_card(t):
    now = timezone.now()
    risk = "late" if t.delay_minutes > 15 else ("no_eta" if not t.eta else ("at_risk" if t.planned_end and t.eta > t.planned_end else "on_track"))
    gps = "silent" if not t.last_gps_at or t.last_gps_at < now - dt.timedelta(minutes=30) else "ok"
    return dict(id=t.id, number=t.number, order=t.order.number, order_id=t.order_id, lane=str(t.order.lane), customer=str(t.order.customer),
                job_type=t.order.job_type, status=t.status, risk=risk, gps=gps,
                truck=(str(t.vehicle) if t.vehicle else (f"Market · {t.vendor}" if t.vendor else None)),
                driver=t.driver.name if t.driver else None, planned_start=t.planned_start, planned_end=t.planned_end,
                eta=t.eta, delay_minutes=t.delay_minutes, stale=bool(t.actual_start and t.actual_start < now - dt.timedelta(days=3)))


def control_tower(params):
    now = timezone.now()
    qs = m.Trip.objects.select_related("order__lane__source", "order__lane__destination", "order__customer", "vehicle", "vendor", "driver")
    if params.get("branch"):
        qs = qs.filter(order__branch_id=params["branch"])
    on_road = [trip_card(t) for t in qs.filter(status="in_progress")]
    order = {"late": 0, "no_eta": 1, "at_risk": 2, "on_track": 3}
    on_road.sort(key=lambda c: (order[c["risk"]], -c["delay_minutes"]))
    nxt = [trip_card(t) for t in qs.filter(status__in=["assigned", "unassigned"], planned_start__range=(now, now + dt.timedelta(hours=24)))]
    arr = [trip_card(t) for t in qs.filter(status="in_progress", eta__range=(now, now + dt.timedelta(hours=24)))]
    need = [c for c in nxt if c["status"] == "unassigned"]
    fleet = fleet_snapshot(params.get("branch"))
    return dict(updated_at=now, tiles=dict(on_road=len(on_road), at_risk=sum(c["risk"] in ("late", "at_risk", "no_eta") for c in on_road),
                need_truck=len(need), gps_silent=sum(c["gps"] == "silent" for c in on_road), idle=fleet["idle"],
                completed_today=qs.filter(status="completed", actual_end__date=timezone.localdate()).count()),
                on_road=on_road, departures=nxt, arrivals=arr, fleet=fleet,
                idle_vehicles=fleet["idle_vehicles"])
