from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://milkbarstore.com"
    api_url = "https://milkbarstore.com/pages/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[contains(@class, "location-standard location")] | //div[@class="flagship-info large--width-50 large--padding-left-3"] | //div[@class="location-standard"] | //div[@class="flagship-info large--width-50"]'
    )
    for d in div:

        page_url = "https://milkbarstore.com/pages/locations"
        location_name = "".join(d.xpath('.//h4[@class="h3"]/text()')) or "<MISSING>"
        if location_name == "<MISSING>":
            location_name = "".join(d.xpath('.//h4[@class="h2"]/text()'))
        ad = (
            " ".join(d.xpath('.//b[text()="Hours:"]//preceding-sibling::p/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if ad == "<MISSING>":
            ad = (
                " ".join(
                    d.xpath(
                        './/div[@class="padding-top-1 large--padding-top-2 width-100"]/p/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        ad = ad.replace("(Men's Store)", "").strip()
        if ad.find("*") != -1:
            ad = ad.split("*")[0].strip()

        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "CA"
        if postal.isdigit():
            country_code = "US"
        city = a.city or "<MISSING>"
        if street_address.find("382 Metropolitan Ave") != -1:
            city = "New York"
        phone = (
            "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(d.xpath('.//b[text()="Hours:"]//following-sibling::p/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation.find("temporarily closed") != -1:
            hours_of_operation = "Temporarily Closed"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
