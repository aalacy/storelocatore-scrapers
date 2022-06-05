from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.makro.be"
base_url = "https://www.makro.be//sxa/search/results/?itemid={6F251418-3DCC-4C8F-B875-470A576A84C7}&sig=store-locator&g=%7C&o=StoreName%2CAscending&p=20&v=%7BA0897F25-35F9-47F8-A28F-94814E5A0A78%7D"
detail_url = "https://www.makro.be//sxa/geoVariants/%7B657ADFBA-E18F-49E6-90F9-AA9BB0A8AE4A%7D/{}/0,0/undefined"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["Results"]
        for loc in locations:
            logger.info(loc["Id"])
            new_loc = session.get(detail_url.format(loc["Id"]), headers=_headers).json()
            _ = bs(new_loc["Html"], "lxml")
            raw_address = _.select_one("div.sl-address").text.strip()
            addr = raw_address.split(",")
            if addr[-1].strip() == "België":
                del addr[-1]
            hours = []
            temp = list(_.select_one("div.sl-opening-hours").stripped_strings)
            for x in range(0, len(temp), 2):
                hours.append(f"{temp[x]}: {temp[x+1]}")
            yield SgRecord(
                page_url=locator_domain + _.a["href"],
                store_number=loc["Id"],
                location_name=_.select_one("div.sl-store-name").text.strip(),
                street_address=", ".join(addr[:-2]),
                city=addr[-2],
                zip_postal=addr[-1].strip().split()[0],
                latitude=loc["Geospatial"]["Latitude"],
                longitude=loc["Geospatial"]["Longitude"],
                country_code="Belgium",
                locator_domain=locator_domain,
                raw_address=raw_address,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
