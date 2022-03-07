from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def fetch_data(sgw: SgWriter):
    api = "https://www.liquorexpress.ca/locations/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//div[@class='location-container']")
    for d in divs:
        location_name = "".join(d.xpath("./preceding-sibling::h3[1]/text()")).strip()
        slug = (
            location_name.replace("Liquor Express", "")
            .lower()
            .strip()
            .replace(" ", "-")
        )
        page_url = f"https://www.liquorexpress.ca/locations/{slug}/"

        line = "".join(
            d.xpath(
                ".//td[contains(text(), 'Location:')]/following-sibling::td[1]/text()"
            )
        ).strip()

        adr = parse_address(International_Parser(), line)
        street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
            "None", ""
        ).strip()

        city = adr.city
        state = adr.state
        postal = adr.postcode
        phone = (
            "".join(d.xpath(".//td[contains(text(), 'Ph:')]/text()"))
            .replace("Ph:", "")
            .strip()
        )
        if "F" in phone:
            phone = phone.split("F")[0].strip()
        text = "".join(d.xpath(".//iframe/@src"))
        latitude, longitude = get_coords_from_embed(text)
        hours_of_operation = "".join(
            d.xpath(".//td[contains(text(), 'Hours')]/following-sibling::td[1]/text()")
        ).strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="CA",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.liquorexpress.ca/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
