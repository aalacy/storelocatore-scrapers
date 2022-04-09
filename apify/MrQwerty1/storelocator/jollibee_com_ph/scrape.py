from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_hoo(j, _any=False):
    _tmp = []
    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    hours = j.get("storeHours") or []
    for h in hours:
        _type = h.get("disposition")
        if _any:
            _type = "PICKUP"

        if _type != "PICKUP":
            continue

        for day in days:
            start = h[day]["openTime"]["timeString"].split(", ")[0]
            end = h[day]["closeTime"]["timeString"].split(", ")[0]
            _tmp.append(f"{day}: {start}-{end}")

        break

    return ";".join(_tmp)


def clean_phone(text):
    text = str(text).replace("?", "")
    start = text
    black_list = [",", ";", "/", "or", "mo", "cp", "-", "    "]
    for b in black_list:
        if b in text.lower():
            text = text.lower().split(b)[0].strip()
    if ":" in text:
        text = text.split(":")[0].strip()
    if "." in text:
        return SgRecord.MISSING
    if text.endswith(")"):
        text = "(".join(text.split("(")[:-1])

    if len(text) < 6:
        fixed = False
        if ";" in start:
            text = start.split(";")[0].strip()
            fixed = True

        if "/" in start:
            text = start.split("/")[0].strip()
            fixed = True

        if "and" in start:
            text = start.split("and")[0].strip()
            fixed = True

        if ":" in start:
            text = start.split(":")[-1].strip()
            fixed = True

        if not fixed:
            text = start

    return text


def fetch_data(sgw: SgWriter):
    api = "https://api.jollibeedelivery.com/mobilem8-web-service/rest/storeinfo/distance?attributes=&disposition=DINE_IN&disposition=DRIVE_THRU&disposition=DELIVERY&disposition=PICKUP&disposition=CURB_SIDE&latitude=14.5995124&longitude=120.9842195&maxResults=1000&radius=5000&radiusUnit=km&statuses=ACTIVE&statuses=TEMP-INACTIVE&statuses=INACTIVE&tenant=jb-ph"
    r = session.get(api)

    for j in r.json()["getStoresResult"]["stores"]:
        store_number = j.get("storeName")
        page_url = f"https://www.jollibeedelivery.com/store-details?id={store_number}"
        location_name = store_number
        pp = j.get("storeProperties") or []
        for p in pp:
            if p.get("propertyKey") == "alias":
                location_name = p.get("propertyValue")
                break
        street_address = j.get("street") or ""
        city = j.get("city") or ""
        if city in street_address:
            street_address = street_address.split(city)[0].strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]
        state = j.get("state") or ""
        postal = j.get("zipCode") or ""
        raw_address = f"{street_address} {city} {state} {postal}"
        country = j.get("country")
        phone = j.get("phoneNumber") or ""
        phone = clean_phone(phone)
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = get_hoo(j)
        if not hours_of_operation:
            hours_of_operation = get_hoo(j, _any=True)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            store_number=store_number,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://jollibee.com.ph"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
