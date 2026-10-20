"""Domain models for AgentOnWheels.

Conventions (fixes for ATS issues):
* All weights are stored in TONNES (field names end with _t). UI always labels the unit.
* All money is Decimal(12,2) plus an explicit currency taken from the branch country.
* Datetimes are stored in UTC; each Country carries an IANA timezone for display.
* Tax comes from TaxRule (per country/currency), never hard-coded.
"""
import datetime as dt
from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.utils import timezone

JOB_TYPES = [("FTL", "FTL"), ("LTL", "LTL"), ("FCL", "FCL")]
ACTIVE = [("active", "Active"), ("inactive", "Inactive")]
M = dict(max_digits=12, decimal_places=2)


def money(v):
    return Decimal(v or 0).quantize(Decimal("0.01"), ROUND_HALF_UP)


class Stamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=80, blank=True, editable=False)

    class Meta:
        abstract = True


def next_number(model, field, prefix):
    """Sequential human number like AOW-ORD-000123 (gap tolerant, locked)."""
    last = model.objects.select_for_update().filter(**{f"{field}__startswith": prefix}).order_by(f"-{field}").values_list(field, flat=True).first()
    n = int(last.rsplit("-", 1)[-1]) + 1 if last else 1
    return f"{prefix}{n:06d}"


class Numbered(Stamped):
    NUMBER_FIELD = "number"
    PREFIX = "AOW-"
    number = models.CharField(max_length=30, unique=True, editable=False, blank=True)

    class Meta:
        abstract = True

    def save(self, *a, **kw):
        if not self.number:
            with transaction.atomic():
                self.number = next_number(type(self), "number", self.PREFIX)
                return super().save(*a, **kw)
        return super().save(*a, **kw)

    def __str__(self):
        return self.number


# ---------------------------------------------------------------- master data
class Country(Stamped):
    code = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=80)
    currency = models.CharField(max_length=3)
    timezone = models.CharField(max_length=50, help_text="IANA timezone, e.g. Asia/Dubai")
    phone_code = models.CharField(max_length=6, blank=True)

    class Meta:
        ordering = ["name"]; verbose_name_plural = "countries"

    def __str__(self):
        return f"{self.name} ({self.currency})"


class TaxRule(Stamped):
    """Configurable tax per country + currency (UAE VAT 5%, India GST 18%, ...)."""
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="tax_rules")
    currency = models.CharField(max_length=3)
    name = models.CharField(max_length=40, help_text="e.g. VAT, GST")
    rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    valid_from = models.DateField(default=dt.date(2000, 1, 1))
    status = models.CharField(max_length=10, choices=ACTIVE, default="active")

    class Meta:
        ordering = ["country__name", "-valid_from"]

    def __str__(self):
        return f"{self.name} {self.rate}% ({self.country.code}/{self.currency})"

    @classmethod
    def for_(cls, country, currency, on=None):
        on = on or timezone.localdate()
        return cls.objects.filter(country=country, currency=currency, status="active", valid_from__lte=on).order_by("-valid_from").first()


class Branch(Stamped):
    TYPES = [("local", "Local"), ("cross_border", "Cross-border"), ("gcc", "GCC")]
    name = models.CharField(max_length=80, unique=True)
    code = models.CharField(max_length=10, unique=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    branch_type = models.CharField(max_length=20, choices=TYPES, default="local")
    contact_person = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=ACTIVE, default="active")

    class Meta:
        ordering = ["name"]; verbose_name_plural = "branches"

    def __str__(self):
        return self.name

    @property
    def currency(self):
        return self.country.currency


class Location(Stamped):
    TYPES = [("city", "City"), ("port", "Port"), ("warehouse", "Warehouse"), ("border", "Border crossing"), ("yard", "Yard")]
    name = models.CharField(max_length=80)
    code = models.CharField(max_length=12, unique=True)
    location_type = models.CharField(max_length=20, choices=TYPES, default="city")
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(max_length=10, choices=ACTIVE, default="active")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, {self.country.code}"


class Lane(Stamped):
    SERVICE = [("domestic", "Domestic"), ("cross_border", "Cross-border")]
    source = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="lanes_out")
    destination = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="lanes_in")
    service_type = models.CharField(max_length=20, choices=SERVICE, editable=False)
    distance_km = models.PositiveIntegerField(default=0)
    turnaround_hours = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    via = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=10, choices=ACTIVE, default="active")

    class Meta:
        unique_together = [("source", "destination", "via")]

    def save(self, *a, **kw):
        self.service_type = "domestic" if self.source.country_id == self.destination.country_id else "cross_border"
        super().save(*a, **kw)

    def __str__(self):
        return f"{self.source.name} → {self.destination.name}"


class Product(Stamped):
    name = models.CharField(max_length=80, unique=True)
    job_type = models.CharField(max_length=3, choices=JOB_TYPES)
    charge_code = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class VehicleType(Stamped):
    name = models.CharField(max_length=60, unique=True)
    charge_code = models.CharField(max_length=20, blank=True)
    payload_t = models.DecimalField("Payload (t)", max_digits=6, decimal_places=2)
    length_cm = models.PositiveIntegerField(default=0)
    width_cm = models.PositiveIntegerField(default=0)
    height_cm = models.PositiveIntegerField(default=0)
    trailer_required = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class TrailerType(Stamped):
    name = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.name


class ContainerType(Stamped):
    name = models.CharField(max_length=60, unique=True)
    size_ft = models.PositiveIntegerField(default=20)
    charge_code = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class CustomerGroup(Stamped):
    name = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.name


class Milestone(Stamped):
    TYPES = [("pickup", "Pickup"), ("transit", "Transit"), ("delivery", "Delivery"), ("border", "Border")]
    name = models.CharField(max_length=60, unique=True)
    milestone_type = models.CharField(max_length=20, choices=TYPES)
    sequence = models.PositiveIntegerField(default=1)
    document_required = models.BooleanField(default=False)

    class Meta:
        ordering = ["sequence"]

    def __str__(self):
        return self.name


class Charge(Stamped):
    name = models.CharField(max_length=60, unique=True)
    code = models.CharField(max_length=20, unique=True)
    charge_type = models.CharField(max_length=20, choices=[("revenue", "Revenue"), ("cost", "Cost")], default="revenue")
    category = models.CharField(max_length=40, blank=True)
    gl_code = models.CharField(max_length=20, blank=True)
    taxable = models.BooleanField(default=True, help_text="Rate comes from the Tax rule of the invoice country/currency")
    auto_apply = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class DocumentType(Stamped):
    MODULES = [("vehicle", "Vehicle"), ("driver", "Driver"), ("customer", "Customer"), ("vendor", "Vendor")]
    name = models.CharField(max_length=60, unique=True)
    module = models.CharField(max_length=20, choices=MODULES)
    mandatory = models.BooleanField(default=False)
    expiry_required = models.BooleanField(default=True)
    reminder_days = models.PositiveIntegerField(default=30)

    def __str__(self):
        return self.name


# ---------------------------------------------------------------- partners
class Customer(Stamped):
    TYPES = [("shipper", "Shipper"), ("forwarder", "Freight forwarder"), ("consignee", "Consignee")]
    BILLING = [("per_trip", "Per trip"), ("weekly", "Weekly"), ("monthly", "Monthly")]
    FLEET = [("any", "Any"), ("own", "Own fleet"), ("market", "Market")]
    BASIS = [("per_trip", "Per trip"), ("per_tonne", "Per tonne"), ("per_km", "Per km")]
    company_name = models.CharField(max_length=120, unique=True)
    code = models.CharField("SAP company code", max_length=20, unique=True)
    customer_type = models.CharField(max_length=20, choices=TYPES, default="shipper")
    group = models.ForeignKey(CustomerGroup, on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    salesperson = models.CharField(max_length=80, blank=True)
    contact_name = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    billing_frequency = models.CharField(max_length=20, choices=BILLING, default="monthly")
    fleet_preference = models.CharField(max_length=20, choices=FLEET, default="any")
    payment_terms_days = models.PositiveIntegerField(default=30, validators=[MaxValueValidator(365)])
    rate_basis = models.CharField("Rate calculation basis", max_length=20, choices=BASIS, default="per_trip")
    credit_limit = models.DecimalField(**M, default=0)
    domestic_markup_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cross_border_markup_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    bid_markup_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    invoicing_company = models.CharField(max_length=120, default="AgentOnWheels Logistics LLC")
    billing_tax_id = models.CharField(max_length=30, blank=True)
    billing_address = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=ACTIVE, default="active")

    class Meta:
        ordering = ["company_name"]

    def __str__(self):
        return self.company_name


class Vendor(Stamped):
    TYPES = [("transporter", "Transporter"), ("broker", "Broker"), ("owner_operator", "Owner operator")]
    company_name = models.CharField(max_length=120, unique=True)
    code = models.CharField("SAP company code", max_length=20, unique=True)
    vendor_type = models.CharField(max_length=20, choices=TYPES, default="transporter")
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    rating = models.PositiveSmallIntegerField("Performance rating (1-5)", default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    contact_name = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    rfq_eligible = models.BooleanField(default=True)
    bid_eligible = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=ACTIVE, default="active")

    class Meta:
        ordering = ["company_name"]

    def __str__(self):
        return self.company_name


# ---------------------------------------------------------------- fleet
class Vehicle(Stamped):
    STATUS = [("active", "Active"), ("maintenance", "In maintenance"), ("on_lease", "On lease"), ("inactive", "Deactivated")]
    FUEL = [("diesel", "Diesel"), ("petrol", "Petrol"), ("electric", "Electric"), ("cng", "CNG")]
    plate_number = models.CharField("Vehicle number", max_length=20, unique=True)
    asset_code = models.CharField(max_length=20, blank=True)
    fleet_number = models.CharField(max_length=20, blank=True)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.PROTECT)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
    base_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    chassis_number = models.CharField(max_length=40, blank=True)
    fuel_type = models.CharField(max_length=10, choices=FUEL, default="diesel")
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, help_text="Empty = own fleet")
    status = models.CharField(max_length=20, choices=STATUS, default="active")
    expected_return = models.DateField(null=True, blank=True)
    fuel_efficiency_kmpl = models.DecimalField("Fuel efficiency (km/L)", max_digits=5, decimal_places=2, null=True, blank=True)
    odometer_km = models.PositiveIntegerField(default=0)
    model = models.CharField(max_length=60, blank=True)
    colour = models.CharField(max_length=30, blank=True)
    make_year = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1980), MaxValueValidator(2100)])

    class Meta:
        ordering = ["plate_number"]

    def __str__(self):
        return self.plate_number

    @property
    def is_own(self):
        return self.vendor_id is None


class Trailer(Stamped):
    STATUS = [("available", "Available"), ("in_use", "In use"), ("maintenance", "In maintenance"), ("inactive", "Deactivated")]
    trailer_number = models.CharField(max_length=20, unique=True)
    trailer_type = models.ForeignKey(TrailerType, on_delete=models.PROTECT)
    fleet_number = models.CharField(max_length=20, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
    chassis_number = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="available")

    def __str__(self):
        return self.trailer_number


class Driver(Stamped):
    STATUS = [("active", "Active"), ("on_lease", "On lease"), ("inactive", "Deactivated")]
    LANG = [("en", "English"), ("ar", "Arabic"), ("hi", "Hindi"), ("ur", "Urdu")]
    name = models.CharField(max_length=80)
    employee_id = models.CharField(max_length=20, unique=True)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, help_text="Empty = internal driver")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name="drivers")
    phone_code = models.CharField(max_length=6, default="+971")
    phone = models.CharField("Contact no.", max_length=20)
    language = models.CharField(max_length=5, choices=LANG, default="en")
    license_class = models.CharField(max_length=20, blank=True)
    license_expiry = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="active")
    passcode_hash = models.CharField(max_length=128, editable=False, blank=True)
    passcode_set_at = models.DateTimeField(null=True, blank=True, editable=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.employee_id})"

    WEAK = {"000000", "111111", "123456", "654321", "123123", "999999"}

    def set_passcode(self, raw):
        raw = str(raw)
        if not raw.isdigit() or len(raw) < 6:
            raise ValidationError("Passcode must be at least 6 digits.")
        if raw in self.WEAK or len(set(raw)) == 1:
            raise ValidationError("Passcode is too easy to guess.")
        self.passcode_hash = make_password(raw)
        self.passcode_set_at = timezone.now()

    def check_passcode(self, raw):
        return bool(self.passcode_hash) and check_password(str(raw), self.passcode_hash)


class DriverAttendance(Stamped):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="attendance")
    date = models.DateField()
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    present = models.BooleanField(default=False, editable=False)

    class Meta:
        unique_together = [("driver", "date")]; ordering = ["-date"]

    def save(self, *a, **kw):
        self.present = self.check_in is not None
        super().save(*a, **kw)


class AssetDocument(Stamped):
    document_type = models.ForeignKey(DocumentType, on_delete=models.PROTECT)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, null=True, blank=True)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True, blank=True)
    document_number = models.CharField(max_length=40)
    expiry_date = models.DateField(null=True, blank=True)

    def clean(self):
        if not (self.vehicle_id or self.driver_id):
            raise ValidationError("Link the document to a vehicle or a driver.")
        if self.document_type_id and self.document_type.expiry_required and not self.expiry_date:
            raise ValidationError({"expiry_date": "This document type requires an expiry date."})


class Tyre(Stamped):
    CONDITION = [("new", "New"), ("good", "Good"), ("worn", "Worn"), ("replace", "Replace now")]
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    position = models.CharField(max_length=20)
    serial_number = models.CharField(max_length=40, unique=True)
    fitted_on = models.DateField()
    tread_depth_mm = models.DecimalField(max_digits=4, decimal_places=1)
    condition = models.CharField(max_length=10, choices=CONDITION, default="good")
    replacement_due_km = models.PositiveIntegerField(default=0)


class AssetTransfer(Stamped):
    STATUS = [("requested", "Requested"), ("completed", "Completed"), ("cancelled", "Cancelled")]
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, null=True, blank=True)
    from_branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="+")
    to_branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="+")
    transfer_date = models.DateField(default=dt.date.today)
    status = models.CharField(max_length=20, choices=STATUS, default="requested")

    def clean(self):
        if not (self.driver_id or self.vehicle_id):
            raise ValidationError("Select a driver and/or a vehicle to transfer.")
        if self.from_branch_id == self.to_branch_id:
            raise ValidationError({"to_branch": "Destination branch must differ from source."})

    def save(self, *a, **kw):
        super().save(*a, **kw)
        if self.status == "completed":
            if self.driver_id:
                Driver.objects.filter(pk=self.driver_id).update(branch=self.to_branch)
            if self.vehicle_id:
                Vehicle.objects.filter(pk=self.vehicle_id).update(branch=self.to_branch)


# ---------------------------------------------------------------- workshop
class Technician(Stamped):
    name = models.CharField(max_length=80, unique=True)
    capacity = models.PositiveIntegerField(default=4, help_text="Max concurrent open job cards")

    def __str__(self):
        return self.name


class WorkshopBay(Stamped):
    name = models.CharField(max_length=60, unique=True)
    location = models.CharField(max_length=60)
    capacity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.location} – {self.name}"


class Maintenance(Numbered):
    PREFIX = "AOW-MNT-"
    STATUS = [("pending", "Pending"), ("accepted", "Accepted"), ("active", "Active"), ("closed", "Closed")]
    TYPES = [("preventive", "Preventive"), ("breakdown", "Breakdown"), ("accident", "Accident"), ("tyre", "Tyre"), ("washing", "Washing")]
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="maintenance")
    maintenance_type = models.CharField(max_length=20, choices=TYPES)
    in_house = models.BooleanField(default=True)
    priority = models.CharField(max_length=10, choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")], default="medium")
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(**M, default=0)
    notes = models.TextField(blank=True)

    def clean(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date cannot be before start date."})

    def save(self, *a, **kw):
        super().save(*a, **kw)
        # single source of truth: vehicle status follows open maintenance
        open_ = Maintenance.objects.filter(vehicle=self.vehicle, status__in=["accepted", "active"]).exists()
        v = self.vehicle
        if open_ and v.status == "active":
            Vehicle.objects.filter(pk=v.pk).update(status="maintenance")
        elif not open_ and v.status == "maintenance":
            Vehicle.objects.filter(pk=v.pk).update(status="active")


class JobCard(Numbered):
    PREFIX = "AOW-JC-"
    STATUS = [("open", "Open"), ("assigned", "Assigned"), ("in_progress", "In progress"), ("on_hold", "On hold"),
              ("pending_approval", "Pending approval"), ("completed", "Completed"), ("closed", "Closed"), ("cancelled", "Cancelled")]
    OPEN_STATES = ["open", "assigned", "in_progress", "on_hold", "pending_approval"]
    maintenance = models.ForeignKey(Maintenance, on_delete=models.CASCADE, related_name="job_cards")
    activity = models.CharField(max_length=60)
    priority = models.CharField(max_length=10, choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")], default="medium")
    technician = models.ForeignKey(Technician, on_delete=models.SET_NULL, null=True, blank=True)
    bay = models.ForeignKey(WorkshopBay, on_delete=models.SET_NULL, null=True, blank=True)
    odometer_km = models.PositiveIntegerField()
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default="open")
    opened_at = models.DateTimeField(default=timezone.now)
    closed_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.status in self.OPEN_STATES:
            dup = JobCard.objects.filter(maintenance__vehicle=self.maintenance.vehicle, activity__iexact=self.activity,
                                         status__in=self.OPEN_STATES).exclude(pk=self.pk)
            if dup.exists():
                raise ValidationError({"activity": f"An open job card for this activity already exists ({dup.first().number})."})
        if self.technician_id and self.status in self.OPEN_STATES:
            load = JobCard.objects.filter(technician=self.technician, status__in=self.OPEN_STATES).exclude(pk=self.pk).count()
            if load >= self.technician.capacity:
                raise ValidationError({"technician": f"{self.technician} is at capacity ({load}/{self.technician.capacity})."})

    def save(self, *a, **kw):
        if self.status in ("completed", "closed") and not self.closed_at:
            self.closed_at = timezone.now()
        super().save(*a, **kw)


class MaterialRequest(Stamped):
    job_card = models.ForeignKey(JobCard, on_delete=models.CASCADE)
    part_code = models.CharField(max_length=30)
    part_name = models.CharField(max_length=60)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=[("requested", "Requested"), ("issued", "Issued"), ("rejected", "Rejected")], default="requested")
    remarks = models.CharField(max_length=200, blank=True)


class GatePass(Numbered):
    PREFIX = "AOW-GP-"
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    job_card = models.ForeignKey(JobCard, on_delete=models.SET_NULL, null=True, blank=True)
    pass_type = models.CharField(max_length=10, choices=[("in", "Gate in"), ("out", "Gate out")])
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    at = models.DateTimeField(default=timezone.now)
    odometer_km = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=[("issued", "Issued"), ("used", "Used"), ("void", "Void")], default="issued")


# ---------------------------------------------------------------- rates & sourcing
class RateMaster(Stamped):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, help_text="Empty = standard tariff for all customers")
    lane = models.ForeignKey(Lane, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    rate = models.DecimalField(**M, validators=[MinValueValidator(Decimal("1"))])
    currency = models.CharField(max_length=3)
    valid_from = models.DateField(default=dt.date.today)
    valid_to = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=ACTIVE, default="active")
    remarks = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = [("customer", "lane", "product", "valid_from")]


class RFQ(Stamped):
    STATUS = [("scheduled", "Scheduled"), ("active", "Active"), ("completed", "Completed")]
    name = models.CharField(max_length=80, unique=True)
    month = models.DateField(help_text="First day of the month covered")
    contract_expiry = models.DateField()
    cycle1_start = models.DateField(); cycle1_end = models.DateField()
    cycle2_start = models.DateField(null=True, blank=True); cycle2_end = models.DateField(null=True, blank=True)
    vendors = models.ManyToManyField(Vendor, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="scheduled")

    class Meta:
        verbose_name = "RFQ"

    def clean(self):
        if self.cycle1_end < self.cycle1_start:
            raise ValidationError({"cycle1_end": "Cycle 1 end is before its start."})
        if self.cycle2_start and self.cycle2_start < self.cycle1_end:
            raise ValidationError({"cycle2_start": "Cycle 2 must start after cycle 1 ends."})

    def __str__(self):
        return self.name


class Bid(Numbered):
    PREFIX = "AOW-BID-"
    STATUS = [("pending", "Pending"), ("active", "Active"), ("closed", "Closed"), ("completed", "Completed"),
              ("cancelled", "Cancelled"), ("expired", "Expired")]
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    commodity = models.CharField(max_length=80, blank=True)
    num_vehicles = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    lane = models.ForeignKey(Lane, on_delete=models.PROTECT)
    bid_start = models.DateTimeField()
    bid_end = models.DateTimeField()
    loading_at = models.DateTimeField()
    weight_t = models.DecimalField("Weight (t)", max_digits=8, decimal_places=2, null=True, blank=True)
    target_rate = models.DecimalField(**M, null=True, blank=True)
    currency = models.CharField(max_length=3, default="AED")
    temperature_controlled = models.BooleanField(default=False)
    hazardous = models.BooleanField(default=False)
    stackable = models.BooleanField(default=False)
    vendors_invited = models.ManyToManyField(Vendor, blank=True, related_name="bids_invited")
    winning_vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name="bids_won")
    winning_rate = models.DecimalField(**M, null=True, blank=True)
    customer_remarks = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="pending")

    def clean(self):
        if self.bid_end and self.bid_start and self.bid_end <= self.bid_start:
            raise ValidationError({"bid_end": "Bid end must be after bid start."})
        if self.loading_at and self.bid_end and self.loading_at < self.bid_end:
            raise ValidationError({"loading_at": "Loading must be after the bid window closes."})
        if self.status == "completed" and not self.winning_vendor_id:
            raise ValidationError({"status": "A bid can only be completed with a winning vendor."})


class BidResponse(Stamped):
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name="responses")
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    rate = models.DecimalField(**M, validators=[MinValueValidator(Decimal("1"))])
    vehicles_offered = models.PositiveIntegerField(default=1)
    remarks = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = [("bid", "vendor")]


class RateInquiry(Numbered):
    PREFIX = "AOW-RI-"
    STATUS = [("draft", "Draft"), ("pending_approval", "Pending approval"), ("approved", "Approved"), ("rejected", "Rejected"), ("sourcing", "Sent to sourcing")]
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    lane = models.ForeignKey(Lane, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    commodity = models.CharField(max_length=80)
    loading_date = models.DateField(null=True, blank=True)
    open_inquiry = models.BooleanField(default=False)
    weight_t = models.DecimalField("Cargo weight (t)", max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    own_truck = models.BooleanField(default=True)
    backload = models.BooleanField(default=False)
    rate_found = models.BooleanField(default=False, editable=False)
    buy_price = models.DecimalField(**M, null=True, blank=True, editable=False)
    sell_price = models.DecimalField(**M, null=True, blank=True)
    currency = models.CharField(max_length=3, default="AED")
    status = models.CharField(max_length=20, choices=STATUS, default="draft")

    class Meta:
        verbose_name_plural = "rate inquiries"

    def clean(self):
        if not self.open_inquiry and not self.loading_date:
            raise ValidationError({"loading_date": "Loading date is required unless this is an open inquiry."})
        if self.status == "approved" and not self.sell_price:
            raise ValidationError({"status": "Cannot approve an inquiry without a sell price (no rate available)."})
        if not self.pk:
            dup = RateInquiry.objects.filter(customer_id=self.customer_id, lane_id=self.lane_id, product_id=self.product_id,
                                             loading_date=self.loading_date, commodity__iexact=self.commodity,
                                             created_at__gte=timezone.now() - dt.timedelta(hours=24))
            if dup.exists():
                raise ValidationError(f"Duplicate of {dup.first().number} created in the last 24h.")

    def lookup_rate(self):
        r = (RateMaster.objects.filter(lane=self.lane, product=self.product, status="active", customer=self.customer).first()
             or RateMaster.objects.filter(lane=self.lane, product=self.product, status="active", customer__isnull=True).first())
        self.rate_found = bool(r)
        if r:
            mk = self.customer.domestic_markup_pct if self.lane.service_type == "domestic" else self.customer.cross_border_markup_pct
            self.buy_price = r.rate
            self.currency = r.currency
            if not self.sell_price:
                self.sell_price = money(Decimal(r.rate) * (1 + Decimal(str(mk)) / 100))
        return r

    def save(self, *a, **kw):
        creating = not self.pk
        self.lookup_rate()
        super().save(*a, **kw)
        if creating and not self.rate_found:
            SourcingRequest.objects.get_or_create(inquiry=self, defaults=dict(num_vehicles=self.quantity))
            RateInquiry.objects.filter(pk=self.pk).update(status="sourcing")


class SourcingRequest(Numbered):
    PREFIX = "AOW-SR-"
    STATUS = [("open", "Open"), ("bid_created", "Bid created"), ("sourced", "Sourced"), ("cancelled", "Cancelled")]
    inquiry = models.OneToOneField(RateInquiry, on_delete=models.CASCADE)
    num_vehicles = models.PositiveIntegerField(default=1)
    target_buy_rate = models.DecimalField(**M, null=True, blank=True)
    bid = models.ForeignKey(Bid, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="open")


class Quotation(Numbered):
    PREFIX = "AOW-QT-"
    STATUS = [("draft", "Draft"), ("sent", "Sent"), ("accepted", "Accepted"), ("rejected", "Rejected"), ("expired", "Expired")]
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    lane = models.ForeignKey(Lane, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    amount = models.DecimalField(**M, validators=[MinValueValidator(Decimal("1"))])
    currency = models.CharField(max_length=3, default="AED")
    valid_till = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS, default="draft")
    notes = models.TextField(blank=True)


class CustomerContract(Numbered):
    PREFIX = "AOW-CC-"
    STATUS = [("pending", "Pending"), ("active", "Active"), ("expired", "Expired")]
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    job_type = models.CharField(max_length=3, choices=JOB_TYPES)
    start_date = models.DateField(); end_date = models.DateField()
    num_rates = models.PositiveIntegerField("No. of rates", default=0)
    remarks = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="pending", editable=False)

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date is before start date."})

    def save(self, *a, **kw):
        self.status = contract_status(self.start_date, self.end_date)
        super().save(*a, **kw)


class VendorContract(Numbered):
    PREFIX = "AOW-VC-"
    STATUS = CustomerContract.STATUS
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    rfq = models.ForeignKey(RFQ, on_delete=models.SET_NULL, null=True, blank=True)
    job_type = models.CharField(max_length=3, choices=JOB_TYPES)
    uom = models.CharField("UOM", max_length=10, choices=[("trip", "Trip"), ("tonne", "Tonne"), ("km", "Km")], default="trip")
    rate_basis = models.CharField(max_length=20, choices=[("fixed", "Fixed"), ("slab", "Slab")], default="fixed")
    start_date = models.DateField(); end_date = models.DateField()
    num_rates = models.PositiveIntegerField("No. of rates", default=0)
    status = models.CharField(max_length=20, choices=STATUS, default="pending", editable=False)

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date is before start date."})

    def save(self, *a, **kw):
        self.status = contract_status(self.start_date, self.end_date)
        super().save(*a, **kw)


def contract_status(start, end, today=None):
    today = today or timezone.localdate()
    if end < today:
        return "expired"
    return "active" if start <= today else "pending"


# ---------------------------------------------------------------- operations
class Order(Numbered):
    PREFIX = "AOW-ORD-"
    STATUS = [("pending", "Pending"), ("confirmed", "Confirmed"), ("active", "Active"), ("completed", "Completed"),
              ("ready_for_invoice", "Ready for invoice"), ("invoiced", "Invoice generated"), ("cancelled", "Cancelled"), ("rejected", "Rejected")]
    FLOW = {"pending": ["confirmed", "rejected", "cancelled"], "confirmed": ["active", "cancelled"], "active": ["completed", "cancelled"],
            "completed": ["ready_for_invoice"], "ready_for_invoice": ["invoiced"], "invoiced": [], "cancelled": [], "rejected": []}
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="orders")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
    job_type = models.CharField(max_length=3, choices=JOB_TYPES)
    reference = models.CharField("Reference number", max_length=40, blank=True)
    shipment_reference = models.CharField(max_length=40, blank=True)
    order_date = models.DateField(default=dt.date.today)
    loading_at = models.DateTimeField("Loading date/time")
    lane = models.ForeignKey(Lane, on_delete=models.PROTECT)
    pickup_address = models.CharField(max_length=200, blank=True)
    pickup_contact = models.CharField(max_length=80, blank=True)
    drop_address = models.CharField(max_length=200, blank=True)
    drop_contact = models.CharField(max_length=80, blank=True)
    load_cutoff = models.DateTimeField(null=True, blank=True)
    offload_cutoff = models.DateTimeField(null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    container_type = models.ForeignKey(ContainerType, on_delete=models.SET_NULL, null=True, blank=True)
    commodity = models.CharField(max_length=80)
    num_vehicles = models.PositiveIntegerField("Number of vehicles", default=1, validators=[MinValueValidator(1)])
    weight_t = models.DecimalField("Cargo weight (t)", max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    quantity = models.PositiveIntegerField(default=1)
    temperature_controlled = models.BooleanField(default=False)
    hazardous = models.BooleanField(default=False)
    stackable = models.BooleanField(default=False)
    sell_rate = models.DecimalField(**M, validators=[MinValueValidator(Decimal("1"))])
    currency = models.CharField(max_length=3, editable=False)
    contract = models.ForeignKey(CustomerContract, on_delete=models.SET_NULL, null=True, blank=True, editable=False)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-order_date", "-id"]

    def clean(self):
        if self.load_cutoff and self.offload_cutoff and self.offload_cutoff < self.load_cutoff:
            raise ValidationError({"offload_cutoff": "Offload cut-off must be after load cut-off."})
        if self.order_date and self.loading_at and self.loading_at.date() < self.order_date - dt.timedelta(days=1):
            raise ValidationError({"loading_at": "Loading cannot be before the order date."})
        if self.product_id and self.product.job_type != self.job_type and not (self.job_type == "LTL" and self.product.job_type == "FTL"):
            raise ValidationError({"product": f"Product '{self.product}' is for {self.product.job_type}, not {self.job_type}."})
        if self.pk:
            old = Order.objects.filter(pk=self.pk).values_list("status", flat=True).first()
            if old and old != self.status and self.status not in self.FLOW.get(old, []):
                raise ValidationError({"status": f"Cannot move from {dict(self.STATUS)[old]} to {dict(self.STATUS)[self.status]}."})

    def save(self, *a, **kw):
        self.currency = self.branch.country.currency
        self.contract = CustomerContract.objects.filter(customer_id=self.customer_id, job_type=self.job_type,
                                                        start_date__lte=self.order_date, end_date__gte=self.order_date).first()
        super().save(*a, **kw)

    # ---- single source of truth for derived values
    @property
    def vehicles_committed(self):
        if hasattr(self, "_prefetched_objects_cache") and "trips" in self._prefetched_objects_cache:
            return sum(1 for t in self._prefetched_objects_cache["trips"] if t.status != "cancelled" and (t.vehicle_id or t.vendor_id))
        return self.trips.exclude(status="cancelled").filter(models.Q(vehicle__isnull=False) | models.Q(vendor__isnull=False)).count()

    @property
    def allocation_status(self):
        c = self.vehicles_committed
        return "allocated" if c >= self.num_vehicles else ("partial" if c else "pending")

    @property
    def cost(self):
        if hasattr(self, "_prefetched_objects_cache") and "trips" in self._prefetched_objects_cache:
            return money(sum(t.buy_rate for t in self._prefetched_objects_cache["trips"] if t.status != "cancelled"))
        return money(self.trips.exclude(status="cancelled").aggregate(s=models.Sum("buy_rate"))["s"])

    @property
    def margin(self):
        return money(self.sell_rate - self.cost)


class Trip(Numbered):
    PREFIX = "AOW-TRP-"
    STATUS = [("unassigned", "Needs a truck"), ("assigned", "Assigned"), ("in_progress", "In progress"), ("completed", "Completed"), ("cancelled", "Cancelled")]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="trips")
    leg_no = models.PositiveIntegerField(default=1)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name="trips")
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name="trips")
    trailer = models.ForeignKey(Trailer, on_delete=models.SET_NULL, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, help_text="Set for market (outsourced) trucks")
    market_truck_plate = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="unassigned")
    planned_start = models.DateTimeField()
    planned_end = models.DateTimeField(null=True, blank=True)
    eta = models.DateTimeField("ETA", null=True, blank=True)
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    buy_rate = models.DecimalField(**M, default=0, help_text="Own-fleet cost or vendor buy rate")
    sell_rate = models.DecimalField(**M, default=0)
    distance_km = models.PositiveIntegerField(default=0)
    last_milestone = models.ForeignKey(Milestone, on_delete=models.SET_NULL, null=True, blank=True)
    last_gps_at = models.DateTimeField(null=True, blank=True)
    container_ref = models.CharField("Container / shipment ref", max_length=40, blank=True)
    cro_ref = models.CharField("CRO / DPW ref", max_length=40, blank=True)
    remarks = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["planned_start"]

    @property
    def is_market(self):
        return self.vendor_id is not None

    @property
    def delay_minutes(self):
        """Delivery delay vs planned_end (0 if on time / unknown)."""
        if not self.planned_end:
            return 0
        ref = self.actual_end or (timezone.now() if self.status == "in_progress" else None)
        if not ref:
            return 0
        return max(0, int((ref - self.planned_end).total_seconds() // 60))

    def clean(self):
        if self.vehicle_id and self.vendor_id:
            raise ValidationError("Choose either an own vehicle or a market vendor, not both.")
        if self.vehicle_id and self.vehicle.status in ("maintenance", "inactive"):
            raise ValidationError({"vehicle": f"{self.vehicle} is {self.vehicle.get_status_display().lower()}."})
        if self.actual_end and self.actual_start and self.actual_end < self.actual_start:
            raise ValidationError({"actual_end": "Actual end is before actual start."})
        if self.vehicle_id and self.status in ("assigned", "in_progress") and self.planned_end:
            clash = Trip.objects.filter(vehicle=self.vehicle, status__in=["assigned", "in_progress"],
                                        planned_start__lt=self.planned_end, planned_end__gt=self.planned_start).exclude(pk=self.pk)
            if clash.exists():
                raise ValidationError({"vehicle": f"{self.vehicle} is already booked on {clash.first().number} in that window."})

    def save(self, *a, **kw):
        if self.status == "unassigned" and (self.vehicle_id or self.vendor_id):
            self.status = "assigned"
        if self.status == "in_progress" and not self.actual_start:
            self.actual_start = timezone.now()
        if self.status == "completed" and not self.actual_end:
            self.actual_end = timezone.now()
        if not self.sell_rate and self.order_id:
            self.sell_rate = money(self.order.sell_rate / max(self.order.num_vehicles, 1))
        super().save(*a, **kw)
        self.order.sync_status_from_trips() if hasattr(self.order, "sync_status_from_trips") else None


def _sync(order):
    """Order status follows its legs, so 'completed with 0 committed' can never happen."""
    trips = list(order.trips.exclude(status="cancelled"))
    if not trips or order.status in ("cancelled", "rejected", "ready_for_invoice", "invoiced", "pending"):
        return
    st = {t.status for t in trips}
    new = order.status
    if st == {"completed"} and len(trips) >= order.num_vehicles:
        new = "completed"
    elif "in_progress" in st or "completed" in st:
        new = "active"
    if new != order.status:
        Order.objects.filter(pk=order.pk).update(status=new)


Order.sync_status_from_trips = _sync


class LeaseOrder(Numbered):
    PREFIX = "AOW-LSE-"
    STATUS = [("created", "Created"), ("active", "Active"), ("completed", "Completed"), ("cancelled", "Cancelled")]
    TYPES = [("daily", "Daily"), ("weekly", "Weekly"), ("monthly", "Monthly")]
    MIN_DAYS = {"daily": 1, "weekly": 7, "monthly": 28}
    reference = models.CharField("Reference number", max_length=40)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    lease_type = models.CharField(max_length=10, choices=TYPES, default="monthly")
    start_date = models.DateField(); end_date = models.DateField()
    vehicles = models.ManyToManyField(Vehicle, blank=True)
    rate = models.DecimalField(**M, default=0)
    status = models.CharField(max_length=20, choices=STATUS, default="created")

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date is before start date."})
        days = (self.end_date - self.start_date).days + 1
        if days < self.MIN_DAYS[self.lease_type]:
            raise ValidationError({"lease_type": f"A {self.lease_type} lease must cover at least {self.MIN_DAYS[self.lease_type]} days (this covers {days})."})


class VendorOrder(Numbered):
    PREFIX = "AOW-VO-"
    STATUS = [("requested", "Requested"), ("accepted", "Accepted"), ("rejected", "Rejected"), ("ready_for_invoice", "Ready for invoice"), ("invoiced", "Invoiced"), ("cancelled", "Cancelled")]
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="vendor_orders")
    vehicles_requested = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    vehicles_committed = models.PositiveIntegerField(default=0)
    rate = models.DecimalField(**M)
    currency = models.CharField(max_length=3, default="AED")
    status = models.CharField(max_length=20, choices=STATUS, default="requested")

    @property
    def vehicles_remaining(self):
        return max(0, self.vehicles_requested - self.vehicles_committed)

    def clean(self):
        if self.vehicles_committed > self.vehicles_requested:
            raise ValidationError({"vehicles_committed": "Committed cannot exceed requested."})

    def save(self, *a, **kw):
        creating = not self.pk
        super().save(*a, **kw)
        if self.status == "ready_for_invoice" and not hasattr(self, "_skip_vi"):
            VendorInvoice.objects.get_or_create(vendor_order=self, defaults=dict(vendor=self.vendor, base_amount=self.rate * self.vehicles_committed, currency=self.currency))


# ---------------------------------------------------------------- finance
class Invoice(Numbered):
    PREFIX = "AOW-INV-"
    STATUS = [("draft", "Draft"), ("sent", "Sent"), ("accepted", "Accepted"), ("rejected", "Rejected"), ("paid", "Paid")]
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
    invoicing_company = models.CharField(max_length=120, blank=True)
    billing_name = models.CharField(max_length=120)
    billing_tax_id = models.CharField(max_length=30)
    billing_address = models.CharField(max_length=200)
    invoice_date = models.DateField(default=dt.date.today)
    due_date = models.DateField(editable=False)
    currency = models.CharField(max_length=3, editable=False)
    orders = models.ManyToManyField(Order, blank=True, related_name="invoices")
    base_amount = models.DecimalField(**M, default=0, editable=False)
    tax_name = models.CharField(max_length=40, editable=False, blank=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, editable=False)
    tax_amount = models.DecimalField(**M, default=0, editable=False)
    total = models.DecimalField(**M, default=0, editable=False)
    status = models.CharField(max_length=20, choices=STATUS, default="draft")
    paid_on = models.DateField(null=True, blank=True)

    def clean(self):
        if self.invoice_date and self.invoice_date > timezone.localdate() + dt.timedelta(days=1):
            raise ValidationError({"invoice_date": "Invoice date cannot be in the future."})
        if self.paid_on and self.paid_on < self.invoice_date:
            raise ValidationError({"paid_on": "Payment date is before the invoice date."})

    def recalc(self):
        self.currency = self.branch.country.currency
        self.due_date = self.invoice_date + dt.timedelta(days=self.customer.payment_terms_days)
        self.invoicing_company = self.invoicing_company or self.customer.invoicing_company
        rule = TaxRule.for_(self.branch.country, self.currency, self.invoice_date)
        self.tax_name, self.tax_rate = (rule.name, rule.rate) if rule else ("", Decimal(0))
        if self.pk:
            self.base_amount = money(sum((o.sell_rate for o in self.orders.all()), Decimal(0)))
        self.tax_amount = money(self.base_amount * self.tax_rate / 100)
        self.total = money(self.base_amount + self.tax_amount)

    def save(self, *a, **kw):
        if isinstance(self.invoice_date, str):
            self.invoice_date = dt.date.fromisoformat(self.invoice_date)
        self.recalc()
        if self.status == "paid" and not self.paid_on:
            self.paid_on = timezone.localdate()
        super().save(*a, **kw)

    @property
    def is_overdue(self):
        return self.status in ("sent", "accepted") and self.due_date < timezone.localdate()


class VendorInvoice(Numbered):
    PREFIX = "AOW-VINV-"
    STATUS = [("draft", "Draft"), ("approved", "Approved"), ("paid", "Paid"), ("disputed", "Disputed")]
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    vendor_order = models.OneToOneField(VendorOrder, on_delete=models.CASCADE, null=True, blank=True)
    invoice_date = models.DateField(default=dt.date.today)
    due_date = models.DateField(null=True, blank=True)
    currency = models.CharField(max_length=3, default="AED")
    base_amount = models.DecimalField(**M, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, editable=False)
    tax_amount = models.DecimalField(**M, default=0, editable=False)
    total = models.DecimalField(**M, default=0, editable=False)
    status = models.CharField(max_length=20, choices=STATUS, default="draft")

    def save(self, *a, **kw):
        self.due_date = self.due_date or self.invoice_date + dt.timedelta(days=30)
        rule = TaxRule.for_(self.vendor.country, self.currency, self.invoice_date)
        self.tax_rate = rule.rate if rule else 0
        self.tax_amount = money(Decimal(self.base_amount) * self.tax_rate / 100)
        self.total = money(Decimal(self.base_amount) + self.tax_amount)
        super().save(*a, **kw)


class AllowanceRule(Stamped):
    lane = models.ForeignKey(Lane, on_delete=models.CASCADE)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    rule_km = models.PositiveIntegerField()
    fixed_amount = models.DecimalField(**M, default=0)
    fuel_amount = models.DecimalField(**M, default=0)
    border_amount = models.DecimalField(**M, default=0)
    additional_km_rate = models.DecimalField(**M, default=0)

    class Meta:
        unique_together = [("lane", "vehicle_type")]


class Allowance(Stamped):
    STATUS = [("pending", "Pending"), ("approved", "Approved"), ("paid", "Paid")]
    trip = models.OneToOneField(Trip, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT)
    fixed_amount = models.DecimalField(**M, default=0)
    fuel_amount = models.DecimalField(**M, default=0)
    border_amount = models.DecimalField(**M, default=0)
    actual_km = models.PositiveIntegerField(default=0)
    rule_km = models.PositiveIntegerField(default=0)
    additional_km_rate = models.DecimalField(**M, default=0)
    total = models.DecimalField(**M, default=0, editable=False)
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    payout = models.ForeignKey("Payout", on_delete=models.SET_NULL, null=True, blank=True, related_name="allowances")

    @property
    def additional_km(self):
        return max(0, self.actual_km - self.rule_km)

    def save(self, *a, **kw):
        self.total = money(self.fixed_amount + self.fuel_amount + self.border_amount + self.additional_km * self.additional_km_rate)
        super().save(*a, **kw)


class Payout(Numbered):
    PREFIX = "AOW-PO-"
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT)
    period_start = models.DateField(); period_end = models.DateField()
    payout_date = models.DateField()
    fuel_cost = models.DecimalField(**M, default=0)
    total = models.DecimalField(**M, default=0)
    remarks = models.CharField(max_length=200, blank=True)

    def clean(self):
        if self.period_end < self.period_start:
            raise ValidationError({"period_end": "Period end is before start."})
        if self.payout_date < self.period_end:
            raise ValidationError({"payout_date": "Payout date must be on/after the period end."})


class Report(Numbered):
    PREFIX = "AOW-RPT-"
    TYPES = [("orders", "Orders"), ("trips", "Trips"), ("revenue_by_customer", "Revenue by customer"), ("vehicle_utilisation", "Vehicle utilisation"),
             ("driver_attendance", "Driver attendance"), ("vendor_scorecard", "Vendor scorecard"), ("maintenance", "Maintenance")]
    name = models.CharField(max_length=80)
    report_type = models.CharField(max_length=30, choices=TYPES)
    date_from = models.DateField(); date_to = models.DateField()
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=[("generated", "Generated"), ("failed", "Failed")], default="generated", editable=False)

    def clean(self):
        if self.date_to < self.date_from:
            raise ValidationError({"date_to": "End is before start."})


class Notification(Stamped):
    level = models.CharField(max_length=10, choices=[("info", "Info"), ("warning", "Warning"), ("danger", "Danger")], default="info")
    message = models.CharField(max_length=250)
    link = models.CharField(max_length=200, blank=True)
    read = models.BooleanField(default=False)
