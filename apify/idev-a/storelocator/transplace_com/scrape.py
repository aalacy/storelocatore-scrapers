from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("transplace")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.transplace.com"
base_url = "https://www.transplace.com/contact/find-an-office/"


def _p(val):
    return (
        val.split(":")[-1]
        .replace("Phone", "")
        .split("x")[0]
        .replace("(", "")
        .split("al")[0]
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("main div.find-at-office div.inner div.wrap > div.col")
        logger.info(f"{len(links)} found")
        for link in links:
            country = link.select_one("div.title-wrap").text.strip()
            locations = link.select("main div.item")
            for _ in locations:
                location_name = _.select_one("div.item-title").text.strip()
                for loc in _.select("p"):
                    block = list(loc.stripped_strings)
                    phone = ""
                    if _p(block[-1]):
                        phone = (
                            block[-1]
                            .split(":")[-1]
                            .replace("Phone", "")
                            .split("al")[0]
                            .split("x")[0]
                            .strip()
                        )
                        del block[-1]
                    if "phone" in block[-1].lower():
                        del block[-1]
                    raw_address = " ".join(block)
                    addr = parse_address_intl(raw_address)
                    street_address = addr.street_address_1
                    if addr.street_address_2:
                        street_address += " " + addr.street_address_2

                    country_code = addr.country
                    if not country_code:
                        country_code = country
                    yield SgRecord(
                        page_url=base_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=addr.city,
                        state=addr.state,
                        zip_postal=addr.postcode.replace("CP. ", "").replace("CP ", ""),
                        country_code=country_code,
                        phone=phone,
                        locator_domain=locator_domain,
                        raw_address=raw_address,
                    )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
