from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from sgpostal.sgpostal import parse_address_intl
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

LIMIT_CNT = 30

locator_domain = "https://www.regatta.com/"
base_url = "https://backend-regatta-uk.basecamp-pwa-prod.com/api/ext/store-locations/search?lat1={}&lng1={}&lat2={}&lng2={}"
us_url = "https://backend-regatta-us.basecamp-pwa-prod.com/api/ext/store-locations/search?lat1=52.536273191622705&lng1=-122.47558631250001&lat2=17.727758845003045&lng2=-68.95019568750001"

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fetch_data(lat1, lat2, lng1, lng2):
    lat = (lat1 + lat2) / 2
    lng = (lng1 + lng2) / 2
    formatted_url = base_url.format(lat1, lng1, lat2, lng2)
    stores = list(fetch_stores(formatted_url))
    logger.info(f"{len(stores)} {lat1, lng1, lat2, lng2} found")
    if len(stores) >= LIMIT_CNT:
        top_left = fetch_data(lat1, lat, lng1, lng)
        top_right = fetch_data(lat, lat2, lng1, lng)
        bottom_left = fetch_data(lat1, lat, lng, lng2)
        bottom_right = fetch_data(lat, lat2, lng, lng2)

        return stores + bottom_left + bottom_right + top_left + top_right

    return stores


def fetch_us():
    return list(fetch_stores(us_url))


ie_list = [
    "Killarney",
    "Limerick",
    "Cork",
    "Ennis",
    "Carlow",
    "Dingle",
    "Offaly",
    "Blessingto",
    "Belfast",
    "Ballina",
    "Dublin",
    "Co.Westmea",
]


def fetch_stores(url):
    with SgRequests() as session:
        locations = session.get(url, headers=_headers).json()["result"]["hits"]["hits"]
        for loc in locations:
            _ = loc["_source"]
            if "Coming Soon" in _["telephone"]:
                continue
            _street_address = _["street"]
            if _["street_line_2"]:
                _street_address += ", " + _["street_line_2"]

            hours = []
            if _.get("opening_hours", {}):
                hh = json.loads(_["opening_hours"])
                for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
                    day = day.lower()
                    start = hh.get(f"{day}_from")
                    end = hh.get(f"{day}_to")
                    hours.append(f"{day}: {start} - {end}")

            country_code = _["country"]
            if country_code == "GB":
                country_code = "United Kingdom"
            zip_postal = _["postcode"]

            if _["city"] in ie_list or _["region"] in ie_list:
                country_code = "Ireland"

            if zip_postal in ie_list:
                zip_postal = ""
                country_code = "Ireland"

            raw_address = f"{_street_address}, {_['city']}, {_['region']}, {_['postcode']}, {country_code}".replace(
                "?", ""
            )

            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            city = _["city"].split(",")[0]
            if city and street_address:
                _city = city[0].upper() + city.lower()[1:]
                if (
                    _city in street_address
                    and _city != "Peterborough"
                    and _city != "Oundle"
                    and _city != "Coventry"
                    and _city != "Lakeside"
                    and _city != "Chatham"
                    and _city != "Woldingham"
                ):
                    street_address = street_address.split(_city)[0]

            if street_address:
                street_address = (
                    street_address.replace("Regatta Outlet Store", "")
                    .replace("Affinity Sterling Mills Outlet", "")
                    .replace("Lawrence Way Regatta Outlet", "")
                )
                if street_address.replace("-", "").strip().isdigit():
                    street_address = _street_address

            phone = _["telephone"]

            if phone and (
                phone.lower() == "tbc" or phone.lower() == "tba" or phone == "0"
            ):
                phone = ""

            if country_code == "US":
                zip_postal = zip_postal.split()[-1]
            yield SgRecord(
                page_url="https://www.regatta.com/us/store-locator/",
                store_number=_["store_id"],
                location_name=_["name"],
                street_address=street_address,
                city=city,
                state=addr.state,
                zip_postal=zip_postal,
                latitude=_["location"]["lat"],
                longitude=_["location"]["lon"],
                country_code=country_code,
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.GeoSpatialId,
            duplicate_streak_failure_factor=5000,
        )
    ) as writer:
        results = fetch_data(90.0, -90.0, -180.0, 180.0)
        for rec in results:
            writer.write_row(rec)

        results = fetch_us()
        for rec in results:
            writer.write_row(rec)
