from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = (
        "https://www.recheio.pt/wp-admin/admin-ajax.php?action=store_search&autoload=1"
    )
    r = session.get(api, headers=headers)

    for j in r.json():
        location_name = j.get("store")
        latitude = j.get("lat")
        longitude = j.get("lng")
        phone = j.get("phone") or ""
        if "|" in phone:
            phone = phone.split("|")[0].strip()
        page_url = j.get("url")
        store_number = j.get("id")
        street_address = f'{j.get("address")} {j.get("address2") or ""}'.strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")

        source = j.get("hours") or "<html></html>"
        tree = html.fromstring(source)
        hours = tree.xpath("//text()")
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="PT",
            phone=phone,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.recheio.pt/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
