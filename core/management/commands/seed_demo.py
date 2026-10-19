"""Seed realistic, internally-consistent demo data (UAE/GCC operations). Safe to re-run with --reset."""
import datetime as dt
import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core import models as m


class Command(BaseCommand):
    def add_arguments(self, p):
        p.add_argument("--reset", action="store_true")

    def handle(self, *a, reset=False, **kw):
        rnd = random.Random(42)
        if reset:
            for model in reversed(list(m.Stamped.__subclasses__())):
                pass
            from django.apps import apps
            for model in reversed(list(apps.get_app_config("core").get_models())):
                model.objects.all().delete()
        if m.Country.objects.exists():
            self.stdout.write("Already seeded (use --reset)."); return
        now = timezone.now(); today = timezone.localdate()
        with transaction.atomic():
            C = {c[0]: m.Country.objects.create(code=c[0], name=c[1], currency=c[2], timezone=c[3], phone_code=c[4]) for c in [
                ("AE", "United Arab Emirates", "AED", "Asia/Dubai", "+971"), ("SA", "Saudi Arabia", "SAR", "Asia/Riyadh", "+966"),
                ("OM", "Oman", "OMR", "Asia/Muscat", "+968"), ("IN", "India", "INR", "Asia/Kolkata", "+91")]}
            for cc, cur, name, rate in [("AE", "AED", "VAT", 5), ("SA", "SAR", "VAT", 15), ("OM", "OMR", "VAT", 5), ("IN", "INR", "GST", 18)]:
                m.TaxRule.objects.create(country=C[cc], currency=cur, name=name, rate=rate, valid_from=dt.date(2018, 1, 1))
            B = {b[1]: m.Branch.objects.create(name=b[0], code=b[1], country=C[b[2]], branch_type=b[3], contact_person=b[4], phone=b[5], email=f"{b[1].lower()}@agentonwheels.ae")
                 for b in [("Dubai", "DXB", "AE", "local", "Omar Haddad", "+97145550101"), ("Abu Dhabi", "AUH", "AE", "local", "Fatima Noor", "+97125550102"),
                           ("Ras Al Khaimah", "RAK", "AE", "local", "Imran Sheikh", "+97175550103"), ("GCC Cross-border", "GCC", "AE", "cross_border", "Sameer Rao", "+97145550104")]}
            L = {}
            for name, code, typ, cc, br in [("Dubai", "DXB", "city", "AE", "DXB"), ("Jebel Ali Port", "JEA", "port", "AE", "DXB"), ("Sharjah", "SHJ", "city", "AE", "DXB"),
                                            ("Abu Dhabi", "AUH", "city", "AE", "AUH"), ("Khalifa Port", "KHP", "port", "AE", "AUH"), ("Al Ain", "AAN", "city", "AE", "AUH"),
                                            ("Ras Al Khaimah", "RKT", "city", "AE", "RAK"), ("Fujairah", "FJR", "port", "AE", "RAK"), ("Ghuwaifat border", "GHW", "border", "AE", "GCC"),
                                            ("Riyadh", "RUH", "city", "SA", "GCC"), ("Dammam", "DMM", "port", "SA", "GCC"), ("Muscat", "MCT", "city", "OM", "GCC"), ("Sohar", "SOH", "port", "OM", "GCC")]:
                L[code] = m.Location.objects.create(name=name, code=code, location_type=typ, country=C[cc], branch=B[br])
            lane_defs = [("JEA", "DXB", 35, 3), ("JEA", "AUH", 150, 6), ("KHP", "AUH", 70, 4), ("DXB", "SHJ", 30, 3), ("JEA", "RKT", 120, 6),
                         ("AUH", "AAN", 160, 6), ("DXB", "FJR", 130, 6), ("KHP", "DXB", 110, 5), ("JEA", "RUH", 1000, 30), ("DXB", "DMM", 900, 28),
                         ("DXB", "MCT", 420, 14), ("SHJ", "SOH", 260, 10)]
            LN = [m.Lane.objects.create(source=L[s], destination=L[d], distance_km=km, turnaround_hours=h) for s, d, km, h in lane_defs]
            P = {p[0]: m.Product.objects.create(name=p[0], job_type=p[1], charge_code=p[2]) for p in [
                ("3T pickup", "FTL", "TRK3"), ("7T truck", "FTL", "TRK7"), ("Flatbed 40ft", "FTL", "FLB"), ("Curtainsider", "FTL", "CRT"),
                ("Reefer 12m", "FTL", "RFR"), ("20ft container", "FCL", "C20"), ("40ft container", "FCL", "C40")]}
            VT = {v[0]: m.VehicleType.objects.create(name=v[0], payload_t=v[1], length_cm=v[2], width_cm=245, height_cm=260, trailer_required=v[3]) for v in [
                ("Pickup 3T", 3, 420, False), ("Rigid 7T", 7, 650, False), ("Prime mover", 30, 600, True), ("Reefer truck", 12, 1200, False)]}
            TT = {n: m.TrailerType.objects.create(name=n) for n in ["Flatbed trailer", "Curtainsider trailer", "Skeletal trailer"]}
            CT = {n: m.ContainerType.objects.create(name=n, size_ft=s) for n, s in [("20ft dry", 20), ("40ft dry", 40), ("40ft reefer", 40)]}
            G = {n: m.CustomerGroup.objects.create(name=n) for n in ["Intercompany", "Third party"]}
            MS = [m.Milestone.objects.create(name=n, milestone_type=t, sequence=i + 1, document_required=d) for i, (n, t, d) in enumerate(
                [("Reached pickup", "pickup", False), ("Loaded", "pickup", True), ("Departed", "transit", False), ("At border", "border", True),
                 ("Reached drop", "delivery", False), ("POD uploaded", "delivery", True)])]
            m.Charge.objects.create(name="Freight", code="FRT", category="Transport", gl_code="400100", taxable=True, auto_apply=True)
            m.Charge.objects.create(name="Fuel surcharge", code="FSC", category="Surcharge", gl_code="400110", taxable=True)
            m.Charge.objects.create(name="Waiting charges", code="WTG", category="Accessorial", gl_code="400120", taxable=True)
            DT = {n: m.DocumentType.objects.create(name=n, module=mod, mandatory=True, expiry_required=True, reminder_days=30) for n, mod in [
                ("Mulkiya (registration)", "vehicle"), ("Vehicle insurance", "vehicle"), ("Driving licence", "driver"), ("Emirates ID", "driver"), ("Trade licence", "customer")]}

            cust_names = ["Star Foods Trading LLC", "Emirates Steel Industries", "Al Waha Electronics", "Gulf Cement Co", "Desert Rose FMCG", "Noor Pharma Distribution",
                          "Blue Wave Seafood", "Falcon Auto Parts", "Oasis Beverages", "Marina Retail Group", "Arabian Plastics", "Horizon Building Materials"]
            CU = [m.Customer.objects.create(company_name=n, code=f"C{1000 + i}", customer_type=rnd.choice(["shipper", "shipper", "forwarder"]),
                                            group=G["Intercompany" if i < 2 else "Third party"], country=C["AE"], salesperson=rnd.choice(["Aisha K", "Rahul M", "Yousef A"]),
                                            contact_name=f"Contact {i + 1}", phone=f"+9715{rnd.randint(10000000, 99999999)}", email=f"ops{i + 1}@example.ae",
                                            payment_terms_days=rnd.choice([15, 30, 45, 60]), credit_limit=rnd.choice([50000, 100000, 250000]),
                                            domestic_markup_pct=10, cross_border_markup_pct=15, bid_markup_pct=8, billing_tax_id=f"1000{rnd.randint(10000000000, 99999999999)}",
                                            billing_address=f"Office {i + 10}, Business Bay, Dubai") for i, n in enumerate(cust_names)]
            VE = [m.Vendor.objects.create(company_name=n, code=f"V{2000 + i}", vendor_type=t, country=C[cc], rating=rnd.randint(2, 5),
                                          contact_name=f"Dispatcher {i + 1}", phone=f"+9715{rnd.randint(10000000, 99999999)}", email=f"dispatch{i + 1}@vendor.ae")
                  for i, (n, t, cc) in enumerate([("Al Futtaim Haulage", "transporter", "AE"), ("Sahara Movers", "transporter", "AE"), ("Quick Cargo Brokers", "broker", "AE"),
                                                  ("Najd Transport", "transporter", "SA"), ("Muscat Freightlines", "transporter", "OM"), ("Ahmed Owner-Operator", "owner_operator", "AE")])]

            plates = ["DXB-A-11223", "DXB-B-44556", "DXB-C-77889", "AUH-1-23456", "AUH-5-65432", "RAK-K-11122", "DXB-F-90901", "AUH-12-3434", "SHJ-3-78787", "DXB-M-55443"]
            VH = []
            for i, p in enumerate(plates):
                vt = list(VT.values())[i % 4]
                br = [B["DXB"], B["AUH"], B["RAK"], B["DXB"], B["GCC"]][i % 5]
                VH.append(m.Vehicle.objects.create(plate_number=p, asset_code=f"AST-{100 + i}", fleet_number=f"FL{i + 1:03d}", vehicle_type=vt, branch=br,
                                                   base_location=L["DXB"] if br.code in ("DXB", "GCC") else L["AUH" if br.code == "AUH" else "RKT"],
                                                   chassis_number=f"WDB9{rnd.randint(100000000, 999999999)}", fuel_efficiency_kmpl=Decimal(rnd.randint(25, 45)) / 10,
                                                   odometer_km=rnd.randint(40000, 380000), model=rnd.choice(["Actros 2645", "Isuzu NPR", "Volvo FH", "Hino 500"]),
                                                   make_year=rnd.randint(2016, 2025), status="on_lease" if i == 9 else "active"))
            TR = [m.Trailer.objects.create(trailer_number=f"TRL-{300 + i}", trailer_type=list(TT.values())[i % 3], fleet_number=f"TF{i + 1:03d}", branch=B["DXB"]) for i in range(5)]
            dnames = ["Mohammed Rafiq", "Sajid Khan", "Ramesh Kumar", "Abdul Basit", "John Mathew", "Ali Hassan", "Bilal Ahmed", "Sunil Thapa", "Khalid Saeed", "Arif Hussain"]
            DR = []
            for i, n in enumerate(dnames):
                d = m.Driver(name=n, employee_id=f"EMP{500 + i}", branch=VH[i % 9].branch, vehicle=VH[i] if i < 9 else None, phone=f"5{rnd.randint(10000000, 99999999)}",
                             language=rnd.choice(["en", "hi", "ur", "ar"]), license_class="Heavy", license_expiry=today + dt.timedelta(days=rnd.randint(-10, 700)))
                d.set_passcode(f"{rnd.randint(200000, 989898)}7"[:6] if False else str(rnd.randint(200001, 979797)))
                d.save(); DR.append(d)
            for i, v in enumerate(VH):
                m.AssetDocument.objects.create(document_type=DT["Mulkiya (registration)"], vehicle=v, document_number=f"MUL{rnd.randint(100000, 999999)}", expiry_date=today + dt.timedelta(days=rnd.randint(-5, 400)))
                m.AssetDocument.objects.create(document_type=DT["Vehicle insurance"], vehicle=v, document_number=f"INS{rnd.randint(100000, 999999)}", expiry_date=today + dt.timedelta(days=rnd.randint(10, 365)))
            for d in DR:
                m.AssetDocument.objects.create(document_type=DT["Driving licence"], driver=d, document_number=f"DL{rnd.randint(100000, 999999)}", expiry_date=d.license_expiry)
            # attendance for last 30 days, only real active drivers
            att = []
            for k in range(30):
                day = today - dt.timedelta(days=k)
                for d in DR:
                    present = rnd.random() < 0.85
                    ci = timezone.make_aware(dt.datetime.combine(day, dt.time(6, rnd.randint(0, 59)))) if present else None
                    att.append(m.DriverAttendance(driver=d, date=day, check_in=ci, check_out=ci + dt.timedelta(hours=10) if ci and k else None, present=present))
            m.DriverAttendance.objects.bulk_create(att)

            for c in CU[:6]:
                m.CustomerContract.objects.create(customer=c, job_type="FTL", start_date=today - dt.timedelta(days=200), end_date=today + dt.timedelta(days=rnd.choice([-20, 60, 160])), num_rates=len(LN))
            for v in VE[:4]:
                m.VendorContract.objects.create(vendor=v, job_type="FTL", uom="trip", start_date=today - dt.timedelta(days=100), end_date=today + dt.timedelta(days=rnd.choice([-5, 90])), num_rates=6)
            base = {"3T pickup": 1, "7T truck": 1.4, "Flatbed 40ft": 2.2, "Curtainsider": 2.3, "Reefer 12m": 2.8, "20ft container": 1.8, "40ft container": 2.4}
            for ln in LN:
                for pn, f in base.items():
                    cur = "AED"
                    m.RateMaster.objects.create(lane=ln, product=P[pn], rate=Decimal(round((250 + ln.distance_km * 2.1) * f)), currency=cur, valid_from=today - dt.timedelta(days=365))
            m.RateMaster.objects.create(customer=CU[0], lane=LN[0], product=P["7T truck"], rate=Decimal("420"), currency="AED", valid_from=today - dt.timedelta(days=90))

            # orders & trips over last 90 days (+ upcoming)
            for i in range(90):
                odate = today - dt.timedelta(days=rnd.randint(-3, 89))
                ln = rnd.choice(LN[:8] if rnd.random() < 0.8 else LN)
                fcl = ln.source.location_type == "port" and rnd.random() < 0.5
                prod = P[rnd.choice(["20ft container", "40ft container"])] if fcl else P[rnd.choice(["3T pickup", "7T truck", "Flatbed 40ft", "Curtainsider", "Reefer 12m"])]
                nveh = rnd.choice([1, 1, 1, 2])
                rate = m.RateMaster.objects.get(lane=ln, product=prod, customer__isnull=True).rate
                load = timezone.make_aware(dt.datetime.combine(odate + dt.timedelta(days=rnd.randint(0, 2)), dt.time(rnd.randint(5, 18), rnd.choice([0, 30]))))
                br = B["GCC"] if ln.service_type == "cross_border" else ln.source.branch
                o = m.Order.objects.create(customer=rnd.choice(CU), branch=br, job_type="FCL" if fcl else "FTL", reference=f"{'FCL' if fcl else 'FTL'}-{rnd.randint(10000, 99999)}",
                                           order_date=odate, loading_at=load, lane=ln, pickup_address=f"Warehouse {rnd.randint(1, 40)}, {ln.source.name}",
                                           drop_address=f"Site {rnd.randint(1, 40)}, {ln.destination.name}", pickup_contact="+971 50 123 4567", drop_contact="+971 55 765 4321",
                                           load_cutoff=load, offload_cutoff=load + dt.timedelta(hours=float(ln.turnaround_hours)),
                                           product=prod, container_type=CT["20ft dry"] if prod.name.startswith("20") else (CT["40ft dry"] if fcl else None),
                                           commodity=rnd.choice(["Steel coils", "Frozen food", "Electronics", "Cement bags", "Beverages", "Pharma", "Auto parts"]),
                                           num_vehicles=nveh, weight_t=Decimal(rnd.randint(20, 240)) / 10, quantity=rnd.randint(1, 30),
                                           temperature_controlled=prod.name.startswith("Reefer"), sell_rate=Decimal(round(float(rate) * nveh * 1.12)), status="pending", created_by="seed")
                age = (today - odate).days
                if load > now + dt.timedelta(hours=12):
                    target = rnd.choice(["pending", "confirmed"])
                elif rnd.random() < 0.05:
                    target = "cancelled"
                elif age <= 1:
                    target = "active"
                else:
                    target = rnd.choice(["completed", "completed", "ready_for_invoice", "invoiced", "completed"])
                if target == "cancelled":
                    m.Order.objects.filter(pk=o.pk).update(status="cancelled"); continue
                if target == "pending":
                    continue
                m.Order.objects.filter(pk=o.pk).update(status="confirmed"); o.status = "confirmed"
                for leg in range(nveh):
                    market = rnd.random() < 0.25 or ln.service_type == "cross_border" and rnd.random() < 0.6
                    v = None if market else VH[rnd.randint(0, 8)]
                    ps = load + dt.timedelta(minutes=30 * leg)
                    pe = ps + dt.timedelta(hours=float(ln.turnaround_hours))
                    t = m.Trip(order=o, leg_no=leg + 1, planned_start=ps, planned_end=pe, distance_km=ln.distance_km,
                               sell_rate=Decimal(round(float(o.sell_rate) / nveh)),
                               buy_rate=Decimal(round(float(rate) * (0.85 if market else 0.62))))
                    if market:
                        t.vendor = rnd.choice(VE); t.market_truck_plate = f"MKT-{rnd.randint(1000, 9999)}"
                    else:
                        t.vehicle = v; t.driver = v.drivers.first(); t.trailer = rnd.choice(TR) if v.vehicle_type.trailer_required else None
                    if target == "confirmed":
                        if rnd.random() < 0.4:
                            t.vehicle = t.driver = t.vendor = None; t.market_truck_plate = ""
                        t.status = "assigned" if (t.vehicle or t.vendor) else "unassigned"
                    elif target == "active":
                        t.status = "in_progress"; t.actual_start = ps + dt.timedelta(minutes=rnd.randint(0, 40))
                        t.eta = pe + dt.timedelta(minutes=rnd.choice([-20, 0, 10, 60, 120])) if rnd.random() < 0.85 else None
                        t.last_gps_at = now - dt.timedelta(minutes=rnd.choice([2, 5, 8, 45])); t.last_milestone = MS[2]
                    else:
                        t.status = "completed"; t.actual_start = ps + dt.timedelta(minutes=rnd.randint(0, 30))
                        t.actual_end = pe + dt.timedelta(minutes=rnd.choice([-30, -10, 0, 5, 10, 20, 45, 90, 180]))
                        t.last_milestone = MS[5]
                    t.save()
                    if market and t.vendor:
                        m.VendorOrder.objects.create(vendor=t.vendor, order=o, vehicles_requested=1, vehicles_committed=1, rate=t.buy_rate,
                                                     status="ready_for_invoice" if target in ("ready_for_invoice", "invoiced") else "accepted")
                o.refresh_from_db()
                if target in ("ready_for_invoice", "invoiced"):
                    m.Order.objects.filter(pk=o.pk).update(status="ready_for_invoice")
            # invoices for 'invoiced' group: group a few ready orders per customer
            for c in CU:
                ready = list(m.Order.objects.filter(customer=c, status="ready_for_invoice").order_by("order_date"))
                if len(ready) < 2:
                    continue
                batch = ready[: len(ready) // 2 + 1]
                idate = max(o.order_date for o in batch) + dt.timedelta(days=2)
                idate = min(idate, today)
                br = batch[0].branch
                inv = m.Invoice.objects.create(customer=c, branch=br, billing_name=c.company_name, billing_tax_id=c.billing_tax_id, billing_address=c.billing_address,
                                               invoice_date=idate, status=rnd.choice(["draft", "sent", "sent", "paid", "accepted"]), created_by="seed")
                inv.orders.set([o for o in batch if o.branch_id == br.id]); inv.save()
                m.Order.objects.filter(pk__in=[o.pk for o in batch if o.branch_id == br.id]).update(status="invoiced")

            # leases
            m.LeaseOrder.objects.create(reference="LSE-STAR-01", branch=B["DXB"], customer=CU[0], lease_type="monthly", start_date=today - dt.timedelta(days=60), end_date=today - dt.timedelta(days=20), rate=18000)
            lo = m.LeaseOrder.objects.create(reference="LSE-STEEL-02", branch=B["AUH"], customer=CU[1], lease_type="monthly", start_date=today - dt.timedelta(days=10), end_date=today + dt.timedelta(days=80), rate=21000)
            lo.vehicles.set([VH[9]])
            m.LeaseOrder.objects.create(reference="LSE-NOOR-03", branch=B["DXB"], customer=CU[5], lease_type="weekly", start_date=today + dt.timedelta(days=5), end_date=today + dt.timedelta(days=19), rate=6500)

            # RFQ + bids
            rfq = m.RFQ.objects.create(name=f"RFQ {today:%b %Y}", month=today.replace(day=1), contract_expiry=today + dt.timedelta(days=60),
                                       cycle1_start=today - dt.timedelta(days=12), cycle1_end=today - dt.timedelta(days=5), cycle2_start=today - dt.timedelta(days=4), cycle2_end=today + dt.timedelta(days=3))
            rfq.vendors.set(VE)
            for i in range(8):
                st = now - dt.timedelta(days=rnd.randint(-2, 40))
                b = m.Bid.objects.create(customer=rnd.choice(CU), product=P["Flatbed 40ft"], commodity=rnd.choice(["Steel beams", "Machinery", "Pipes"]), num_vehicles=rnd.randint(1, 4),
                                         lane=rnd.choice(LN), bid_start=st, bid_end=st + dt.timedelta(days=2), loading_at=st + dt.timedelta(days=4),
                                         weight_t=Decimal(rnd.randint(100, 280)) / 10, target_rate=Decimal(rnd.randint(9, 30) * 100))
                inv = rnd.sample(VE, 4); b.vendors_invited.set(inv)
                if st < now - dt.timedelta(hours=6):
                    for v in rnd.sample(inv, rnd.randint(0, 3)):
                        m.BidResponse.objects.create(bid=b, vendor=v, rate=b.target_rate * Decimal(rnd.uniform(0.9, 1.2)).quantize(Decimal("0.01")))
                    best = b.responses.order_by("rate").first()
                    if best and rnd.random() < 0.6 and st < now - dt.timedelta(days=3):
                        b.winning_vendor, b.winning_rate, b.status = best.vendor, best.rate, "completed"; b.save()
            # rate inquiries (some lanes without rates trigger sourcing)
            nolane = m.Lane.objects.create(source=L["SHJ"], destination=L["RUH"], distance_km=1050, turnaround_hours=32)
            for i in range(10):
                ln = nolane if i % 4 == 0 else rnd.choice(LN)
                ri = m.RateInquiry(customer=rnd.choice(CU), lane=ln, product=P["Curtainsider"], commodity=rnd.choice(["FMCG", "Furniture", "Tiles"]),
                                   loading_date=today + dt.timedelta(days=rnd.randint(1, 20)), weight_t=Decimal(rnd.randint(50, 200)) / 10)
                ri.save()
                if ri.rate_found:
                    m.RateInquiry.objects.filter(pk=ri.pk).update(status=rnd.choice(["draft", "pending_approval", "approved"]))
            for c in CU[:4]:
                ln = rnd.choice(LN)
                m.Quotation.objects.create(customer=c, lane=ln, product=P["7T truck"], amount=Decimal(rnd.randint(5, 30) * 100), valid_till=today + dt.timedelta(days=rnd.choice([-3, 14, 30])), status=rnd.choice(["draft", "sent"]))

            # workshop
            techs = [m.Technician.objects.create(name=n, capacity=c) for n, c in [("Murad Ali", 4), ("Vinod Pillai", 3), ("Hassan Omar", 4)]]
            bays = [m.WorkshopBay.objects.create(name=n, location=loc, capacity=1) for n, loc in [("Bay 1", "RAK Workshop"), ("Bay 2", "RAK Workshop"), ("Wash bay", "Dubai Yard")]]
            for i, v in enumerate(VH[:7]):
                st = "active" if i in (3, 6) else "closed"
                mt = m.Maintenance.objects.create(vehicle=v, maintenance_type=rnd.choice(["preventive", "breakdown", "tyre"]), status=st, start_date=today - dt.timedelta(days=rnd.randint(1, 50)),
                                                  cost=Decimal(rnd.randint(4, 60) * 100))
                if st == "closed":
                    mt.end_date = mt.start_date + dt.timedelta(days=rnd.randint(0, 4)); mt.save()
                jc = m.JobCard.objects.create(maintenance=mt, activity=rnd.choice(["Engine service", "Brake pads", "Tyre change", "Electrical"]), priority="medium",
                                              technician=techs[i % 3], bay=bays[i % 3], odometer_km=v.odometer_km, description="Scheduled work",
                                              status="in_progress" if st == "active" else "closed")
                m.MaterialRequest.objects.create(job_card=jc, part_code=f"PRT-{rnd.randint(100, 999)}", part_name=rnd.choice(["Oil filter", "Brake pad set", "Tyre 315/80R22.5"]), quantity=rnd.randint(1, 4),
                                                 status="issued" if st == "closed" else "requested")
                m.GatePass.objects.create(vehicle=v, job_card=jc, pass_type="in", driver=v.drivers.first(), odometer_km=v.odometer_km)
            for i in range(6):
                m.Tyre.objects.create(vehicle=VH[i], position=rnd.choice(["FL", "FR", "RL1", "RR1"]), serial_number=f"TY{rnd.randint(100000, 999999)}", fitted_on=today - dt.timedelta(days=rnd.randint(30, 500)),
                                      tread_depth_mm=Decimal(rnd.randint(30, 140)) / 10, replacement_due_km=rnd.randint(5000, 80000))

            # allowances & payouts
            for ln in LN[:8]:
                for vt in VT.values():
                    m.AllowanceRule.objects.create(lane=ln, vehicle_type=vt, rule_km=ln.distance_km, fixed_amount=50, fuel_amount=Decimal(ln.distance_km) * Decimal("0.6"), border_amount=0, additional_km_rate=Decimal("0.5"))
            for t in m.Trip.objects.filter(status="completed", driver__isnull=False, vehicle__isnull=False).select_related("order__lane", "vehicle")[:40]:
                r = m.AllowanceRule.objects.filter(lane=t.order.lane, vehicle_type=t.vehicle.vehicle_type).first()
                if r:
                    m.Allowance.objects.create(trip=t, driver=t.driver, fixed_amount=r.fixed_amount, fuel_amount=r.fuel_amount, border_amount=r.border_amount, actual_km=r.rule_km + rnd.randint(0, 25),
                                               rule_km=r.rule_km, additional_km_rate=r.additional_km_rate, status=rnd.choice(["pending", "approved"]))
            d0 = DR[0]
            m.Payout.objects.create(driver=d0, period_start=today - dt.timedelta(days=45), period_end=today - dt.timedelta(days=15), payout_date=today - dt.timedelta(days=12), fuel_cost=0,
                                    total=sum(a.total for a in m.Allowance.objects.filter(driver=d0)))
            m.Report.objects.create(name="Last 30 days orders", report_type="orders", date_from=today - dt.timedelta(days=30), date_to=today)
            m.Notification.objects.create(level="warning", message="Documents expiring within 30 days — review Fleet ▸ Documents", link="/r/documents")
        from core.services import expire_statuses
        self.stdout.write(f"Expiry pass: {expire_statuses()}")
        self.stdout.write(self.style.SUCCESS(f"Seeded: {m.Order.objects.count()} orders, {m.Trip.objects.count()} trips, {m.Invoice.objects.count()} invoices"))
