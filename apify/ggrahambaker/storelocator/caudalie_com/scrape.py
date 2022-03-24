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


def get_country_by_code(code):
    if not code:
        return ""
    if us.states.lookup(code):
        return "US"
    elif code in ca_provinces_codes:
        return "CA"
    else:
        return ""


locator_domain = "https://us.caudalie.com"
urls = [
    "https://us.caudalie.com/store-locator/ajax?center_latitude=-19.73508046085627&center_longitude=-128.76074258125757&south_west_latitude=-82.64392126178035&north_east_latitude=75.20560346217067&south_west_longitude=-180&north_east_longitude=180&current_zoom=2&_=1646992483719",
    "https://us.caudalie.com/store-locator/ajax?center_latitude=-59.58408914185782&center_longitude=-170.77246133125757&south_west_latitude=-89.74002709930632&north_east_latitude=86.48313381832612&south_west_longitude=-180&north_east_longitude=180&current_zoom=1&_=1646992483720",
]


def fetch_data():
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
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2

                city = addr.city
                state = addr.state
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

                location_type = ""
                if _["cid"]:
                    location_type = _["cid"].split("_")[0]

                country_code = addr.country or get_country_by_code(addr.state)
                if not country_code:
                    if "México" in raw_address:
                        country_code = "México"
                yield SgRecord(
                    page_url="https://us.caudalie.com/store-locator",
                    store_number=_["id"],
                    location_name=_["label"],
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=addr.postcode,
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code=country_code,
                    location_type=location_type,
                    phone=_["phone_number"],
                    locator_domain=locator_domain,
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
