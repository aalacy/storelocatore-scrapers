import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.denmans.co.uk/den/store-finder"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//div[@data-stores]/@data-stores"))
    js = json.loads(text).values()

    for j in js:
        location_name = j.get("displayName")
        store_number = j.get("name")
        page_url = f"https://www.denmans.co.uk/den/-/store/{store_number}"
        street_address = f'{j.get("line1")} {j.get("line2") or ""}'.strip()
        city = j.get("town")
        postal = j.get("postalCode")
        country = j.get("country")
        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        location_type = j.get("storeType")

        hours = j.get("hours") or ""
        hours_of_operation = (
            hours.replace("true", "Closed")
            .replace(", ", ";")
            .replace("[", "")
            .replace("]", "")
        )

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country,
            location_type=location_type,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.denmans.co.uk/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
