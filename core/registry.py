"""Declarative resource registry: one entry per module drives the API, list page, filters,
CSV export and (multi-step) forms in the Vue app. Keeps ~40 modules consistent."""
from . import models as m

R = {}


def reg(key, model, *, group, title, columns, search=(), filters=(), dates=(), status=None, steps=None,
        extra=(), ordering="-id", icon="", readonly=False, detail=False, create=True):
    R[key] = dict(key=key, model=model, group=group, title=title, columns=list(columns), search=list(search),
                  filters=list(filters), dates=list(dates), status=status, steps=steps, extra=list(extra),
                  ordering=ordering, icon=icon, readonly=readonly, detail=detail, create=create and not readonly)


# ------------------------------------------------------------- operations
reg("orders", m.Order, group="Operations", title="Orders", icon="📦", detail=True,
    columns=["number", "customer", "lane", "loading_at", "status", "sell_rate", "currency", "job_type", "branch", "order_date",
             "load_cutoff", "offload_cutoff", "product", "vendor", "num_vehicles", "vehicles_committed", "allocation_status",
             "weight_t", "quantity", "cost", "margin", "contract", "reference", "created_by", "created_at", "updated_at"],
    search=["number", "reference", "shipment_reference", "customer__company_name", "commodity"],
    filters=["branch", "customer", "job_type", "vendor", "product", "lane__source", "lane__destination"],
    dates=["order_date", "loading_at"], status="status",
    extra=["vehicles_committed", "allocation_status", "cost", "margin"],
    steps=[("Order details", ["customer", "branch", "job_type", "reference", "shipment_reference", "order_date", "loading_at"]),
           ("Vehicles & cargo", ["product", "container_type", "num_vehicles", "weight_t", "commodity", "quantity", "temperature_controlled", "hazardous", "stackable"]),
           ("Route", ["lane", "pickup_address", "pickup_contact", "load_cutoff", "drop_address", "drop_contact", "offload_cutoff"]),
           ("Pricing & notes", ["sell_rate", "vendor", "notes", "status"])])
reg("trips", m.Trip, group="Operations", title="Trip scheduling", icon="🗓️", ordering="planned_start",
    columns=["order", "number", "leg_no", "planned_start", "status", "vehicle", "driver", "trailer", "vendor", "market_truck_plate",
             "eta", "delay_minutes", "last_milestone", "container_ref", "cro_ref", "buy_rate", "sell_rate", "remarks", "created_at"],
    search=["number", "order__number", "driver__name", "vehicle__plate_number", "container_ref"],
    filters=["order__branch", "order__customer", "order__job_type", "vehicle", "driver", "vendor"], dates=["planned_start"],
    status="status", extra=["delay_minutes"],
    steps=[("Leg", ["order", "leg_no", "planned_start", "planned_end", "eta", "distance_km"]),
           ("Allocation", ["vehicle", "driver", "trailer", "vendor", "market_truck_plate", "status"]),
           ("Execution & money", ["actual_start", "actual_end", "last_milestone", "last_gps_at", "buy_rate", "sell_rate", "container_ref", "cro_ref", "remarks"])])
reg("lease-orders", m.LeaseOrder, group="Operations", title="Lease orders", icon="🔑",
    columns=["number", "reference", "branch", "customer", "lease_type", "start_date", "end_date", "rate", "status", "created_at", "updated_at"],
    search=["number", "reference", "customer__company_name"], filters=["branch", "customer", "lease_type"], dates=["start_date", "end_date"], status="status")
reg("vendor-orders", m.VendorOrder, group="Operations", title="Vendor orders", icon="🤝",
    columns=["number", "vendor", "order", "vehicles_requested", "vehicles_committed", "vehicles_remaining", "rate", "currency", "status", "created_at"],
    search=["number", "order__number", "vendor__company_name"], filters=["vendor", "order__customer"], status="status", extra=["vehicles_remaining"])

# ------------------------------------------------------------- rates
reg("rates", m.RateMaster, group="Rates", title="Rate master", icon="💲",
    columns=["lane", "product", "customer", "rate", "currency", "valid_from", "valid_to", "status", "created_at", "updated_at"],
    search=["lane__source__name", "lane__destination__name", "customer__company_name"], filters=["lane__source", "lane__destination", "product", "customer"], status="status")
reg("rfqs", m.RFQ, group="Rates", title="RFQs", icon="📨",
    columns=["name", "month", "contract_expiry", "cycle1_start", "cycle1_end", "cycle2_start", "cycle2_end", "status", "created_at"],
    search=["name"], dates=["month"], status="status",
    steps=[("Details", ["name", "month", "notes"]), ("Cycles and expiry", ["cycle1_start", "cycle1_end", "cycle2_start", "cycle2_end", "contract_expiry"]), ("Vendors", ["vendors", "status"])])
reg("bids", m.Bid, group="Rates", title="Bids", icon="🔨",
    columns=["number", "customer", "status", "bid_start", "bid_end", "lane", "product", "commodity", "weight_t", "num_vehicles",
             "loading_at", "target_rate", "winning_vendor", "winning_rate", "responses_label", "created_at"],
    search=["number", "customer__company_name", "commodity"], filters=["customer", "product", "winning_vendor"], dates=["bid_start"], status="status",
    extra=["responses_label"],
    steps=[("Enquiry", ["customer", "product", "commodity", "num_vehicles", "weight_t", "lane", "loading_at", "temperature_controlled", "hazardous", "stackable", "customer_remarks"]),
           ("Bid window & vendors", ["bid_start", "bid_end", "target_rate", "currency", "vendors_invited"]),
           ("Award", ["winning_vendor", "winning_rate", "status"])])
reg("bid-responses", m.BidResponse, group="Rates", title="Bid responses", icon="✉️",
    columns=["bid", "vendor", "rate", "vehicles_offered", "remarks", "created_at"], filters=["bid", "vendor"])
reg("rate-inquiries", m.RateInquiry, group="Rates", title="Rate requests", icon="❓",
    columns=["number", "lane", "product", "customer", "loading_date", "commodity", "weight_t", "rate_found", "buy_price", "sell_price", "currency", "status", "created_at"],
    search=["number", "customer__company_name", "commodity"], filters=["customer", "product", "rate_found"], dates=["loading_date"], status="status")
reg("sourcing", m.SourcingRequest, group="Rates", title="Sourcing", icon="🔎",
    columns=["number", "inquiry", "num_vehicles", "target_buy_rate", "bid", "status", "created_at"], search=["number"], status="status")
reg("quotations", m.Quotation, group="Rates", title="Quotations", icon="🧾",
    columns=["number", "customer", "lane", "product", "amount", "currency", "valid_till", "status", "created_at", "updated_at"],
    search=["number", "customer__company_name"], filters=["customer"], dates=["valid_till"], status="status")
reg("customer-contracts", m.CustomerContract, group="Rates", title="Customer contracts", icon="📄",
    columns=["number", "customer", "job_type", "start_date", "end_date", "status", "num_rates", "created_at", "updated_at"],
    search=["number", "customer__company_name"], filters=["customer", "job_type"], dates=["start_date"], status="status")
reg("vendor-contracts", m.VendorContract, group="Rates", title="Vendor contracts", icon="📃",
    columns=["number", "vendor", "rfq", "job_type", "uom", "rate_basis", "start_date", "end_date", "status", "num_rates", "created_at"],
    search=["number", "vendor__company_name"], filters=["vendor", "job_type", "uom"], dates=["start_date"], status="status")

# ------------------------------------------------------------- partners
reg("customers", m.Customer, group="Partners", title="Customers", icon="🏢", ordering="company_name",
    columns=["company_name", "code", "group", "country", "salesperson", "billing_frequency", "fleet_preference", "status", "contact_name",
             "phone", "email", "payment_terms_days", "customer_type", "rate_basis", "credit_limit", "domestic_markup_pct",
             "cross_border_markup_pct", "bid_markup_pct", "invoicing_company", "created_at", "updated_at"],
    search=["company_name", "code", "contact_name", "email"], filters=["customer_type", "group", "country"], status="status",
    steps=[("Company", ["company_name", "code", "customer_type", "group", "country", "salesperson"]),
           ("Contact", ["contact_name", "phone", "email"]),
           ("Commercial", ["billing_frequency", "fleet_preference", "payment_terms_days", "rate_basis", "credit_limit", "domestic_markup_pct", "cross_border_markup_pct", "bid_markup_pct"]),
           ("Invoicing", ["invoicing_company", "billing_tax_id", "billing_address", "status"])])
reg("vendors", m.Vendor, group="Partners", title="Vendors", icon="🚚", ordering="company_name",
    columns=["company_name", "code", "vendor_type", "country", "status", "contact_name", "phone", "email", "rating", "rfq_eligible", "bid_eligible", "created_at", "updated_at"],
    search=["company_name", "code", "email"], filters=["vendor_type", "country", "rfq_eligible", "bid_eligible"], status="status")

# ------------------------------------------------------------- fleet
reg("drivers", m.Driver, group="Fleet", title="Drivers", icon="🧑‍✈️", ordering="name",
    columns=["name", "employee_id", "branch", "vendor", "status", "vehicle", "phone_code", "phone", "language", "license_class", "license_expiry", "passcode_status", "created_at", "updated_at"],
    search=["name", "employee_id", "phone"], filters=["branch", "vehicle", "language", "vendor"], status="status", extra=["passcode_status"])
reg("attendance", m.DriverAttendance, group="Fleet", title="Driver attendance", icon="🕘", ordering="-date",
    columns=["date", "driver", "check_in", "check_out", "present"], search=["driver__name"], filters=["driver", "present", "driver__branch"], dates=["date"])
reg("vehicles", m.Vehicle, group="Fleet", title="Vehicles", icon="🚛", ordering="plate_number",
    columns=["plate_number", "asset_code", "vehicle_type", "fleet_number", "branch", "base_location", "chassis_number", "fuel_type", "vendor",
             "status", "expected_return", "fuel_efficiency_kmpl", "odometer_km", "model", "make_year", "created_at", "updated_at"],
    search=["plate_number", "asset_code", "fleet_number", "chassis_number"], filters=["branch", "vehicle_type", "vendor", "base_location", "fuel_type"], status="status",
    steps=[("Vehicle details", ["vehicle_type", "plate_number", "fleet_number", "chassis_number", "model", "colour", "make_year", "asset_code"]),
           ("Performance and fuel", ["fuel_type", "fuel_efficiency_kmpl", "odometer_km"]),
           ("Ownership", ["branch", "base_location", "vendor", "status", "expected_return"])])
reg("trailers", m.Trailer, group="Fleet", title="Trailers", icon="🛻",
    columns=["trailer_number", "trailer_type", "fleet_number", "branch", "chassis_number", "status", "created_at", "updated_at"],
    search=["trailer_number", "fleet_number"], filters=["branch", "trailer_type"], status="status")
reg("tyres", m.Tyre, group="Fleet", title="Tyres", icon="🛞",
    columns=["vehicle", "position", "serial_number", "fitted_on", "tread_depth_mm", "condition", "replacement_due_km", "created_at"],
    search=["serial_number", "vehicle__plate_number"], filters=["vehicle", "condition"])
reg("asset-transfers", m.AssetTransfer, group="Fleet", title="Asset transfers", icon="🔁",
    columns=["driver", "vehicle", "from_branch", "to_branch", "transfer_date", "status", "created_at"], filters=["from_branch", "to_branch"], status="status")
reg("documents", m.AssetDocument, group="Fleet", title="Documents", icon="📑", ordering="expiry_date",
    columns=["document_type", "document_number", "vehicle", "driver", "expiry_date", "created_at"], search=["document_number"],
    filters=["document_type", "vehicle", "driver"], dates=["expiry_date"])

# ------------------------------------------------------------- workshop
reg("maintenance", m.Maintenance, group="Workshop", title="Maintenance", icon="🔧",
    columns=["number", "vehicle", "status", "maintenance_type", "priority", "in_house", "start_date", "end_date", "cost", "created_at", "updated_at"],
    search=["number", "vehicle__plate_number"], filters=["vehicle", "maintenance_type", "in_house", "priority"], dates=["start_date"], status="status",
    steps=[("Asset", ["vehicle", "maintenance_type", "priority", "in_house"]), ("Schedule and cost", ["start_date", "end_date", "cost", "status"]), ("Notes", ["notes"])])
reg("job-cards", m.JobCard, group="Workshop", title="Job cards", icon="🧰",
    columns=["number", "maintenance", "activity", "priority", "technician", "bay", "status", "odometer_km", "opened_at", "closed_at", "created_at"],
    search=["number", "activity", "description"], filters=["priority", "technician", "bay"], status="status")
reg("material-requests", m.MaterialRequest, group="Workshop", title="Material requests", icon="📦",
    columns=["job_card", "part_code", "part_name", "quantity", "status", "remarks", "created_at", "updated_at"], search=["part_code", "part_name"], status="status")
reg("gate-passes", m.GatePass, group="Workshop", title="Gate passes", icon="🚧",
    columns=["number", "pass_type", "status", "vehicle", "job_card", "driver", "at", "odometer_km", "created_at"], filters=["vehicle", "pass_type"], status="status")

# ------------------------------------------------------------- finance
reg("invoices", m.Invoice, group="Finance", title="Invoices", icon="🧾",
    columns=["number", "customer", "invoice_date", "invoicing_company", "due_date", "currency", "base_amount", "tax_name", "tax_rate",
             "tax_amount", "total", "status", "is_overdue", "paid_on", "created_at"],
    search=["number", "customer__company_name", "billing_name"], filters=["customer", "branch"], dates=["invoice_date", "due_date"], status="status",
    extra=["is_overdue"],
    steps=[("Customer and billing", ["customer", "branch", "billing_name", "billing_tax_id", "billing_address", "invoicing_company"]),
           ("Dates", ["invoice_date", "status", "paid_on"]), ("Orders", ["orders"])])
reg("vendor-invoices", m.VendorInvoice, group="Finance", title="Vendor invoices", icon="📥",
    columns=["number", "vendor", "vendor_order", "invoice_date", "due_date", "currency", "base_amount", "tax_rate", "tax_amount", "total", "status", "created_at"],
    search=["number", "vendor__company_name"], filters=["vendor"], dates=["invoice_date"], status="status")
reg("allowances", m.Allowance, group="Finance", title="Allowances", icon="💵",
    columns=["trip", "driver", "fixed_amount", "fuel_amount", "border_amount", "actual_km", "rule_km", "additional_km", "additional_km_rate", "total", "status", "payout"],
    search=["trip__number", "driver__name"], filters=["driver"], status="status", extra=["additional_km"])
reg("payouts", m.Payout, group="Finance", title="Payouts", icon="💳",
    columns=["number", "driver", "period_start", "period_end", "payout_date", "fuel_cost", "total", "remarks", "created_at"], search=["number", "driver__name"],
    filters=["driver"], dates=["payout_date"])
reg("reports", m.Report, group="Insights", title="Reports", icon="📊",
    columns=["number", "name", "report_type", "date_from", "date_to", "branch", "status", "created_at"], filters=["report_type", "branch"], status="status")

# ------------------------------------------------------------- configuration
for key, model, title, cols, *f in [
    ("countries", m.Country, "Countries", ["code", "name", "currency", "timezone", "phone_code"]),
    ("tax-rules", m.TaxRule, "Tax rules", ["country", "currency", "name", "rate", "valid_from", "status"], ["country"]),
    ("branches", m.Branch, "Branches", ["name", "code", "country", "branch_type", "contact_person", "phone", "email", "address", "status"], ["country", "branch_type"]),
    ("locations", m.Location, "Locations", ["name", "code", "location_type", "country", "branch", "latitude", "longitude", "status"], ["country", "branch", "location_type"]),
    ("lanes", m.Lane, "Lanes", ["source", "destination", "service_type", "distance_km", "turnaround_hours", "via", "status"], ["source", "destination", "service_type"]),
    ("products", m.Product, "Products", ["name", "job_type", "charge_code"], ["job_type"]),
    ("vehicle-types", m.VehicleType, "Vehicle types", ["name", "charge_code", "payload_t", "length_cm", "width_cm", "height_cm", "trailer_required"]),
    ("trailer-types", m.TrailerType, "Trailer types", ["name"]),
    ("container-types", m.ContainerType, "Container types", ["name", "size_ft", "charge_code"]),
    ("customer-groups", m.CustomerGroup, "Customer groups", ["name"]),
    ("milestones", m.Milestone, "Milestones", ["sequence", "name", "milestone_type", "document_required"]),
    ("charges", m.Charge, "Charges", ["name", "code", "charge_type", "category", "gl_code", "taxable", "auto_apply"]),
    ("document-types", m.DocumentType, "Document types", ["name", "module", "mandatory", "expiry_required", "reminder_days"], ["module"]),
    ("technicians", m.Technician, "Technicians", ["name", "capacity", "open_jobs"]),
    ("workshop-bays", m.WorkshopBay, "Workshop bays", ["name", "location", "capacity"]),
    ("allowance-rules", m.AllowanceRule, "Allowance rules", ["lane", "vehicle_type", "rule_km", "fixed_amount", "fuel_amount", "border_amount", "additional_km_rate"], ["vehicle_type"]),
]:
    reg(key, model, group="Configuration", title=title, columns=cols, search=["name"] if hasattr(model, "name") and key not in ("lanes",) else [],
        filters=f[0] if f else [], status="status" if any(fl.name == "status" for fl in model._meta.fields) else None,
        extra=["open_jobs"] if key == "technicians" else [])

# computed properties used by extras
def _bid_responses_label(s):
    if hasattr(s, "_prefetched_objects_cache"):
        r = len(s._prefetched_objects_cache.get("responses", [])) if "responses" in s._prefetched_objects_cache else s.responses.count()
        v = len(s._prefetched_objects_cache.get("vendors_invited", [])) if "vendors_invited" in s._prefetched_objects_cache else s.vendors_invited.count()
        return f"{r}/{v}"
    return f"{s.responses.count()}/{s.vendors_invited.count()}"

def _technician_open_jobs(s):
    if hasattr(s, "_prefetched_objects_cache") and "jobcard_set" in s._prefetched_objects_cache:
        c = sum(1 for j in s._prefetched_objects_cache["jobcard_set"] if j.status in m.JobCard.OPEN_STATES)
        return f"{c}/{s.capacity}"
    return f"{s.jobcard_set.filter(status__in=m.JobCard.OPEN_STATES).count()}/{s.capacity}"

m.Bid.responses_label = property(_bid_responses_label)
m.Driver.passcode_status = property(lambda s: "Set" if s.passcode_hash else "Not set")
m.Technician.open_jobs = property(_technician_open_jobs)
