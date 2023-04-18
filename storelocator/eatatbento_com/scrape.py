from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl
from sgpostal.sgpostal import parse_address_intl

ssl._create_default_https_context = ssl._create_unverified_context

logger = SgLogSetup().get_logger("eatatbento")

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}

locator_domain = "https://www.eatatbento.com/"
base_url = "https://www.eatatbento.com/locations/"
json_url = "https://eatatbento.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxR0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABU0Wug"


def fetch_data():
    with SgRequests() as session:
        links = session.get(json_url, headers=_headers).json()["markers"]
        logger.info(f"{len(links)} found")
        for _ in links:
            page_url = _["link"]
            logger.info(page_url)
            soup1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            if (
                "coming soon"
                in soup1.find("h2", string=re.compile(r"Address"))
                .find_next_sibling()
                .text.lower()
                .strip()
            ):
                continue
            _hr = soup1.find("h2", string=re.compile(r"HOURS$", re.IGNORECASE))
            hours = []
            if _hr:
                temp = list(_hr.find_next_sibling().stripped_strings)
                if temp:
                    if "Soft" in temp[0]:
                        del temp[0]
                    for x in range(0, len(temp), 2):
                        hours.append(f"{temp[x]} {temp[x+1]}")

            phone = ""
            if soup1.find("a", href=re.compile(r"tel:")):
                phone = soup1.find("a", href=re.compile(r"tel:")).text
            addr = parse_address_intl(_["address"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["title"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
                latitude=_["lat"],
                longitude=_["lng"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
