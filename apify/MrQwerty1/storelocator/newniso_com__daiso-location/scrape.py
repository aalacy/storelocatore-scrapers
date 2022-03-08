from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
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


def get_coords():
    coords = dict()
    r = session.get(
        "https://www.google.com/maps/d/u/0/kml?mid=1BwAsLCDYun8RucTFY2YrZw3hmCk&forcekml=1",
    )
    source = r.text.replace("<![CDATA[", "").replace("]]>", "")
    tree = html.fromstring(source.encode())
    markers = tree.xpath("//placemark")
    for m in markers:
        key = " ".join("".join(m.xpath("./name/text()")).split()[:2]).lower()
        value = "".join(m.xpath(".//coordinates/text()")).replace(",0", "").split(",")
        coords[key] = value

    return coords


def fetch_data(sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    coords = get_coords()

    divs = tree.xpath("//div[@class='tb-toggle']")
    for d in divs:
        location_name = "".join(d.xpath(".//a/text()")).strip()
        key = " ".join(location_name.split()[:2]).lower()
        latitude, longitude = coords.get(key) or (SgRecord.MISSING, SgRecord.MISSING)
        raw_address = " ".join("".join(d.xpath(".//p[1]/text()")).split())
        street_address, city, state, postal = get_international(raw_address)

        phone = " ".join("".join(d.xpath(".//p[3]/text()")).split())
        phone = phone.split("Tel/Fax:")[-1].strip()
        phone = phone.split("Tel:")[-1].split("Fax:")[0].strip()
        hours_of_operation = " ".join("".join(d.xpath(".//p[2]/text()")).split())

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="MY",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "http://newniso.com/"
    page_url = "http://newniso.com/daiso-location/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
