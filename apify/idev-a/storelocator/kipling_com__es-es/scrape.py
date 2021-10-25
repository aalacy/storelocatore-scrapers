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
            if _.find_previous_sibling("h3").text != "España":
                continue
            block = list(_.stripped_strings)
            phone = ""
            if _p(block[-1]):
                phone = block[-1]
                del block[-1]
            if "@" in block[-1]:
                del block[-1]
            raw_address = " ".join(block[1:])
            addr = parse_address_intl(raw_address + ", Spain")
            yield SgRecord(
                page_url=base_url,
                location_name=block[0],
                street_address=block[1:][0],
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Spain",
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
