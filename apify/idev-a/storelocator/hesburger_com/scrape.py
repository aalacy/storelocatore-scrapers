from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("hesburger")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.hesburger.com"
base_url = "https://www.hesburger.com/restaurants"


def fetch_data():
    with SgRequests() as session:
        countries = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "select#country option"
        )
        for country in countries:
            country_code = country.text.strip()
            logger.info(country_code)
            locations = json.loads(
                session.get(f"{base_url}?country={country['value']}", headers=_headers)
                .text.split("var DATA=")[1]
                .split("PLACES=")[0]
                .strip()[:-1]
            )
            for _ in locations:
                hours = []
                if _["aukioloajat"]:
                    hours = list(bs(_["aukioloajat"], "lxml").stripped_strings)
                city = _["kuntaNimi"]
                raw_address = _["osoite"].strip()
                if raw_address.endswith(","):
                    raw_address = raw_address[:-1]
                if country_code == "Russia":
                    if "Россия" not in raw_address:
                        raw_address = "Россия, " + raw_address
                elif country_code == "Estonia":
                    if "Eesti" not in raw_address:
                        raw_address += ", Eesti"
                elif country_code == "Ukraine":
                    if "Україна" not in raw_address:
                        raw_address += ", Україна"

                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                if not city:
                    city = addr.city
                zip_postal = addr.postcode
                if zip_postal:
                    if country_code == "Ukraine":
                        zip_postal = zip_postal.replace("UA", "").replace("-", "")
                        if not zip_postal.isdigit():
                            zip_postal = ""
                    elif country_code == "Finland":
                        zip_postal = zip_postal.split()[-1]
                    elif country_code == "Lithuania":
                        zip_postal = zip_postal.split()[0]
                yield SgRecord(
                    page_url=_["url"],
                    store_number=_["tid"],
                    location_name=_["nimi"],
                    street_address=street_address,
                    city=city,
                    state=addr.state,
                    zip_postal=zip_postal,
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code=country_code,
                    phone=_["phone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
