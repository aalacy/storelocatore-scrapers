from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://www.ahipokibowl.com/wp-admin/admin-ajax.php?action=store_search&autoload=1"
    page_url = "https://www.ahipokibowl.com/storelocator/"

    r = session.get(api, headers=headers)
    for j in r.json():
        location_name = j.get("store") or ""
        street = f'{j.get("address")} {j.get("address2") or ""}'.strip()
        if "@" in street:
            street = street.split("@")[0].strip()
        source = j.get("hours") or "<html></html>"
        tree = html.fromstring(source)
        hours = tree.xpath("//text()")
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours)
        if "Coming" in location_name:
            hours_of_operation = "Coming Soon"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street,
            city=j.get("city"),
            state=j.get("state"),
            zip_postal=j.get("zip"),
            country_code="US",
            store_number=j.get("id"),
            phone=j.get("phone"),
            location_type=SgRecord.MISSING,
            latitude=j.get("lat"),
            longitude=j.get("lng"),
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.ahipokibowl.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
