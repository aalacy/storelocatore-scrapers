from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def get_postal(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    _tmp = []
    text = tree.xpath("//p[contains(text(), 'Telefon')]/preceding-sibling::h3/text()")[
        -1
    ].strip()
    for t in text:
        if t.isdigit():
            _tmp.append(t)

    return "".join(_tmp)


def fetch_data(sgw: SgWriter):
    api = "https://www.okq8.se/-/Station/GetGlobalMapStations?appDataSource=9d780912-2801-4457-9376-16c48d02e688"
    r = session.get(api, headers=headers)
    js = r.json()["stations"]

    for j in js:
        location_name = j.get("name")
        slug = j.get("url")
        page_url = f"https://www.okq8.se{slug}"
        street_address = j.get("address") or ""
        if street_address.strip() == ".":
            street_address = SgRecord.MISSING

        try:
            postal = get_postal(page_url)
        except:
            postal = SgRecord.MISSING
        city = j.get("city")
        phone = j.get("phone")

        p = j.get("position") or {}
        latitude = p.get("lat") or ""
        longitude = p.get("lng") or ""
        if str(latitude) == "0":
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
        store_number = j.get("stationNumber") or ""
        if store_number == "0":
            store_number = SgRecord.MISSING

        _tmp = []
        hours = j.get("openingHours") or {}
        if hours.get("AlwaysOpen"):
            _tmp.append("24/7")
        elif hours:
            hours.pop("AlwaysOpen")
            for day, v in hours.items():
                inter = v.get("scheduleString")
                _tmp.append(f"{day}: {inter}")
        hours_of_operation = ";".join(_tmp)

        if not j.get("isOpen"):
            hours_of_operation = "Closed"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="SE",
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.okq8.se/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)
