from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from sgpostal.sgpostal import parse_address_intl
from sglogging import SgLogSetup
import math

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

LIMIT_CNT = 50

locator_domain = "https://www.regatta.com/"
base_url = "https://backend-regatta-uk.basecamp-pwa-prod.com/api/ext/store-locations/search?lat1={}&lng1={}&lat2={}&lng2={}"

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

coords = (
    83.27040769609754,
    -48.940428988101154,
    -170.25434606624188,
    179.13901582952695,
)


def from_latlng_to_cartesian(lat, lng):
    lat = lat * math.pi / 180
    lng = lng * math.pi / 180
    x = math.cos(lat) * math.cos(lng)
    y = math.cos(lat) * math.sin(lng)
    z = math.sin(lat)
    return x, y, z


def calc_midpoint_from_catesians(cat1, cat2):
    x1, y1, z1 = cat1
    x2, y2, z2 = cat2
    x = (x1 + x2) / 2
    y = (y1 + y2) / 2
    z = (z1 + z2) / 2
    Lon = math.atan2(y, x)
    Hyp = math.sqrt(x * x + y * y)
    Lat = math.atan2(z, Hyp)

    lat = Lat * (180 / math.pi)
    lng = Lon * (180 / math.pi)

    return lat, lng


def calc_midpoint_from_bounding_box(bounding_box):
    lat1, lat2, lng1, lng2 = bounding_box

    cat1 = from_latlng_to_cartesian(lat1, lng1)
    cat2 = from_latlng_to_cartesian(lat2, lng2)
    return calc_midpoint_from_catesians(cat1, cat2)


def get_top_left_box(bounding_box):
    lat1, lat2, lng1, lng2 = bounding_box
    lat, lng = calc_midpoint_from_bounding_box(bounding_box)
    logger.info(
        f"get_top_left_box {lat1, lat2, lng1, lng2}",
    )
    return lat1, lat, lng1, lng


def get_top_right_box(bounding_box):
    lat1, lat2, lng1, lng2 = bounding_box
    lat, lng = calc_midpoint_from_bounding_box(bounding_box)
    logger.info(
        f"get_top_right_box {lat1, lat2, lat, lng}",
    )
    return lat, lat2, lng1, lng


def get_bottom_left_box(bounding_box):
    lat1, lat2, lng1, lng2 = bounding_box
    lat, lng = calc_midpoint_from_bounding_box(bounding_box)
    logger.info(
        f"get_bottom_left_box {lat, lat2, lng, lng2}",
    )
    return lat1, lat, lng, lng2


def get_bottom_right_box(bounding_box):
    lat1, lat2, lng1, lng2 = bounding_box
    lat, lng = calc_midpoint_from_bounding_box(bounding_box)
    logger.info(
        f"get_bottom_right_box {lat1, lat, lng, lng2}",
    )
    return lat, lat2, lng, lng2


def fetch_data(writer, bounding_box):
    with SgRequests() as session:
        lat1, lat2, lng1, lng2 = bounding_box
        locations = session.get(
            base_url.format(lat1, lng1, lat2, lng2), headers=_headers
        ).json()["result"]["hits"]["hits"]
        cnt = len(locations)

        logger.info(f"{cnt} {lat1, lng1, lat2, lng2} found")
        if cnt == LIMIT_CNT:
            top_left_box = get_top_left_box(bounding_box)
            fetch_data(writer, top_left_box)
            top_right_box = get_top_right_box(bounding_box)
            fetch_data(writer, top_right_box)

            bottom_left_box = get_bottom_left_box(bounding_box)
            fetch_data(writer, bottom_left_box)
            bottom_right_box = get_bottom_right_box(bounding_box)
            fetch_data(writer, bottom_right_box)

        write_data(writer, locations)


def write_data(writer, locations):
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
        if "Dublin" in _["city"] or "Dublin" in _["region"]:
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

        if phone and (phone.lower() == "tbc" or phone.lower() == "tba" or phone == "0"):
            phone = ""

        writer.write_row(
            SgRecord(
                page_url="https://www.regatta.com/us/store-locator/",
                store_number=_["store_id"],
                location_name=_["name"],
                street_address=street_address,
                city=city,
                state=addr.state,
                zip_postal=_["postcode"],
                latitude=_["location"]["lat"],
                longitude=_["location"]["lon"],
                country_code=country_code,
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )
        )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.GeoSpatialId,
            duplicate_streak_failure_factor=5000,
        )
    ) as writer:
        fetch_data(writer, coords)
