from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = (
        "https://mydaiso.com.au/wp-admin/admin-ajax.php?action=store_search&autoload=1"
    )
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        location_name = j.get("store")
        street_address = f'{j.get("address")} {j.get("address2") or ""}'.strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        country = j.get("country")

        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")
        store_number = j.get("id")

        _tmp = []
        text = j.get("hours") or "<html/>"
        tree = html.fromstring(text)
        tr = tree.xpath("//tr")
        for t in tr:
            day = "".join(t.xpath("./td[1]//text()")).strip()
            inter = "".join(t.xpath("./td[2]//text()")).strip()
            _tmp.append(f"{day}: {inter}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://mydaiso.com.au/"
    page_url = "https://mydaiso.com.au/stores/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
