from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://www.dunhamssports.com/on/demandware.store/Sites-dunhamssports-Site/en_US/Stores-FindStores?showMap=true&radius=3000&lat=41.7697&long=-87.6985"

    r = session.get(api, headers=headers)
    js = r.json()["stores"]

    for j in js:
        location_name = j.get("name")
        store_number = j.get("ID")
        page_url = f"https://www.dunhamssports.com/on/demandware.store/Sites-dunhamssports-Site/en_US/Stores-Detail?storeID={store_number}"

        street_address = f'{j.get("address1")} {j.get("address2") or ""}'.strip()
        city = j.get("city")
        state = j.get("stateCode")
        postal = j.get("postalCode")
        country_code = j.get("countryCode")
        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        _tmp = []
        source = j.get("storeHours") or "<html></html>"
        tree = html.fromstring(source)
        tr = tree.xpath("//tr")
        for t in tr:
            day = "".join(t.xpath("./td[1]//text()")).strip()
            time = "".join(t.xpath("./td[2]/text()")).strip()
            _tmp.append(f"{day}: {time}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
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
            location_type=SgRecord.MISSING,
            latitude=str(latitude),
            longitude=str(longitude),
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.dunhamssports.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
