from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("miafrancesca")

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.miafrancesca.com"
        base_url = "https://www.miafrancesca.com/locations/"
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("locations:")[1]
            .split("apiKey:")[0]
            .strip()[:-1]
        )
        logger.info(f"{len(locations)} found")
        for _ in locations:
            if not _["street"]:
                continue
            page_url = locator_domain + _["url"]
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in bs(_["hours"], "lxml").select("p")
            ]
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["street"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal_code"],
                country_code="US",
                phone=_["phone_number"],
                latitude=_["lat"],
                longitude=_["lng"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
