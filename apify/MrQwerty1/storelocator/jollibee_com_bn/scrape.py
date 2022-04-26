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
    api = "https://www.jollibee.com.bn/assets/jollibee-theme/js/gmap.js"
    r = session.get(api)
    text = r.text.split("=[")[1].split("],")[0].split("},{")

    for t in text:
        latitude = t.split("lat:")[1].split(",")[0]
        longitude = t.split("lng:")[1].split("}")[0]
        source = t.split("content:")[-1]
        d = html.fromstring(source)
        location_name = "".join(d.xpath(".//header/text()")).strip()
        raw_address = "".join(d.xpath("//address/text()")).strip()
        street_address, city, state, postal = get_international(raw_address)
        phone = "".join(d.xpath("//div[@class='phoneNumber']//text()")).strip()
        location_type = "Branch"
        if t.split("iconImage:")[1].split(",")[0] == "s":
            location_type = "Drive-Thru"
        hours_of_operation = ";".join(
            d.xpath("//div[@class='openHour']//text()")
        ).strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="BN",
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.jollibee.com.bn/"
    page_url = "https://www.jollibee.com.bn/branches/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
