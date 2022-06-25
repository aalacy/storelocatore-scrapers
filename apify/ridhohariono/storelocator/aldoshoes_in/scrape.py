import re

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    post = "".join(regex.findall(line))
    adr = parse_address(International_Parser(), line, postcode=post)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, state, postal


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[contains(@id, 'item_store_')]")

    for d in divs:
        params = "".join(d.xpath("./@onclick")).replace("showcontent", "").strip()
        latitude, longitude, raw_address = eval(params)
        street_address, city, state, postal = get_international(raw_address)
        country_code = "IN"
        store_number = (
            "".join(d.xpath(".//span[@class='store-number']/text()"))
            .replace(".", "")
            .strip()
        )
        location_name = "".join(d.xpath(".//div[@class='store_title']/text()")).strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            store_number=store_number,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    regex = re.compile(r"\d{6}")
    locator_domain = "https://www.aldoshoes.in/"
    page_url = "https://www.aldoshoes.in/store-locator/aldo-store-locator.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
