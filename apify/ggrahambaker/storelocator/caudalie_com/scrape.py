from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import us

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
urls = [
    "https://us.caudalie.com/store-locator/ajax?center_latitude=-14.235004&center_longitude=-51.92528&south_west_latitude=-89.74002709930632&north_east_latitude=86.48313381832612&south_west_longitude=-180&north_east_longitude=180&current_zoom=1&_=1646992483720",
    "https://kr.caudalie.com/store-locator/ajax?center_latitude=12.877157056913818&center_longitude=-37.92915513565662&south_west_latitude=-48.472181958176236&north_east_latitude=62.9057349020387&south_west_longitude=-105.69282701065661&north_east_longitude=29.8345167393434&current_zoom=3&_=1648885215304",
    "https://kr.caudalie.com/store-locator/ajax?center_latitude=38.09546919238839&center_longitude=115.13542397978671&south_west_latitude=6.964356460508858&north_east_latitude=60.0400395401089&south_west_longitude=72.77214272978671&north_east_longitude=157.4987052297867&current_zoom=4&_=1648885549787",
]


def parse_cn(raw_address):
    raw_address = raw_address.replace("中国", "")
    state = city = street_address = ""
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

    if "市" in raw_address:
        _ss = raw_address.split("市")
        street_address = _ss[-1]
        city = _ss[0]
        if "市" not in city:
            city += "市"

    return street_address, city, state, ""


def fetch_data():
    #  formula to find the South west and North East points from lat,lon between 10km.
    with SgRequests() as session:
        for base_url in urls:
            locations = session.get(base_url, headers=_headers).json()
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

                yield SgRecord(
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


if __name__ == "__main__":
    with SgRequests() as session:
        with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
            results = fetch_data()
            for rec in results:
                writer.write_row(rec)
