from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import re
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("dunkin")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://dunkin.pe"
base_url = "https://dunkin.pe/locales"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = json.loads(
            soup.find("script", string=re.compile(r"window\.__NUXT__")).string.replace(
                "window.__NUXT__=", ""
            )[:-1]
        )["state"]["locales"]["stores"]
        logger.info(f"{len(links)} found")
        for _ in links:
            addr = parse_address_intl(_["address"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours_of_operation = "; ".join(
                bs(_["description"], "lxml").stripped_strings
            )
            if hours_of_operation:
                hours_of_operation = hours_of_operation.split(":")[-1].strip()
            yield SgRecord(
                page_url=base_url,
                store_number=_["storelocator_id"],
                location_name=_["name"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Peru",
                phone=_["phone"],
                locator_domain=locator_domain,
                latitude=_.get("latitude"),
                longitude=_.get("longtitude"),
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.ZIP,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
