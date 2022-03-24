from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://flippinpizza.com/wp-content/uploads/ssf-wp-uploads/ssf-data.json"
    r = session.get(api, headers=headers)
    js = r.json()["item"]

    for j in js:
        text = j.get("description") or "<html></html>"
        tree = html.fromstring(text)
        location_name = j.get("location")
        raw_address = j.get("address") or ""
        line = raw_address.split("  ")
        state, postal = line.pop().split()
        city = line.pop().replace(",", "")
        street_address = ", ".join(line)
        store_number = j.get("storeId")
        page_url = "".join(tree.xpath("//div[@class='location-btn']/a/@href"))
        phone = j.get("telephone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            phone=phone,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://flippinpizza.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
