from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("geox")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.geox.com"
base_url = "https://www.geox.com/en-US/stores"


def fetch_data():
    with SgRequests() as session:
        countries = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "select#dwfrm_storelocator_country option"
        )
        for country in countries:
            url = f"https://www.geox.com/on/demandware.store/Sites-nausa-Site/en_US/Stores-FindStoresAjax?countryCode={country['value']}&page=storelocator&format=ajax"
            locations = session.get(url, headers=_headers).json()["stores"]
            if locations:
                logger.info(f"[{country['value']}] {len(locations)} found")
                for _ in locations:
                    page_url = f"https://www.geox.com/en-US/storedetails?StoreID={_['storeId']}&PC={country['value']}"
                    hours = []
                    temp = list(bs(_["storeHours"], "lxml").stripped_strings)
                    if temp:
                        for hh in temp:
                            if "Standard" in hh:
                                continue
                            if len(hh.split(",")) > 1:
                                continue
                            if "Extra" in hh:
                                break
                            hours.append(hh)
                    yield SgRecord(
                        page_url=page_url,
                        store_number=_["storeId"],
                        location_name=_["name"],
                        street_address=_["address"],
                        city=_["city"],
                        state=_["stateCode"],
                        zip_postal=_["postalCode"],
                        latitude=_["lat"],
                        longitude=_["long"],
                        country_code=_["countryCode"],
                        phone=_["phone"],
                        locator_domain=locator_domain,
                        hours_of_operation="; ".join(hours),
                    )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
