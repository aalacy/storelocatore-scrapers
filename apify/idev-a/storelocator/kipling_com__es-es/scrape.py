from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("kipling")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kipling.com"
base_url = "https://www.kipling.com/es-es/selectedstores/"


def _p(val):
    if (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.shop-container div.shop-address")
        for _ in locations:
            block = list(_.stripped_strings)
            phone = ""
            if _p(block[-1]):
                phone = block[-1]
                del block[-1]
            if "@" in block[-1]:
                del block[-1]
            raw_address = " ".join(block[1:])
            addr = parse_address_intl(raw_address)
            location_name = "Kipling"
            if "outlet" in _.strong.text.lower():
                location_name = "Kipling Outlet"

            city = addr.city
            if "Kildare" in raw_address:
                city = "Kildare"
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=block[1:][0],
                city=city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=_.find_previous_sibling("h3").text,
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
