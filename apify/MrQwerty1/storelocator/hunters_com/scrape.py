from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street = f"{adr.street_address_1} {adr.street_address_2}".replace(
        "None", ""
    ).strip()
    city = adr.city
    state = adr.state
    postal = adr.postcode

    return street, city, state, postal


def get_additional(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    raw_address = "".join(
        tree.xpath("//h3[@class='heading--four']/following-sibling::p[1]/text()")
    )
    raw_address = " ".join(raw_address.split())
    text = "".join(tree.xpath("//iframe/@src"))
    try:
        lat, lng = text.split("q=")[1].split("&")[0].split(",")
    except:
        lat, lng = SgRecord.MISSING, SgRecord.MISSING

    return raw_address, lat, lng


def fetch_data(sgw: SgWriter):
    api = "https://www.hunters.com/api/offices"
    r = session.get(api)
    js = r.json()["results"].values()

    for s in js:
        for j in s:
            location_name = j.get("name")
            page_url = j.get("url")
            raw_address, latitude, longitude = get_additional(page_url)
            street_address, city, state, postal = get_international(raw_address)
            if len(street_address) < 5:
                street_address = raw_address.split(",")[0].strip()
            if "@" in street_address:
                street_address = street_address.split("@")[-1].strip()
            phone = j.get("sales_phone") or j.get("lettings_phone")
            store_number = j.get("id")
            hours = j.get("opening_times") or ""
            hours_of_operation = " ".join(hours.split())

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="GB",
                store_number=store_number,
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.hunters.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
