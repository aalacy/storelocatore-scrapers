from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
import dirtyjson as json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("adidas")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.adidas.com"
base_url = "https://placesws.adidas-group.com/API/search?brand=adidas&geoengine=google&method=get&category=store&latlng={}%2C{},5422&page=1&pagesize=10000&fields=name%2Cstreet1%2Cstreet2%2Caddressline%2Cbuildingname%2Cpostal_code%2Ccity%2Cstate%2Cstore_o+wner%2Ccountry%2Cstoretype%2Clongitude_google%2Clatitude_google%2Cstore_owner%2Cstate%2Cperformance%2Cbrand_store%2Cfactory_outlet%2Coriginals%2Cneo_label%2Cy3%2Cslvr%2Cchildren%2Cwoman%2Cfootwear%2Cfootball%2Cbasketball%2Coutdoor%2Cporsche_design%2Cmiadidas%2Cmiteam%2Cstella_mccartney%2Ceyewear%2Cmicoach%2Copening_ceremony%2Coperational_status%2Cfrom_date%2Cto_date%2Cdont_show_country&format=json&storetype=ownretail"
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
detail_url = "https://placesws.adidas-group.com/API/detail?brand=adidas&method=get&category=store&objectId={}&format=json"


def fetch_records(search):
    for lat, lng in search:
        with SgRequests() as session:
            locations = json.loads(
                session.get(base_url.format(lat, lng), headers=_headers).text.replace(
                    "\\2", "2"
                )
            )["wsResponse"]["result"]
            logger.info(f"{len(locations)} found")
            for _ in locations:
                if "opening_soon" in _.get("operational_status", "").lower():
                    continue
                hours = []

                zip_postal = _.get("postal_code")
                if zip_postal == "n/a":
                    zip_postal = ""
                state = _.get("state")
                if state and state.isdigit():
                    state = ""
                city = _["city"]
                if city and city.replace("-", "").isdigit():
                    city = ""
                page_url = f"https://www.adidas.com/us/storefinder#/storeID/{_['id']}/"
                logger.info(page_url)
                phone = ""
                try:
                    ss = session.get(
                        detail_url.format(_["id"]), headers=_headers
                    ).json()["wsResponse"]["result"][0]
                    phone = ss.get("phone")
                    if phone:
                        phone = phone.replace("&#43;", "+")
                    for day in days:
                        if ss.get(f"openinghours_{day}"):
                            hours.append(f'{day}: {ss.get(f"openinghours_{day}")}')
                except:
                    page_url = "https://www.adidas.com/us/storefinder#/"

                street_address = _.get("street1")
                if _.get("street2"):
                    street_address += " " + _.get("street2")
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["id"],
                    location_name=_["name"],
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    latitude=_.get("latitude_google"),
                    longitude=_.get("longitude_google"),
                    country_code=_["country"],
                    phone=phone,
                    locator_domain=locator_domain,
                    location_type=_["storetype"],
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=1000
        )
    ) as writer:
        search = DynamicGeoSearch(
            country_codes=SearchableCountries.ALL, expected_search_radius_miles=500
        )
        results = fetch_records(search)
        for rec in results:
            writer.write_row(rec)
