from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    hours = tree.xpath("//p[.//strong[contains(text(), 'Hours')]]//text()")
    hours = list(filter(None, [h.replace("Salon Hours:", "").strip() for h in hours]))

    return ";".join(hours)


def fetch_data(sgw: SgWriter):
    api = "https://glosunspa.com/wp-admin/admin-ajax.php?action=store_search&autoload=1"

    r = session.get(api, headers=headers)

    for j in r.json():
        location_name = j.get("store") or ""
        page_url = j.get("permalink")
        street_address = f'{j.get("address")} {j.get("address2")}'.strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        country_code = "US"
        store_number = j.get("id")
        phone = j.get("phone") or ""
        latitude = j.get("lat")
        longitude = j.get("lng")

        hours_of_operation = get_hours(page_url)
        if "closed" in phone.lower():
            hours_of_operation = "Closed"
            phone = SgRecord.MISSING
        if "coming" in location_name.lower():
            hours_of_operation = "Coming Soon"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://glosunspa.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
