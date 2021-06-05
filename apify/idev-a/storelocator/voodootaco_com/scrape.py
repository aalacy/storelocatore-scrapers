from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
import json

logger = SgLogSetup().get_logger("voodootaco")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.voodootaco.com/"
    base_url = "https://www.voodootaco.com/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.main-content-wrapper .sqs-col-4")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            map_data = json.loads(_.select_one("div.sqs-block-map")["data-block-json"])
            addr = parse_address_intl(
                f"{map_data['location']['addressLine1']} {map_data['location']['addressLine2']}"
            )
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = []
            _hr = list(_.select("div.sqs-block-content p")[1].stripped_strings)
            for x in range(0, len(_hr), 2):
                hours.append(f"{_hr[x]} {_hr[x+1]}")

            yield SgRecord(
                page_url=base_url,
                location_name=" ".join(_.h3.stripped_strings),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=map_data["location"]["addressCountry"],
                phone=_.select_one("div.sqs-block-content p").text.strip(),
                locator_domain=locator_domain,
                latitude=map_data["location"]["mapLat"],
                longitude=map_data["location"]["mapLng"],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
