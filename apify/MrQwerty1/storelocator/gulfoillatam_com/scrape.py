from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, state, postal


def fetch_data(sgw: SgWriter):
    api = "https://www.google.com/maps/d/u/0/kml?mid=1VUA9dHt9h2dD4K2myL35PSOU5_oCA50Q&forcekml=1"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.content)
    divs = tree.xpath("//placemark")

    for d in divs:
        location_name = "".join(d.xpath(".//name/text()")).strip()
        raw_address = (
            "".join(d.xpath(".//description/text()"))
            .replace("]", "")
            .replace(">", "")
            .strip()
        )
        street_address, city, state, postal = get_international(raw_address)
        latitude, longitude = "".join(d.xpath(".//coordinates/text()")).split(",")[:2]

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="AR",
            latitude=latitude,
            longitude=longitude,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "http://www.gulfoillatam.com/"
    page_url = "http://www.gulfoillatam.com/estaciones-de-servicio/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.LATITUDE}))) as writer:
        fetch_data(writer)
