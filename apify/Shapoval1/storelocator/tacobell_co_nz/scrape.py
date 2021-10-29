import json
from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.tacobell.co.nz/"
    api_url = "https://www.tacobell.co.nz/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="col sqs-col-4 span-4"]')
    for d in div:

        page_url = "https://www.tacobell.co.nz/locations"
        location_name = "".join(d.xpath(".//h2/text()"))
        if not location_name:
            continue
        ad = (
            " ".join(
                d.xpath('.//div[./p/strong[contains(text(), "Hours")]]/p[1]/text()')
            )
            .replace("\n", "")
            .strip()
        )

        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        city = a.city or "<MISSING>"
        country_code = "New Zealand"
        jsblock = "".join(d.xpath(".//div/@data-block-json"))
        js = json.loads(jsblock)
        b = js.get("location")
        latitude = b.get("mapLat")
        longitude = b.get("markerLng")
        hours_of_operation = (
            " ".join(d.xpath('.//p[./strong[contains(text(), "Hours")]]/text()'))
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("Sunday-Thursday CLOSED") != -1:
            hours_of_operation = (
                hours_of_operation
                + " "
                + " ".join(
                    d.xpath(
                        './/p[./strong[contains(text(), "Hours")]]/following-sibling::p/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )

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
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
