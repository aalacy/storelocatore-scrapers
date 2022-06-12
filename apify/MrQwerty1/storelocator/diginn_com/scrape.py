import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    coords = dict()
    page_url = "https://www.diginn.com/locations"

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var locations = ')]/text()"))
    text = text.split("var locations = ")[1].split(";")[0]
    js = json.loads(text)

    for j in js:
        lat = j.get("latitude")
        lng = j.get("longitude")
        adr = j.get("street_address")
        key = " ".join(adr.split()[:2])
        coords[key] = (lat, lng)

    divs = tree.xpath("//div[contains(@class, 'flex flex-col justify-between ')]")
    for d in divs:
        location_name = "".join(d.xpath(".//div[@class='space-y-1']/div[1]/text()"))
        if not location_name:
            continue
        line = d.xpath(".//div[@class='space-y-1']/p/text()")
        line = list(filter(None, [l.strip() for l in line]))

        phone = SgRecord.MISSING
        if line[-1][0].isdigit():
            phone = line.pop()

        street_address = line.pop(0)
        if "(" in street_address:
            street_address = street_address.split("(")[0].strip()
        line = line.pop()
        postal = line.split()[-1]
        state = line.split()[-2]
        city = line.replace(postal, "").replace(state, "").replace(",", "").strip()

        key = " ".join(street_address.split()[:2])
        latitude, longitude = coords.get(key) or (SgRecord.MISSING, SgRecord.MISSING)

        hours_of_operation = "".join(
            d.xpath(".//div[@class='space-y-1']/div[./p]//text()")
        ).replace("â", "-")
        if "(" in hours_of_operation:
            hours_of_operation = hours_of_operation.split("(")[0].strip()
        if "Coming" in location_name:
            hours_of_operation = "Coming Soon"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.diginn.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
