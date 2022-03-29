from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://limefreshmexicangrill.com/wp-admin/admin-ajax.php?action=store_search&lat=26.3693717&lng=-80.2025238&max_results=25&search_radius=50&autoload=1"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Proxy-Authorization": "Basic YWNjZXNzX3Rva2VuOmc3NzExNnBzajZqbGZhaHM5dHJwMDdocm0ydTlxNGVzM3BhaGNrYm9oY2kzOGEzMWtpdQ==",
        "Connection": "keep-alive",
        "Referer": "https://limefreshmexicangrill.com/locations/",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }

    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:

        street_address = "".join(j.get("address"))
        phone = "".join(j.get("phone"))
        country_code = "".join(j.get("country"))
        location_name = "".join(j.get("store")).replace(" &#8211;", "–").strip()
        latitude = "".join(j.get("lat"))
        longitude = "".join(j.get("lng"))
        page_url = "https://limefreshmexicangrill.com/locations/"
        hours = "".join(j.get("description"))
        a = html.fromstring(hours)
        hours_of_operation = (
            " ".join(a.xpath('//*[contains(text(), "AM")]/text()')).replace("\r\n", "")
            or "<MISSING>"
        )
        state = "<MISSING>"
        links = a.xpath("//a/@href")
        for i in links:
            if "-fl-" in i:
                state = "FL"
        if "FL" in hours:
            state = "FL"
        perm_cls = "".join(
            a.xpath('//*[contains(text(), "permanently closed")]//text()')
        )
        if perm_cls:
            hours_of_operation = "Permanently closed"
        if location_name.find("Orlando") != -1:
            line = j.get("description")
            b = html.fromstring(line)
            hours_of_operation = " ".join(b.xpath("//p[2]//text()"))
        postal = j.get("zip") or "<MISSING>"
        city = location_name
        if city.find("–") != -1:
            city = city.split("–")[1].strip()
        if city.find(":") != -1:
            city = city.split(":")[0].strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://limefreshmexicangrill.com"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
