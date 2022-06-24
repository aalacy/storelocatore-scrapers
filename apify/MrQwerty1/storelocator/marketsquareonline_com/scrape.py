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
    text = "".join(tree.xpath("//script[contains(text(), 'var locations =')]/text()"))
    text = text.split("var locations =")[1].split("];")[0] + "]"
    js = json.loads(text)

    for j in js:
        adr1 = j.get("address1") or ""
        adr2 = j.get("address2") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zipCode")
        country_code = "US"
        store_number = j.get("storeNumber")
        location_name = j.get("name")
        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = j.get("hourInfo") or ""
        hours_of_operation = hours_of_operation.replace("\n", ";")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.marketsquareonline.com/"
    page_url = (
        "https://www.marketsquareonline.com/contact-us-and-store-info/our-locations/"
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
