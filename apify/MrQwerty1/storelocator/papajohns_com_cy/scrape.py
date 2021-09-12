import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city
    state = adr.state or ""
    postal = adr.postcode

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    page_url = "https://www.papajohns.com.cy/store-locations/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[@class='wpb_column vc_column_container vc_col-sm-4' and .//h4]"
    )

    for d in divs:
        location_name = "".join(d.xpath(".//h4/text()")).strip()
        line = d.xpath(".//div[contains(@class,'title-after_title')]/text()")
        line = list(filter(None, [l.strip() for l in line]))
        phone = line.pop(0)
        raw_address = " ".join(line)
        street_address, city, state, postal = get_international(raw_address)
        city = location_name.split("-")[-1].strip()

        text = "".join(d.xpath(".//div[@data-map-args]/@data-map-args"))
        j = json.loads(text)
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = ";".join(
            d.xpath(".//p[./strong[contains(text(), 'Working')]]/text()")
        ).strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="CY",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.papajohns.com.cy/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
