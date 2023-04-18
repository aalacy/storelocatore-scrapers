from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("olivegarden")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.olivegarden.com/international"
base_url = "https://www.olivegarden.com/international"

ca_provinces_codes = {
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NS",
    "NT",
    "NU",
    "ON",
    "PE",
    "QC",
    "SK",
    "YT",
}


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
        locations = soup.select("main ul li")
        for _ in locations:
            if _.ul:
                continue
            block = list(_.stripped_strings)
            phone = ""
            if "Tel" in block[-1]:
                phone = block[-1].split(":")[-1].replace("Tel", "").strip()
                del block[-1]
            if "T:" in block[-1]:
                phone = block[-1].split("T:")[-1].split("F:")[0].strip()
                del block[-1]
            elif _p(block[-1]):
                phone = _p(block[-1])
                del block[-1]
            raw_address = " ".join(block[1:]).replace("\n", " ")
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            zip_postal = addr.postcode
            if zip_postal and "PR " in zip_postal:
                zip_postal = zip_postal.split()[-1]
                country = "PR"
            country = addr.country
            if addr.state in ca_provinces_codes:
                country = "CA"
            if not country:
                for cc in _.find_parent().find_previous_siblings():
                    if cc.name != "p":
                        country = cc.text.strip()
                        break
            yield SgRecord(
                page_url=base_url,
                location_name=block[0],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=zip_postal,
                country_code=country,
                phone=phone,
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
