from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("goldengoose")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _ss(val):
    if not val:
        return ""
    return (
        val.replace("FLAGSHIP STORE", "")
        .replace("THE DOMAIN", "")
        .replace("BOSTON COPLEY PLACE", "")
        .strip()
    )


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
                street_address = _["address1"] or ""
                if not _ss(street_address):
                    street_address = ""
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
                raw_address = _ss(_["extendedAddress"])
                if "Korea" in raw_address and "South Korea" not in raw_address:
                    raw_address = raw_address.replace("Korea", "South Korea")
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                if addr.state:
                    state = addr.state
                if addr.postcode:
                    zip_postal = addr.postcode
                if _["countryCode"] == "US":
                    zip_postal = zip_postal.split(" ")[-1]
                if city:
                    if state:
                        city = city.replace(state, "")
                    city = (
                        city.replace("P.R.", "")
                        .replace("GYEONGGI-DO", "")
                        .replace("CHUNGCHEONGBUK-DO", "")
                        .strip()
                    )
                street_address = (
                    street_address.replace("Korea", "").replace("Ulsan", "").strip()
                )
                if "3F" == street_address:
                    street_address = raw_address.split(",")[0].strip()
                if "Cheonan-Si" in street_address:
                    street_address = street_address.replace("Cheonan-Si", "")
                    city = "Cheonan-Si"
                if "Cheongju-Si" in street_address:
                    street_address = street_address.replace("Cheongju-Si", "")
                    city = "Cheongju-Si"
                if "Hanam-Si" in street_address:
                    street_address = street_address.replace("Hanam-Si", "")
                    city = "Hanam-Si"
                if "Suwon-Si" in street_address:
                    street_address = street_address.replace("Suwon-Si", "")
                    city = "Suwon-Si"
                if "Incheon" in street_address:
                    street_address = street_address.replace("Incheon", "")
                    city = "Incheon"
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
                    raw_address=raw_address,
                    hours_of_operation="; ".join(hours).replace("–", "-"),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
