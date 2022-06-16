from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://belchicken.com/wp-content/uploads/ssf-wp-uploads/ssf-data.json"
    r = session.get(api, headers=headers)
    js = r.json()["item"]

    for j in js:
        raw_address = str(j.get("address")).strip()
        line = raw_address.split("  ")
        street_address = line.pop(0).strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = line.pop(0).strip()
        if city.endswith(","):
            city = city[:-1]
        postal = line.pop(0).strip()
        country_code = "BE"
        if len(postal) == 5:
            country_code = "DE"
        store_number = j.get("storeId")
        location_name = j.get("location")

        phone = j.get("telephone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        source = j.get("operatingHours") or ""
        if "Monday" not in source:
            source = j.get("description") or "<html>"

        tree = html.fromstring(source)
        hours = tree.xpath("//text()")
        hours = list(filter(None, [h.replace("\xa0", " ").strip() for h in hours]))
        hours_of_operation = " ".join(hours)
        hours_of_operation = (
            hours_of_operation.replace("!", "")
            .replace(" :", ":")
            .replace(":00 ", ":00;")
            .replace(":30 ", ":30;")
            .replace("0 0", "00")
            .replace("3 0", "30")
            .replace(": 30", ":30")
            .replace(";–", " –")
            .replace("Closed ", "Closed;")
        )

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
    locator_domain = "https://belchicken.com/"
    page_url = "https://belchicken.com/restaurants/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
