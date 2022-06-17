from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import us
from sglogging import SgLogSetup
from math import radians, cos, sin, asin, sqrt, pi, atan2

logger = SgLogSetup().get_logger("")

LIMIT_CNT = 30
LIMIT_DISTANCE = 608.0242223147545

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

ca_provinces_codes = {
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NS",
    "NT",
    "NU",
    "ON",
    "PE",
    "QC",
    "SK",
    "YT",
}

ca_provinces = [
    "alberta",
    "british columbia",
    "manitoba",
    "new brunswick",
    "newfoundland and labrador",
    "nova scotia",
    "ontario",
    "prince edward island",
    "quebec",
    "saskatchewan",
]


def get_country_by_code(code):
    if not code:
        return ""
    if us.states.lookup(code):
        return "US"
    elif code in ca_provinces_codes or code in ca_provinces:
        return "CA"
    else:
        return ""


locator_domain = "https://us.caudalie.com"
base_url = "https://us.caudalie.com/store-locator/ajax?center_latitude={}&center_longitude={}&south_west_latitude={}&north_east_latitude={}&south_west_longitude={}&north_east_longitude={}&current_zoom=8&_=1646992483720"

coords = (-89.99993398134211, 89.03514979049804, -180, 180)


def calc_distance(bounding_box):
    lat1, lat2, lon1, lon2 = bounding_box

    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

    c = 2 * asin(sqrt(a))

    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371

    # calculate the result
    return c * r


def from_latlng_to_cartesian(lat, lng):
    lat = lat * pi / 180
    lng = lng * pi / 180
    x = cos(lat) * cos(lng)
    y = cos(lat) * sin(lng)
    z = sin(lat)
    return x, y, z


def calc_midpoint_from_catesians(cat1, cat2):
    x1, y1, z1 = cat1
    x2, y2, z2 = cat2
    x = (x1 + x2) / 2
    y = (y1 + y2) / 2
    z = (z1 + z2) / 2
    Lon = atan2(y, x)
    Hyp = sqrt(x * x + y * y)
    Lat = atan2(z, Hyp)

    lat = Lat * (180 / pi)
    lng = Lon * (180 / pi)

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
    return lat, lat1, lng1, lng


def get_top_right_box(bounding_box):
    lat1, lat2, lng1, lng2 = bounding_box
    lat, lng = calc_midpoint_from_bounding_box(bounding_box)
    logger.info(
        f"get_top_right_box {lat1, lat2, lat, lng}",
    )
    return lat2, lat, lng1, lng


def get_bottom_left_box(bounding_box):
    lat1, lat2, lng1, lng2 = bounding_box
    lat, lng = calc_midpoint_from_bounding_box(bounding_box)
    logger.info(
        f"get_bottom_left_box {lat, lat2, lng, lng2}",
    )
    return lat, lat1, lng, lng2


def get_bottom_right_box(bounding_box):
    lat1, lat2, lng1, lng2 = bounding_box
    lat, lng = calc_midpoint_from_bounding_box(bounding_box)
    logger.info(
        f"get_bottom_right_box {lat1, lat, lng, lng2}",
    )
    return lat2, lat, lng2, lng2


def _city_street_cn(city, raw_address):
    cc = raw_address.split(city)[-1].split("区")
    return city, "区".join(cc[len(cc) - 1 :])


def parse_cn(raw_address):
    raw_address = raw_address.replace("中国", "")
    state = city = street_address = ""
    if "市" in raw_address:
        _ss = raw_address.split("市")
        street_address = _ss[-1]
        city = _ss[0]
        if "市" not in city:
            city += "市"
    else:
        if "北京" in raw_address:
            city, street_address = _city_street_cn("北京", raw_address)
        elif "上海" in raw_address:
            city, street_address = _city_street_cn("上海", raw_address)

        cc = raw_address.split("区")
        street_address = "区".join(cc[len(cc) - 1 :])

    if "澳门" in raw_address:
        city = "澳门"
        street_address = raw_address.replace("澳门", "")
    if "香港" in raw_address:
        city = "香港"
        street_address = raw_address.replace("香港", "")
    if "省" in raw_address:
        state = raw_address.split("省")[0] + "省"
        raw_address = raw_address.split("省")[-1]
    if "自治区" in raw_address:
        state = raw_address.split("自治区")[0] + "自治区"
        raw_address = raw_address.split("自治区")[-1]
    if "内蒙古" in raw_address:
        state = "内蒙古"
        raw_address = raw_address.replace("内蒙古", "")
    if "自治州" in raw_address:
        state = raw_address.split("自治州")[0] + "自治州"
        raw_address = raw_address.split("自治州")[-1]

    if "路" in city:
        _cc = city.split("路")
        city = _cc[-1]
        street_address = _cc[0] + "路" + street_address
    if "号" in city:
        _cc = city.split("号")
        city = _cc[-1]
        street_address = _cc[0] + "号" + street_address
    if "区" in city:
        _cc = city.split("区")
        city = _cc[-1]
        street_address = _cc[0] + "区" + street_address

    return street_address, city, state, ""


def write_data(writer, locations):
    for _ in locations:
        raw_address = (
            ", ".join(bs(_["address"], "lxml").stripped_strings)
            .replace("\n", ", ")
            .replace("\r", " ")
            .replace("QRO.C.P.", "QRO C.P.")
        )
        addr = parse_address_intl(raw_address)
        street_address = city = state = zip_postal = ""
        if "中国" in raw_address or "北京" in raw_address or "上海" in raw_address:
            country_code = "中国"
            street_address, city, state, zip_postal = parse_cn(raw_address)
        else:
            country_code = addr.country or get_country_by_code(addr.state)
            if not country_code:
                if "México" in raw_address:
                    country_code = "México"
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            city = addr.city
            if "Brooklyn" in raw_address:
                city = "Brooklyn"
                country_code = "US"
            if "Gosford" in raw_address:
                city = "Gosford"
                country_code = "Australia"
            if "Brookvale" in raw_address:
                city = "Brookvale"
                country_code = "Australia"
            if "sydney" in raw_address.lower():
                city = "Sydney"
                country_code = "Australia"
            if "chadstone" in raw_address.lower():
                city = "Chadstone"
                country_code = "Australia"
            if "Maribyrnong" in raw_address:
                city = "Maribyrnong"
                country_code = "Australia"
            if "Playa del Carmen" in raw_address:
                city = "Playa del Carmen"
                country_code = "Mexico"
            if "Veracruz" in raw_address:
                city = "Veracruz"
                country_code = "Mexico"
            if "sao roque" in raw_address.lower():
                city = "SAO ROQUE"
                country_code = "Mexico"
            state = addr.state
            zip_postal = addr.postcode
            if city:
                city = (
                    city.replace("Granada Del. Miguel Hidalgo", "")
                    .replace("Col.", "")
                    .strip()
                )
                if city == "Estado De":
                    state = "Estado De"
                    city = ""
            if street_address:
                if "Juárez" in raw_address:
                    city = "Juárez"
                if "Huixquilucan" in raw_address:
                    city = "Huixquilucan"

                if city:
                    street_address = street_address.split(city)[0].strip()

                if street_address.endswith(","):
                    street_address = street_address[:-1]

        if "서울" in raw_address:
            country_code = "South Korea"

        location_type = ""
        if _["cid"]:
            location_type = _["cid"].split("_")[0]

        if location_type == "0":
            location_type = ""

        if street_address and street_address.isdigit():
            street_address = raw_address.split(",")[0]

        writer.write_row(
            SgRecord(
                page_url="https://us.caudalie.com/store-locator",
                store_number=_["id"],
                location_name=_["label"],
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=country_code,
                location_type=location_type,
                phone=_["phone_number"],
                locator_domain=locator_domain,
                raw_address=raw_address,
            )
        )


def fetch_data(writer, bounding_box, zoom):
    #  formula to find the South west and North East points from lat,lon between 10km.
    with SgRequests() as session:
        lat1, lat2, lng1, lng2 = bounding_box
        lat, lng = calc_midpoint_from_bounding_box(bounding_box)
        locations = session.get(
            base_url.format(lat, lng, lat1, lat2, lng1, lng2, zoom), headers=_headers
        ).json()
        cnt = len(locations)

        distance = calc_distance(bounding_box)
        logger.info(f"[***********]{cnt} {lat1, lng1, lat2, lng2, distance} found")
        if distance >= LIMIT_DISTANCE:
            top_left_box = get_top_left_box(bounding_box)
            fetch_data(writer, top_left_box, zoom)
            top_right_box = get_top_right_box(bounding_box)
            fetch_data(writer, top_right_box, zoom)

            bottom_left_box = get_bottom_left_box(bounding_box)
            fetch_data(writer, bottom_left_box, zoom)
            bottom_right_box = get_bottom_right_box(bounding_box)
            fetch_data(writer, bottom_right_box, zoom)

        write_data(writer, locations)


if __name__ == "__main__":
    with SgRequests() as session:
        with SgWriter(
            SgRecordDeduper(
                RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=50000
            )
        ) as writer:
            fetch_data(writer, coords, 13)
