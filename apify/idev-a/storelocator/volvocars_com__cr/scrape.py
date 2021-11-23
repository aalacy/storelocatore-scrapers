from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("volvocars")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.volvocars.com/cr"
base_url = "https://www.volvocars.com/data/retailer?countryCode={}&languageCode=EN&northToSouthSearch=False&serviceType=Service&isOxp=True&sc_site=uk"

country_codes = [
    "CR",
    "DO",
    "EC",
    "PE",
    "AO",
    "EG",
    "JO",
    "KW",
    "MU",
    "BH",
    "MA",
    "OM",
    "QA",
    "AE",
    "ZM",
    "ZW",
    "NZ",
    "VN",
    "CY",
    "EE",
    "LV",
    "IT",
    "MK",
    "MT",
    "ME",
    "AL",
    "RS",
    "BA",
    "AZ",
    "LB",
    "GE",
    "IS",
    "SA",
    "NA",
]


def fetch_data():
    with SgRequests() as session:
        for code in country_codes:
            locations = session.get(base_url.format(code), headers=_headers).json()
            logger.info(f"[{code}] {len(locations)}")
            for _ in locations:
                street_address = _["AddressLine1"]
                hours = []
                for hr in _["Services"]:
                    if hr["ServiceType"] == "new_car_sales" and hr["OpeningHours"]:
                        hours.append(hr["OpeningHours"])

                hours_of_operation = (
                    "; ".join(hours)
                    .replace("Sales:", "")
                    .replace('"', "")
                    .replace("<br>", " ")
                )
                if hours_of_operation == ".":
                    hours_of_operation = ""
                phone = _["Phone"]
                if phone:
                    phone = (
                        phone.split(";")[0]
                        .replace("(Após-Venda)", "")
                        .split(",")[0]
                        .replace("Växel:", "")
                        .split("/ +")[0]
                        .split("/+")[0]
                        .split("or")[0]
                        .strip()
                    )
                    if "@" in phone:
                        phone = ""
                yield SgRecord(
                    store_number=_["DealerId"],
                    location_name=_["Name"],
                    street_address=street_address,
                    city=_["City"],
                    state=_["District"],
                    zip_postal=_["ZipCode"],
                    latitude=_["GeoCode"]["Latitude"],
                    longitude=_["GeoCode"]["Longitude"],
                    country_code=_["Country"],
                    phone=phone,
                    locator_domain=locator_domain,
                    location_type=_["ServiceType"],
                    hours_of_operation=hours_of_operation,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
