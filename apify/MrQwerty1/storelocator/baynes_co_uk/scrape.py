import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), '.wcsl(')]/text()"))
    text = text.split(".wcsl(")[1].split("}});")[0] + "}}"
    js = json.loads(text)["places"]

    for j in js:
        loc = j.get("location") or {}
        e = loc.get("extra_fields") or {}
        raw_address = j.get("address")
        street_address = e.get("shop-street") or ""
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = e.get("shop-town") or ","
        if "," in city:
            city = city.split(",")[0].strip()
        postal = e.get("shop-postal-code")
        country_code = "GB"
        store_number = j.get("id")
        location_name = j.get("title")
        phone = e.get("shop-phone-number")
        latitude = loc.get("lat")
        longitude = loc.get("lng")

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
        for day in days:
            inter = e.get(f"opening-hours-{day}")
            if inter:
                _tmp.append(f"{day.capitalize()}: {inter}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            raw_address=raw_address,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://baynes.co.uk/"
    page_url = "https://baynes.co.uk/our-shops/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
