from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def get_coords():
    coords = dict()
    r = session.get(
        "https://www.google.com/maps/d/u/0/kml?mid=1fvLTSuvRyqH-ECF2C3szEmDWR_ZcCAmW&forcekml=1"
    )
    tree = html.fromstring(r.content)
    markers = tree.xpath("//placemark")
    for marker in markers:
        key = "".join(marker.xpath(".//name/text()")).strip().lower()
        lat, lng = "".join(marker.xpath(".//coordinates/text()")).strip().split(",")[:2]
        coords[key] = (lat, lng)

    return coords


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    coords = get_coords()
    divs = tree.xpath("//p[strong or count(text())=1 and not(contains(text(), 'p.'))]")

    for d in divs:
        location_name = "".join(d.xpath(".//text()")).strip()
        line = d.xpath("./following-sibling::p[1]/text()")
        line = list(filter(None, [li.strip() for li in line]))

        if line[-1][-1].isdigit():
            phone = line.pop()
        else:
            phone = "".join(d.xpath("./following-sibling::p[2]/text()")).strip()

        phone = (
            phone.lower().replace("puh", "").replace("p", "").replace(".", "").strip()
        )
        pc = line.pop()
        street_address = line.pop()
        postal = pc.split()[0]
        city = pc.replace(postal, "").strip()
        if "(" in city:
            city = city.split("(")[0].strip()

        country_code = "FI"
        location_type = (
            "".join(d.xpath("./preceding-sibling::h3[1]/text()")).strip()
            or "Veneasemat"
        )
        key = location_name.lower().replace("gulf", "").strip()
        longitude, latitude = coords.get(key) or (SgRecord.MISSING, SgRecord.MISSING)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            location_type=location_type,
            phone=phone,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.gulfoil.fi/"
    page_url = "https://www.gulfoil.fi/etusivu/huoltoasemat/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.LOCATION_TYPE})
        )
    ) as writer:
        fetch_data(writer)
