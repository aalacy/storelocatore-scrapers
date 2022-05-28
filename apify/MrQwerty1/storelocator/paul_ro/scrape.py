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
    api = "https://www.paul.ro/en/our-shops?ajax=1&all=1"
    r = session.get(api)
    tree = html.fromstring(r.content)
    divs = tree.xpath("//marker")

    for d in divs:
        location_name = "".join(d.xpath("./@name"))
        phone = "".join(d.xpath("./@phone"))
        raw_address = "".join(d.xpath("./@addressnohtml")).replace(phone, "").strip()
        street_address, city, state, postal = get_international(raw_address)
        latitude = "".join(d.xpath("./@lat"))
        longitude = "".join(d.xpath("./@lng"))
        store_number = "".join(d.xpath("./@id_store"))

        _tmp = []
        source = "".join(d.xpath("./@other"))
        root = html.fromstring(source)
        tr = root.xpath("//tr")
        for t in tr:
            day = "".join(t.xpath("./td[1]/text()")).strip()
            inter = "".join(t.xpath("./td[2]/text()")).strip()
            _tmp.append(f"{day} {inter}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="RO",
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
    locator_domain = "https://www.paul.ro/"
    page_url = "https://www.paul.ro/en/our-shops"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
