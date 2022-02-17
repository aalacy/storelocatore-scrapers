from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import dirtyjson as json

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.pro-duo.de"
base_url = "https://www.pro-duo.de/on/demandware.store/Sites-ProDuo_Trade_DE-Site/de_DE/Stores-GetStoresJSON"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            page_url = f"https://www.pro-duo.de/storeinfo?StoreID={_['ID']}"
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in sp1.select("table.store-information_time_table tr")[1:]
            ]
            if "{" in " ".join(hours):
                temp = hours
                hours = []
                try:
                    for hh in json.loads(
                        temp[0].replace('""', '"').replace('}"}', "}")
                    )["periods"]:
                        hours.append(
                            f"{hh['openDay']}: {hh['openTime']} - {hh['closeTime']}"
                        )
                except:
                    import pdb

                    pdb.set_trace()

            yield SgRecord(
                page_url=page_url,
                store_number=_["ID"],
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                zip_postal=_["postalCode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="Germany",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["formattedAddress"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
