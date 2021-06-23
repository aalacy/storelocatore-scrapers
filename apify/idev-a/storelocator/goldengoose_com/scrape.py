from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("goldengoose")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.goldengoose.com"
    country_url = "https://www.goldengoose.com/on/demandware.store/Sites-ggdb-na-Site/en_US/Stores-FindStores?showMap=true"
    base_url = "https://www.goldengoose.com/on/demandware.store/Sites-ggdb-na-Site/en_US/Stores-FindStores?showMap=true&country={}&city="
    with SgRequests() as session:
        countries = session.get(country_url, headers=_headers).json()["countries"]
        for country in countries:
            locations = session.get(
                base_url.format(country["counryCode"]), headers=_headers
            ).json()["stores"]
            logger.info(f"[{country['counryCode']}] {len(locations)} found")
            for _ in locations:
                page_url = locator_domain + _["storeDetailsLink"]
                street_address = _["address1"]
                if _["address2"]:
                    street_address += " " + _["address2"]
                hours = []
                if _.get("storeHours"):
                    if "temporarily closed" in _["storeHours"].lower():
                        hours = ["Temporarily Closed"]
                    else:
                        if bs(_["storeHours"], "lxml").select_one(
                            "div.row > div.col-4"
                        ):
                            days = list(
                                bs(_["storeHours"], "lxml")
                                .select_one("div.row > div.col-4")
                                .stripped_strings
                            )
                            times = list(
                                bs(_["storeHours"], "lxml")
                                .select_one("div.row > div.col-6")
                                .stripped_strings
                            )
                            for x in range(len(days)):
                                hours.append(f"{days[x]}-{times[x]}")

                state = _.get("pickupProvince")
                city = _["city"]
                zip_postal = _["postalCode"]
                if (
                    city.lower() in street_address.lower()
                    or (state and state.lower() in street_address.lower())
                    or "korea" in street_address.lower()
                    or "virginia" in street_address.lower()
                ):
                    addr = parse_address_intl(street_address)
                    street_address = addr.street_address_1
                    if addr.street_address_2:
                        street_address += " " + addr.street_address_2
                    if addr.state:
                        state = addr.state
                    if addr.postcode:
                        zip_postal = addr.postcode
                if _["countryCode"] == "US":
                    zip_postal = zip_postal.split(" ")[-1]
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["ID"],
                    location_name=_["name"],
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code=_["countryCode"],
                    phone=_.get("phone"),
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours).replace("–", "-"),
                    raw_address=_["extendedAddress"],
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
