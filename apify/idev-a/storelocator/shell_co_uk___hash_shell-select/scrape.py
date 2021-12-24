from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from tenacity import retry, wait_fixed, stop_after_attempt

logger = SgLogSetup().get_logger("shell")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://shell.co.uk/#shell-select"
json_url = "https://shellgsllocator.geoapp.me/api/v1/locations/within_bounds?sw%5B%5D={}&sw%5B%5D={}&ne%5B%5D={}&ne%5B%5D={}&with_all%5Bamenities%5D%5B%5D=selectshop&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=50&driving_distances=false&format=json"
base_url = "https://shellgsllocator.geoapp.me/api/v1/locations/within_bounds?sw%5B%5D=-80&sw%5B%5D=-179&ne%5B%5D=80&ne%5B%5D=179&with_all%5Bamenities%5D%5B%5D=selectshop&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json"


@retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
def get_json(url):
    with SgRequests(proxy_country="us") as session:
        return session.get(url, headers=_headers).json()


def fetch_boundings(boundings, writer):
    for bound in boundings:
        _bb = bound["bounds"]
        locations = get_json(
            json_url.format(_bb["sw"][0], _bb["sw"][1], _bb["ne"][0], _bb["ne"][1])
        )
        if locations:
            if locations[0].get("centroid"):
                logger.info(f"{bound['size']} recuring")
                fetch_boundings(locations, writer)
            else:
                logger.info(f"{len(locations)} locations")
                for _ in locations:
                    street_address = ""
                    if _.get("address"):
                        street_address = _["address"]
                    if _.get("address1"):
                        street_address += " " + _["address1"]
                    if _.get("address2"):
                        street_address += " " + _["address2"]
                    zip_postal = _.get("postcode")
                    if zip_postal and zip_postal == "00000":
                        zip_postal = ""
                    writer.write_row(
                        SgRecord(
                            store_number=_["id"],
                            location_name=_["name"],
                            street_address=street_address,
                            city=_["city"],
                            state=_.get("state"),
                            zip_postal=zip_postal,
                            latitude=_["lat"],
                            longitude=_["lng"],
                            country_code=_["country"],
                            phone=_["telephone"],
                            locator_domain=locator_domain,
                            location_type=", ".join(_.get("channel_types", [])),
                        )
                    )
        else:
            break


def fetch_data(writer):
    boundings = get_json(base_url)

    fetch_boundings(boundings, writer)


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=2000
        )
    ) as writer:
        fetch_data(writer)
