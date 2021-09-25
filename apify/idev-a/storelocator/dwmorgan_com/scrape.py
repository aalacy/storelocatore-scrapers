from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("dwmorgan")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.dwmorgan.com"
base_url = "https://www.dwmorgan.com/contacts-and-global-locations/"


def _p(val):
    return (
        val.replace("(", "")
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
        links = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var gmpAllMapsInfo=")[1]
            .split("//]]>")[0]
            .strip()[:-1]
        )[0]["markers"]
        logger.info(f"{len(links)} found")
        for _ in links:
            desc = list(bs(_["description"], "lxml").stripped_strings)
            if not "".join(desc):
                continue
            phone = ""
            if _p(desc[-1]):
                phone = desc[-1]
                del desc[-1]
            if "Region" in desc[0]:
                del desc[0]
            addr = parse_address_intl(" ".join(desc))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["title"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=addr.country,
                locator_domain=locator_domain,
                phone=phone,
                latitude=_["coord_x"],
                longitude=_["coord_y"],
                raw_address=" ".join(desc),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
