import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://customer.dats24.be/wps/portal/datscustomer/nl/b2c/locator"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[@class='locatorMapData']/text()"))
    js = json.loads(text)["stores"]

    for j in js:
        adr1 = j.get("street") or ""
        adr2 = j.get("houseNumber") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = j.get("city")
        postal = j.get("postalCode")
        country_code = "BE"
        store_number = j.get("id")
        location_name = j.get("name")
        page_url = f"https://customer.dats24.be/wps/portal/datscustomer/nl/b2c/locator#!/{store_number}"
        latitude = j.get("lat")
        longitude = j.get("lng")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            store_number=store_number,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://dats24.be/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
