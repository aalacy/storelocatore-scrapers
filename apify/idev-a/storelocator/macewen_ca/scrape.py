from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


logger = SgLogSetup().get_logger("macewen")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

urls = [
    "https://macewen.ca/wp-content/cache/interactive-maps/home-comfort-centre-en.json",
    "https://macewen.ca/wp-content/cache/interactive-maps/station-en.json",
]


def fetch_data():
    locator_domain = "https://macewen.ca/"
    with SgRequests() as session:
        for base_url in urls:
            locations = session.get(base_url, headers=_headers).json()["places"]
            for _ in locations:
                hours = []
                for k, v in _["hours"].items():
                    hours.append(f"{days[int(k)-1]}: {v}")
                addr = parse_address_intl(
                    f"{_['address']['street']} {_['address']['city']} {_['address']['province']} {_['address']['country']}"
                )
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                city = addr.city
                state = addr.state
                zip_postal = addr.postcode
                if street_address.isdigit():
                    street_address = _["address"]["street"]
                    city = _["address"]["city"]
                    state = _["address"]["province"]
                    zip_postal = ""
                yield SgRecord(
                    page_url=_["permalink"],
                    location_name=_["title"].replace("’", "'").replace("–", "-"),
                    store_number=_["id"],
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    latitude=_["position"]["lat"],
                    longitude=_["position"]["lng"],
                    country_code="CA",
                    phone=_["phone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours).replace("–", "-"),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
