from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("millersfresh")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.compactpowerrents.com/"
    base_url = "https://www.compactpowerrents.com/locations/?zip=all"
    with SgRequests() as session:
        links = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("Locations.init(")[1]
            .split("</script>")[0]
            .strip()[:-2]
        )
        logger.info(f"{len(links)} found")
        for _ in links:
            page_url = f"https://www.compactpowerrents.com/location/{_['StoreId']}/{_['City']}/{_['State']}/{_['Zip']}"
            yield SgRecord(
                page_url=page_url,
                store_number=_["StoreGeo"]["StoreId"],
                location_name=f"{_['City']}, {_['State']} {_['Zip']}",
                street_address=_["Address"],
                city=_["City"],
                state=_["State"],
                zip_postal=_["Zip"],
                country_code=_["Country"],
                location_type=_["HDStoreType"],
                phone=_["Phone"],
                locator_domain=locator_domain,
                latitude=_["StoreGeo"]["Lat"],
                longitude=_["StoreGeo"]["Lon"],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
