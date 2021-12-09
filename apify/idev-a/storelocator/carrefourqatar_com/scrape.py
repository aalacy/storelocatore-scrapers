from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("carrefourqatar")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.carrefourqatar.com"
base_url = (
    "https://www.carrefourqatar.com/mafqat/en/store-finder?q={}&page=0&storeFormat="
)

cities = [
    "Doha",
    "Abu az Zuluf",
    "Abu Thaylah",
    "Ad Dawhah al Jadidah",
    "Al Arish",
    "Al Bida ash Sharqiyah",
    "Al Ghanim",
    "Al Ghuwariyah",
    "Al Hilal al Gharbiyah",
    "Al Hilal ash Sharqiyah",
    "Al Hitmi",
    "Al Jasrah",
    "Al Jumaliyah",
    "Al Kabiyah",
    "Al Khalifat",
    "Al Khor",
    "Al Khawr",
    "Al Khuwayr",
    "Al Mafjar",
    "Al Qaabiyah",
    "Al Wakrah",
    "Al Adhbah",
    "An Najmah",
    "Ar Rakiyat",
    "Al Rayyan",
    "Ar Ruays",
    "As Salatah",
    "As Salatah al Jadidah",
    "As Sani",
    "As Sawq",
    "Ath Thaqab",
    "Blare",
    "Dukhan",
    "Ras Laffan Industrial City",
    "Umm Bab",
    "Umm Said",
    "Umm Salal Ali",
    "Umm Salal Mohammed",
]


def fetch_data():
    with SgRequests() as http:
        for city in cities:
            url = base_url.format(city)
            try:
                locations = http.get(url, headers=_headers).json()["data"]
            except:
                locations = []
            logger.info(f"[{city}] {len(locations)}")
            for _ in locations:
                street_address = _["line1"]
                if _["line2"]:
                    street_address += " " + _["line2"]
                hours = []
                for day, hh in _["openings"].items():
                    hours.append(f"{day}: {hh}")
                yield SgRecord(
                    location_name=f"{_['displayName']} - {_['town']}",
                    street_address=street_address,
                    city=_["town"],
                    state=_.get("state"),
                    zip_postal=_.get("postalCode"),
                    country_code="Qatar",
                    phone=_["phone"],
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    location_type=_["storeFormat"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.LOCATION_NAME,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
