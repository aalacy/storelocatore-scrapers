from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import sglog
from sgpostal.sgpostal import USA_Best_Parser, parse_address

DOMAIN = "pizzerialimone.com"
BASE_URL = "https://www.pizzerialimone.com/"
LOCATION_URL = "https://www.pizzerialimone.com/locations"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def fetch_data(sgw: SgWriter):
    r = session.get(LOCATION_URL, headers=HEADERS)
    tree = html.fromstring(r.text)
    div = tree.xpath('//h2[not(text()="HOURS")]')
    for d in div:
        location_name = "".join(d.xpath(".//text()"))
        ad = (
            " ".join(d.xpath(".//following-sibling::p[1]/text()"))
            .replace("\n", "")
            .strip()
        )
        a = parse_address(USA_Best_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/preceding::h2[text()="HOURS"][1]/following-sibling::p/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )

        row = SgRecord(
            locator_domain=DOMAIN,
            page_url=LOCATION_URL,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )
        log.info("Append {} => {}".format(location_name, street_address))
        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
