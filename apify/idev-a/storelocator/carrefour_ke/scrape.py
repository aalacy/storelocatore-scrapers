from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("carrefour")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.carrefour.ke"
base_url = "https://www.carrefour.ke/mafken/en/store-finder?q={}&page=0&storeFormat="
city_url = "https://en.wikipedia.org/wiki/List_of_cities_in_Kenya"


def fetch_data():
    with SgRequests() as http:
        cities = bs(http.get(city_url, headers=_headers).text, "lxml").select(
            "table.multicol tr li a"
        )
        for _city in cities:
            city = _city.text.strip()
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
                    country_code="Kenya",
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
