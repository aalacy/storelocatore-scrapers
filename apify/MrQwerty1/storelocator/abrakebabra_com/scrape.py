import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address, International_Parser


def get_street(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()

    return street


def fetch_data(sgw: SgWriter):
    coords = dict()
    page_url = "https://www.abrakebabra.com/locations/"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    blocks = tree.xpath("//div[@data-x-params]/@data-x-params")
    for b in blocks:
        j = json.loads(b)
        key = str(j.get("markerInfo")).lower()
        lat = j.get("lat")
        lng = j.get("lng")
        coords[key] = (lat, lng)

    divs = tree.xpath("//div[contains(@class, 'x-col') and .//ul]")
    for d in divs:
        location_name = "".join(d.xpath(".//h1/text()")).strip()
        key = location_name.lower()
        raw_address = " ".join("".join(d.xpath(".//div/text()")).split())
        line = raw_address.split(", ")
        pp = line.pop()
        postal = SgRecord.MISSING
        for p in pp:
            if p.isdigit() and "Dublin" not in pp:
                postal = pp
                break

        if postal == SgRecord.MISSING:
            city = pp
        else:
            city = line.pop()

        city = city.replace("Co.", "").strip()
        if "Dublin" in city:
            city = city.split()[0]
        if "Ireland" in city:
            city = line.pop()

        street_address = get_street(raw_address)
        country_code = "IE"
        phone = "".join(d.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()
        try:
            latitude, longitude = coords.get(key) or (
                SgRecord.MISSING,
                SgRecord.MISSING,
            )
        except KeyError:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.abrakebabra.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
