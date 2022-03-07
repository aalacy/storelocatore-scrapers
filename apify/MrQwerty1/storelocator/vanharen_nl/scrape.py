from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def translate(text):
    days = {
        "ma": "Monday",
        "di": "Tuesday",
        "wo": "Wednesday",
        "do": "Thursday",
        "vr": "Friday",
        "za": "Saturday",
        "zo": "Sunday",
    }
    for k, v in days.items():
        text = text.replace(k, v)

    return text


def fetch_data(sgw: SgWriter):
    api = "https://www.vanharen.nl/nl-nl/rest/v2/vanharen-nl/mosaic/stores?&fields=FULL&format=json&pageSize=500"
    r = session.get(api, headers=headers)
    js = r.json()["stores"]

    for j in js:
        a = j.get("address") or {}
        street_address = f'{a.get("line1")} {a.get("line2") or ""}'.strip()
        city = a.get("town") or ""
        if "Amsterdam" in city:
            city = "Amsterdam"
        if "Rotterdam" in city:
            city = "Rotterdam"
        if "-" in city and "´s" not in city:
            city = city.split("-")[0].strip()
        location_name = f"VANHAREN {city}"
        reg = a.get("region") or {}
        state = reg.get("state")
        postal = a.get("postalCode")
        phone = a.get("phone")
        if not phone:
            continue

        geo = j.get("geoPoint") or {}
        latitude = geo.get("latitude")
        longitude = geo.get("longitude")
        store_number = j.get("name")

        _tmp = []
        try:
            hours = j["openingHours"]["weekDayOpeningList"]
        except:
            hours = []

        for h in hours:
            day = h.get("weekDay")
            if h.get("closed"):
                _tmp.append(f"{day}: Closed")
                continue
            start = h["openingTime"]["formattedHour"]
            end = h["closingTime"]["formattedHour"]
            _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = translate(";".join(_tmp))

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="NL",
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.vanharen.nl/"
    page_url = "https://www.vanharen.nl/nl-nl/storefinder"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
