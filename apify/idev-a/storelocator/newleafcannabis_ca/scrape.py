from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("newleafcannabis")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

states = {
    "A": "NL",
    "B": "NS",
    "C": "PE",
    "E": "NB",
    "G": "QC",
    "H": "QC",
    "J": "QC",
    "K": "ON",
    "L": "ON",
    "M": "ON",
    "N": "ON",
    "P": "ON",
    "R": "MB",
    "S": "SK",
    "T": "AB",
    "V": "BC",
    "X": "NU/NT",
    "Y": "YT",
}


def fetch_data():
    locator_domain = "https://www.newleafcannabis.ca/"
    base_url = "https://www.newleafcannabis.ca/contact/"
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        locations = json.loads(
            res.split("var now_open_store_data =")[1]
            .split("var coming_soon_store_data =")[0]
            .strip()[1:-2]
        )
        logger.info(f"{len(locations)} found")
        for _ in locations:
            address = list(bs(_["address"], "lxml").stripped_strings)
            hours = []
            for x, hh in _["days"].items():
                times = f"{hh['open']}-{hh['close']}"
                if hh["is_closed"]:
                    times = "closed"
                hours.append(f"{days[int(x)]}: {times}")

            zip_postal = " ".join(address[1].split(" ")[1:])
            yield SgRecord(
                page_url=_["shop_now_button_url"],
                store_number=_["id"],
                location_name=_["name"],
                street_address=address[0].replace("–", "-"),
                city=_["city"],
                state=states[zip_postal[0].upper()],
                latitude=_["latitude"],
                longitude=_["longitude"],
                zip_postal=zip_postal,
                country_code="CA",
                phone=_["phone_number"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
