from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("wellnow")


def _headers():
    return {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
    }


def fetch_data():
    locator_domain = "https://wellnow.com"
    base_url = "https://wellnow.com/wp-json/facilities/v2/locations"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers()).json()
        logger.info(f"{len(locations)} found")
        for state, locs in locations.items():
            for _ in locs:
                if not _["status"] == "open":
                    continue
                addr = parse_address_intl(_["location"]["address"])
                street_address = _["location"]["address"].split(",")[0]
                yield SgRecord(
                    page_url=_["link"],
                    store_number=_["ID"],
                    location_name=_["title"],
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="US",
                    phone=_["phone"],
                    locator_domain=locator_domain,
                    latitude=_["lat"],
                    longitude=_["lng"],
                    hours_of_operation="; ".join(
                        bs(_["details"], "lxml").stripped_strings
                    )
                    .replace("–", "-")
                    .strip(),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
