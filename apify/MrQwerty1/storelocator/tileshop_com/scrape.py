from lxml import html, etree
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hoo(url):
    _tmp = []
    r = session.get(url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='day-row']")
    for d in divs:
        day = "".join(d.xpath("./p[@class='day']/text()")).strip()
        inter = "".join(d.xpath("./p[@class='hours']/text()")).strip()
        _tmp.append(f"{day} {inter}")

    return ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    api = "https://www.tileshop.com/api/Stores/SearchByCoordinates?lat=44.98&lng=-93.45&distance=8000&take=5000"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        location_name = j.get("StoreName")
        street_address = (
            f"{j.get('AddressLine1')} {j.get('AddressLine2') or ''}".strip()
        )
        city = j.get("City") or "<MISSING>"
        state = j.get("StateCode") or "<MISSING>"
        postal = j.get("PostalCode") or "<MISSING>"
        country_code = "US"
        store_number = j.get("StoreNumber") or "<MISSING>"
        page_url = f'https://www.tileshop.com/store-locator/{j.get("Name")}'
        phone = j.get("Phone1") or "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"

        _tmp = []
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        for d in days:
            _tmp.append(f'{d}: {j.get(f"{d}Hours")}')

        hours_of_operation = ";".join(_tmp)

        if "None" in hours_of_operation:
            try:
                hours_of_operation = get_hoo(page_url)
            except etree.ParserError:
                hours_of_operation = SgRecord.MISSING

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
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.tileshop.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
