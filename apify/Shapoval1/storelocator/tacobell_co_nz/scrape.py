import json
import httpx
from lxml import html
from sgpostal.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import sglog

locator_domain = "https://www.tacobell.co.nz/"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)


def fetch_data(sgw: SgWriter):
    with SgRequests() as http:
        api_url = "https://www.tacobell.co.nz/locations"
        try:
            r = http.get(url=api_url)
            assert isinstance(r, httpx.Response)
            assert 200 == r.status_code
            tree = html.fromstring(r.text)
            div = tree.xpath('//div[@class="col sqs-col-3 span-3"]')
            for d in div:

                page_url = "https://www.tacobell.co.nz/locations"
                location_name = "".join(d.xpath(".//h2/text()"))
                if not location_name:
                    continue
                ad = (
                    " ".join(
                        d.xpath(
                            './/div[./p/strong[contains(text(), "Hours")]]/p[1]/text()'
                        )
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
                js_block = "".join(d.xpath(".//div/@data-block-json"))
                js = json.loads(js_block)
                b = js.get("location")
                latitude = b.get("mapLat")
                longitude = b.get("markerLng")
                hours_of_operation = (
                    " ".join(
                        d.xpath('.//p[./strong[contains(text(), "Hours")]]/text()')
                    )
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
        except Exception as e:
            log.info(f"Err at #L100: {e}")


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
