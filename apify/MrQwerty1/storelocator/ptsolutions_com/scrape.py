from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = (
        "https://ptsolutions.com/wp-admin/admin-ajax.php?action=store_search&autoload=1"
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)

    for j in r.json():
        location_name = j.get("store") or ""
        location_name = (
            location_name.replace("&#8211;", "-")
            .replace("&#038;", "&")
            .replace("&#8217;", "'")
        )
        page_url = j.get("permalink")
        street_address = f'{j.get("address")} {j.get("address2")}'.strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        country_code = "US"

        store_number = j.get("id")
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")

        _tmp = []
        source = j.get("hours") or "<html></html>"
        root = html.fromstring(source)
        tr = root.xpath("//tr")
        for t in tr:
            day = "".join(t.xpath("./td[1]//text()")).strip()
            time = "".join(t.xpath("./td[2]//text()")).strip()
            _tmp.append(f"{day}: {time}")

        hours_of_operation = ";".join(_tmp)

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
    locator_domain = "https://ptsolutions.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
