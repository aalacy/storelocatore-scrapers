from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kfc")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://online.kfc.co.in/"
base_url = "https://restaurants.kfc.co.in/?page={}"


def fetch_data():
    with SgRequests() as session:
        page = 1
        while True:
            soup = bs(session.get(base_url.format(page), headers=_headers).text, "lxml")
            locations = soup.select("div.store-info-box")
            if not locations:
                break
            page += 1
            for _ in locations:
                addr = parse_address_intl(
                    " ".join(_.select_one(".outlet-address").stripped_strings)
                    + ", India"
                )
                street_address = addr.street_address_1 or ""
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                yield SgRecord(
                    page_url=_.select_one("a.btn-website")["href"],
                    location_name=_.select_one(".outlet-name").text.strip(),
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="India",
                    phone=_.select_one(".outlet-phone").text.strip(),
                    latitude=_.select_one("input.outlet-latitude")["value"],
                    longitude=_.select_one("input.outlet-longitude")["value"],
                    locator_domain=locator_domain,
                    hours_of_operation=": ".join(_.select("li")[-3].stripped_strings),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
