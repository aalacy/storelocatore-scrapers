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
    page_url = "https://corp.amway.com.hk/en/our-locations"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//div[@class='infoListItem infoListItem__wImg']")
    for d in divs:
        store_number = "".join(d.xpath("./@data-location"))
        country_code = "HK"
        if store_number == "mo":
            country_code = "MO"
        location_name = "".join(d.xpath(".//span[@class='title']/text()")).strip()
        raw_address = "".join(
            d.xpath(
                ".//div[contains(text(), 'Address')]/following-sibling::div[1]//text()"
            )
        ).strip()
        phone = "".join(
            d.xpath(".//div[contains(text(), 'Tel')]/following-sibling::div[1]//text()")
        ).strip()
        street_address, city, state, postal = get_international(raw_address)
        hours_of_operation = "".join(
            d.xpath(
                ".//div[contains(text(), 'Hours')]/following-sibling::div[1]/text()"
            )
        ).strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://corp.amway.com.hk/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
