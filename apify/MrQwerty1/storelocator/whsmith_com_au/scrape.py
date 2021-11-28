from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    page_url = "https://whsmith.com.au/store-locator/"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//li[@data-show-marker]")
    for d in divs:
        _tmp = []
        hours = d.xpath(".//tr")
        for h in hours:
            day = "".join(h.xpath("./td[1]/text()")).strip()
            inter = "".join(h.xpath("./td[2]/text()")).strip()
            _tmp.append(f"{day}: {inter}")
        hours_of_operation = ";".join(_tmp)

        location_name = "".join(d.xpath(".//h3/text()")).strip()
        raw_address = "".join(d.xpath("./@data-address"))
        if "(" in raw_address and "temporarily" in raw_address:
            raw_address = raw_address.split("(")[0].strip()[:-1]
            hours_of_operation = "Temporarily Closed"
        if "(" in location_name and "temporarily" in location_name:
            location_name = location_name.split("(")[0].strip()
            hours_of_operation = "Temporarily Closed"
        street_address, city, state, postal = get_international(raw_address)
        latitude = "".join(d.xpath("./@data-latitude"))
        longitude = "".join(d.xpath("./@data-longitude"))
        store_number = "".join(d.xpath("./@data-id"))
        try:
            phone = d.xpath(".//a[contains(@href, 'tel:')]/text()")[0].strip()
        except IndexError:
            phone = SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="AU",
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://whsmith.com.au/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
