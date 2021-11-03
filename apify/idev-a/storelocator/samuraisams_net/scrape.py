from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("samuraisams")


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.samuraisams.net"
base_url = "https://locator.kahalamgmt.com/locator/index.php?brand=6&mode=map&latitude=37.09024&longitude=-95.712891&q=&pagesize=0"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).text.split(
            "Locator.stores["
        )
        for loc in locations[1:]:
            _ = json.loads(
                loc.split("Locator.storeIndexes[")[0].split("] =")[1].strip()
            )
            page_url = f"https://www.samuraisams.net/stores/{_['StoreId']}"
            logger.info(page_url)
            hours = [
                hh.text.strip()
                for hh in bs(
                    session.get(page_url, headers=_headers).text, "lxml"
                ).select(".row.details > div > ul li")
            ]
            yield SgRecord(
                page_url=page_url,
                store_number=_["StoreId"],
                location_name=_["Name"],
                street_address=_["Address"].replace(",", ""),
                city=_["City"],
                state=_["State"],
                zip_postal=_["Zip"],
                latitude=_["Latitude"],
                longitude=_["Longitude"],
                country_code=_["CountryCode"],
                phone=_["Phone"],
                location_type=_["LocationType"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
