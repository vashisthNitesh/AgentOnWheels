import csv
import datetime as dt
from decimal import Decimal

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError as DjValidationError
from django.db import models as djm
from django.db.models import Count
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import pagination, serializers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView

from . import models as m
from . import services
from .registry import R

MODEL_KEY = {}
for k, c in R.items():
    MODEL_KEY.setdefault(c["model"], k)


class Pagination(pagination.PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 500


def field_type(f):
    if f.many_to_many:
        return "m2m"
    if f.is_relation:
        return "fk"
    if f.choices:
        return "choice"
    return {djm.BooleanField: "bool", djm.DateTimeField: "datetime", djm.DateField: "date", djm.DecimalField: "decimal",
            djm.TextField: "text", djm.EmailField: "email"}.get(type(f)) or (
        "int" if isinstance(f, (djm.IntegerField,)) else "char")


def label(f):
    v = str(f.verbose_name)
    return v[:1].upper() + v[1:]


def model_fields(model):
    out = {}
    for f in list(model._meta.fields) + list(model._meta.many_to_many):
        if f.name == "id":
            continue
        d = dict(name=f.name, label=label(f), type=field_type(f), help=str(f.help_text or ""),
                 required=not (f.blank or f.null or f.has_default()) and f.editable, readonly=not f.editable or f.auto_created)
        if f.choices:
            d["choices"] = [{"value": a, "label": str(b)} for a, b in f.choices]
        if f.is_relation:
            d["resource"] = MODEL_KEY.get(f.related_model)
        if isinstance(f, djm.DecimalField) and f.name in ("sell_rate", "buy_rate", "rate", "total", "amount", "base_amount", "tax_amount"):
            d["money"] = True
        out[f.name] = d
    return out


def meta_for(key):
    c = R[key]
    fields = model_fields(c["model"])
    for e in c["extra"]:
        fields[e] = dict(name=e, label=e.replace("_", " ").capitalize(), type="computed", readonly=True)
    filters = []
    for fl in c["filters"]:
        base = fl.split("__")
        mdl, f = c["model"], None
        for part in base:
            f = mdl._meta.get_field(part)
            mdl = f.related_model or mdl
        fd = dict(name=fl, label=(label(f) if len(base) == 1 else " ".join(base).replace("_", " ").capitalize()), type=field_type(f))
        if f.choices:
            fd["choices"] = [{"value": a, "label": str(b)} for a, b in f.choices]
        if f.is_relation:
            fd["resource"] = MODEL_KEY.get(f.related_model)
        filters.append(fd)
    return dict(key=key, title=c["title"], group=c["group"], icon=c["icon"], columns=c["columns"], fields=fields, filters=filters,
                dates=[dict(name=d, label=fields[d]["label"]) for d in c["dates"]], status=c["status"],
                status_choices=fields[c["status"]].get("choices") if c["status"] else None,
                steps=[{"title": t, "fields": fs} for t, fs in c["steps"]] if c["steps"] else None,
                search=bool(c["search"]), detail=c["detail"], create=c["create"])


def make_serializer(key):
    c = R[key]
    model = c["model"]
    attrs = {}
    for f in model._meta.fields:
        if f.is_relation:
            attrs[f"{f.name}_label"] = serializers.StringRelatedField(source=f.name, read_only=True)
        if f.choices:
            attrs[f"{f.name}_label"] = serializers.CharField(source=f"get_{f.name}_display", read_only=True)
    for f in model._meta.many_to_many:
        attrs[f"{f.name}_label"] = serializers.StringRelatedField(source=f.name, many=True, read_only=True)
    for e in c["extra"]:
        attrs[e] = serializers.ReadOnlyField()
    attrs["display"] = serializers.SerializerMethodField()
    attrs["get_display"] = lambda self, o: str(o)

    def validate(self, data):
        m2m = {f.name for f in model._meta.many_to_many}
        inst = self.instance or model()
        snapshot = {k: getattr(inst, k) for k in data if k not in m2m} if self.instance else {}
        for k, v in data.items():
            if k not in m2m:
                setattr(inst, k, v)
        try:
            inst.clean()
        except DjValidationError as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, "error_dict") else {"non_field_errors": e.messages})
        finally:
            for k, v in snapshot.items():
                setattr(inst, k, v)
        return data

    attrs["validate"] = validate
    attrs["Meta"] = type("Meta", (), {"model": model, "fields": "__all__"})
    return type(f"{model.__name__}Serializer", (serializers.ModelSerializer,), attrs)


def build_filterset_fields(c):
    out = {f: ["exact"] for f in c["filters"]}
    if c["status"]:
        out[c["status"]] = ["exact", "in"]
    for d in c["dates"]:
        out[d] = ["gte", "lte", "date__gte", "date__lte"] if isinstance(c["model"]._meta.get_field(d), djm.DateTimeField) else ["gte", "lte"]
    return out


class BaseViewSet(viewsets.ModelViewSet):
    key = None

    def get_queryset(self):
        c = R[self.key]
        model = c["model"]
        qs = model.objects.all()
        rel = []
        for f in model._meta.fields:
            if f.is_relation and f.related_model:
                rel.append(f.name)
                if f.related_model == m.Lane:
                    rel.extend([f"{f.name}__source", f"{f.name}__destination"])
                elif f.related_model in (m.Location, m.Branch, m.Customer, m.Vendor):
                    rel.append(f"{f.name}__country")
                elif f.related_model == m.Trip:
                    rel.extend([f"{f.name}__vehicle", f"{f.name}__driver", f"{f.name}__vendor", f"{f.name}__order__lane__source", f"{f.name}__order__lane__destination"])

        qs = qs.select_related(*rel)

        # Reverse relation / m2m prefetches needed by extra fields
        if self.key == "orders":
            qs = qs.prefetch_related("trips")
        elif self.key == "bids":
            qs = qs.prefetch_related("responses", "vendors_invited")
        elif self.key == "technicians":
            qs = qs.prefetch_related("jobcard_set")
        elif self.key == "rfqs":
            qs = qs.prefetch_related("vendors")

        ordering = self.request.query_params.get("ordering") if hasattr(self.request, "query_params") else None
        return qs.order_by(*(ordering and [] or [c["ordering"]]))

    def _bump_ver(self):
        try:
            v = cache.get(f"ver:{self.key}", 1)
            cache.set(f"ver:{self.key}", v + 1, 86400)
        except Exception:
            pass

    def list(self, request, *args, **kwargs):
        v = cache.get(f"ver:{self.key}", 1)
        ck = f"list:{self.key}:{v}:{sorted(request.query_params.items())}"
        cached = cache.get(ck)
        if cached is not None:
            return Response(cached)
        resp = super().list(request, *args, **kwargs)
        cache.set(ck, resp.data, 60)
        return resp

    def perform_create(self, ser):
        kw = {"created_by": self.request.user.get_username()} if hasattr(R[self.key]["model"], "created_by") else {}
        ser.save(**kw)
        self._bump_ver()

    def perform_update(self, ser):
        ser.save()
        self._bump_ver()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        self._bump_ver()

    @action(detail=False)
    def counts(self, request):
        c = R[self.key]
        sf = c["status"]
        if not sf:
            return Response({"all": c["model"].objects.count()})
        v = cache.get(f"ver:{self.key}", 1)
        ck = f"cnt:{self.key}:{v}:{sorted(request.query_params.items())}"
        cached = cache.get(ck)
        if cached is not None:
            return Response(cached)
        params = request.query_params.copy()
        for k in list(params):
            if k.startswith(sf):
                params.pop(k)
        request._request.GET = params
        qs = self.filter_queryset(c["model"].objects.all())
        data = {r[sf]: r["n"] for r in qs.order_by().values(sf).annotate(n=Count("id"))}
        data["all"] = sum(data.values())
        cache.set(ck, data, 60)
        return Response(data)

    @action(detail=False)
    def export(self, request):
        c = R[self.key]
        qs = self.filter_queryset(self.get_queryset())[:20000]
        ser = self.get_serializer_class()(qs, many=True)
        meta = meta_for(self.key)
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = f'attachment; filename="{self.key}-{timezone.localdate()}.csv"'
        w = csv.writer(resp)
        cols = c["columns"]
        w.writerow([meta["fields"].get(col, {"label": col})["label"] for col in cols])
        for row in ser.data:
            w.writerow([row.get(f"{col}_label", row.get(col)) if not isinstance(row.get(f"{col}_label"), list) else "; ".join(row[f"{col}_label"]) for col in cols])
        return resp


VIEWSETS = {}
for key, c in R.items():
    VIEWSETS[key] = type(f"{c['model'].__name__}ViewSet", (BaseViewSet,), dict(
        key=key, serializer_class=make_serializer(key), filterset_fields=build_filterset_fields(c),
        search_fields=c["search"], ordering_fields="__all__",
        http_method_names=["get", "head", "options"] if c["readonly"] else ["get", "post", "put", "patch", "delete", "head", "options"]))


# --------------------------------------------------------------- custom actions
def full(self, request, pk=None):
    o = self.get_object()
    data = self.get_serializer(o).data
    data["trips"] = VIEWSETS["trips"].serializer_class(o.trips.all(), many=True).data
    data["vendor_orders"] = VIEWSETS["vendor-orders"].serializer_class(o.vendor_orders.all(), many=True).data
    data["invoices"] = [dict(id=i.id, number=i.number, status=i.status, total=i.total) for i in o.invoices.all()]
    data["next_statuses"] = [{"value": s, "label": dict(m.Order.STATUS)[s]} for s in m.Order.FLOW[o.status]]
    data["lane_detail"] = dict(source=str(o.lane.source), destination=str(o.lane.destination), service_type=o.lane.get_service_type_display(), distance_km=o.lane.distance_km)
    return Response(data)


def transition(self, request, pk=None):
    o = self.get_object()
    new = request.data.get("status")
    if new not in m.Order.FLOW[o.status]:
        return Response({"status": [f"Cannot move from {o.get_status_display()} to {new}."]}, status=400)
    if new == "confirmed" and not o.trips.exists():
        for i in range(o.num_vehicles):
            m.Trip.objects.create(order=o, leg_no=i + 1, planned_start=o.loading_at, planned_end=o.offload_cutoff or o.loading_at + dt.timedelta(hours=o.lane.turnaround_hours or 6))
    o.status = new
    o.save()
    return full(self, request, pk)


VIEWSETS["orders"].full = action(detail=True)(full)
VIEWSETS["orders"].transition = action(detail=True, methods=["post"])(transition)


def set_passcode(self, request, pk=None):
    d = self.get_object()
    try:
        d.set_passcode(request.data.get("passcode", ""))
    except DjValidationError as e:
        return Response({"passcode": e.messages}, status=400)
    d.save()
    return Response({"ok": True, "passcode_set_at": d.passcode_set_at})


VIEWSETS["drivers"].set_passcode = action(detail=True, methods=["post"])(set_passcode)


def _invoice_save(orig):
    def perform(self, ser):
        orig(self, ser)
        inv = ser.instance
        inv.save()  # recompute totals after m2m orders are set
        inv.orders.filter(status="ready_for_invoice").update(status="invoiced")
    return perform


VIEWSETS["invoices"].perform_create = _invoice_save(BaseViewSet.perform_create)
VIEWSETS["invoices"].perform_update = _invoice_save(lambda self, ser: ser.save())


def download(self, request, pk=None):
    r = self.get_object()
    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = f'attachment; filename="{r.number}.csv"'
    w = csv.writer(resp)
    orders = m.Order.objects.filter(order_date__range=(r.date_from, r.date_to))
    if r.branch_id:
        orders = orders.filter(branch=r.branch)
    if r.report_type == "orders":
        w.writerow(["Order", "Date", "Customer", "Lane", "Status", "Sell", "Cost", "Margin", "Currency"])
        for o in orders.select_related("customer", "lane__source", "lane__destination"):
            w.writerow([o.number, o.order_date, o.customer, o.lane, o.get_status_display(), o.sell_rate, o.cost, o.margin, o.currency])
    elif r.report_type == "trips":
        w.writerow(["Trip", "Order", "Status", "Vehicle", "Vendor", "Driver", "Planned start", "Actual end", "Delay min", "Buy", "Sell"])
        for t in m.Trip.objects.filter(order__in=orders):
            w.writerow([t.number, t.order.number, t.get_status_display(), t.vehicle or "", t.vendor or "", t.driver or "", t.planned_start, t.actual_end or "", t.delay_minutes, t.buy_rate, t.sell_rate])
    elif r.report_type == "revenue_by_customer":
        w.writerow(["Customer", "Orders", "Revenue"])
        for row in orders.values("customer__company_name").annotate(n=Count("id"), s=djm.Sum("sell_rate")).order_by("-s"):
            w.writerow([row["customer__company_name"], row["n"], row["s"]])
    elif r.report_type == "vehicle_utilisation":
        w.writerow(["Vehicle", "Trips", "Revenue"])
        for v in m.Vehicle.objects.all():
            ts = m.Trip.objects.filter(vehicle=v, order__in=orders)
            w.writerow([v, ts.count(), ts.aggregate(s=djm.Sum("sell_rate"))["s"] or 0])
    elif r.report_type == "driver_attendance":
        w.writerow(["Date", "Present", "Absent", "Active drivers"])
        d = r.date_from
        total = m.Driver.objects.filter(status="active").count()
        while d <= r.date_to:
            p = m.DriverAttendance.objects.filter(date=d, present=True).count()
            w.writerow([d, p, total - p, total]); d += dt.timedelta(days=1)
    elif r.report_type == "vendor_scorecard":
        w.writerow(["Vendor", "Bids invited", "Responses", "Wins", "Trips"])
        for v in m.Vendor.objects.all():
            w.writerow([v, v.bids_invited.count(), m.BidResponse.objects.filter(vendor=v).count(), v.bids_won.count(), m.Trip.objects.filter(vendor=v, order__in=orders).count()])
    else:
        w.writerow(["Maintenance", "Vehicle", "Type", "Status", "Start", "End", "Cost"])
        for x in m.Maintenance.objects.filter(start_date__range=(r.date_from, r.date_to)):
            w.writerow([x.number, x.vehicle, x.get_maintenance_type_display(), x.get_status_display(), x.start_date, x.end_date or "", x.cost])
    return resp


VIEWSETS["reports"].download = action(detail=True)(download)


# --------------------------------------------------------------- misc endpoints
class LoginThrottle(AnonRateThrottle):
    scope = "login"


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]


@api_view(["GET"])
def me(request):
    u = request.user
    return Response(dict(id=u.id, username=u.username, name=u.get_full_name() or u.username, email=u.email,
                         is_staff=u.is_staff, display_tz=settings.DEFAULT_TIMEZONE_DISPLAY))


@api_view(["GET"])
def meta_index(request):
    groups = {}
    for k, c in R.items():
        groups.setdefault(c["group"], []).append(dict(key=k, title=c["title"], icon=c["icon"]))
    return Response(dict(groups=groups, countries=list(m.Country.objects.values("id", "code", "name", "currency", "timezone"))))


@api_view(["GET"])
def meta_resource(request, key):
    if key not in R:
        return Response({"detail": "Unknown resource"}, status=404)
    ck = f"meta_res:{key}"
    cached = cache.get(ck)
    if cached is None:
        cached = meta_for(key)
        cache.set(ck, cached, 3600)
    return Response(cached)


@api_view(["GET"])
def dashboard(request):
    return Response(services.dashboard(request.query_params))


@api_view(["GET"])
def control_tower(request):
    return Response(services.control_tower(request.query_params))


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    from django.db import connection
    with connection.cursor() as c:
        c.execute("select 1")
    return Response({"ok": True, "time": timezone.now()})
