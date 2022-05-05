from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("liquordepot")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.liquordepot.ca/"
base_url = "https://www.liquordepot.ca/Our-Stores"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var storeList =")[1]
            .split("//]]")[0]
            .strip()
        )
        logger.info(f"{len(locations)} locations found")
        for _ in locations:
            street_address = _["AddressLine1"]
            if _["AddressLine2"]:
                street_address += " " + _["AddressLine2"]
            page_url = f"https://www.liquordepot.ca/Our-Stores/ctl/MobileStoreDetails/mid/440/storeID/{_['StoreID']}"
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in sp1.select("div.details .detail-row table table tr")
            ]
            yield SgRecord(
                page_url=page_url,
                store_number=_["StoreID"],
                location_name=_["Name"],
                street_address=street_address,
                city=_["City"],
                state=_["StateProvince"],
                zip_postal=_["ZipPostalCode"],
                latitude=_["Latitude"],
                longitude=_["Longitude"],
                country_code="CA",
                phone=_["Phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
