from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.mandarinrestaurant.com/wp-admin/admin-ajax.php?action=store_search&lat=43.65323&lng=-79.38318&max_results=200&search_radius=2000"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        street_address = f"{j.get('address')} {j.get('address2') or ''}".strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        country = j.get("country") or ""
        if "Canada" in country:
            country_code = "CA"
        else:
            country_code = "US"

        page_url = j.get("url")
        location_name = j.get("store")
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")

        source = j.get("hours") or "<html></html>"
        tree = html.fromstring(source)
        text = tree.xpath("//text()")
        text = list(
            filter(
                None,
                [
                    t.replace("CLOSED", "TEMPORARILY CLOSED")
                    .replace("TEMPORARILY", "TEMPORARILY CLOSED")
                    .strip()
                    for t in text
                ],
            )
        )
        _tmp = []
        write = False
        for t in text:
            if "TAKE-OUT" in t:
                write = True
                continue
            if not write:
                continue
            if "DELIVERY" in t:
                break
            _tmp.append(t)

        hours_of_operation = ";".join(_tmp).replace("y;", "y ")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.mandarinrestaurant.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
