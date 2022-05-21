from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line, post):
    adr = parse_address(International_Parser(), line, postcode=post)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    api = "https://www.williamwilson.co.uk/page/storefinder.axd?region="
    r = session.get(api)
    tree = html.fromstring(r.content)

    divs = tree.xpath("//marker")
    for d in divs:
        location_name = "".join(d.xpath("./@name"))
        raw_address = "".join(d.xpath("./@address"))
        store_number = "".join(d.xpath("./@branch"))
        postal = "".join(d.xpath("./branchdetails/@postcode"))
        street_address, city, state, postal = get_international(raw_address, postal)
        phone = "".join(d.xpath("./@phone"))
        latitude = "".join(d.xpath("./@lat"))
        latitude = latitude.split("e")[0]
        longitude = "".join(d.xpath("./@lng"))
        longitude = longitude.split("e")[0]
        hours_of_operation = "".join(d.xpath("./@openingHours")).replace(">", "-")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="GB",
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
    locator_domain = "https://www.williamwilson.co.uk/"
    page_url = "https://www.williamwilson.co.uk/page/branch-locations"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
