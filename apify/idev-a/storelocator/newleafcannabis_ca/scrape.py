from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgselenium import SgChrome
import json
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("newleafcannabis")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fetch_data():
    locator_domain = "https://www.newleafcannabis.ca/"
    base_url = "https://www.newleafcannabis.ca/contact/"
    json_url = "https://v3.dutchie.com/graphql?operationName=ConsumerDispensaries"
    with SgChrome() as driver:
        with SgRequests() as session:
            res = session.get(base_url, headers=_headers).text
            locations = json.loads(
                res.split("var now_open_store_data =")[1]
                .split("var coming_soon_store_data =")[0]
                .strip()[1:-2]
            )
            for _ in locations:
                address = list(bs(_["address"], "lxml").stripped_strings)
                hours = []
                for x, hh in _["days"].items():
                    times = f"{hh['open']}-{hh['close']}"
                    if hh["is_closed"]:
                        times = "closed"
                    hours.append(f"{days[int(x)]}: {times}")

                page_url = _["shop_now_button_url"]
                if not page_url.endswith("/"):
                    page_url += "/"

                driver.get(page_url)
                logger.info(page_url)
                exist = False
                while not exist:
                    time.sleep(1)
                    for rr in driver.requests:
                        if rr.url.startswith(json_url) and rr.response:
                            exist = True
                            locations = json.loads(rr.response.body)
                            addr = json.loads(rr.response.body)["data"][
                                "filteredDispensaries"
                            ][0]["location"]
                            street_address = addr["ln1"]
                            if addr["ln2"]:
                                street_address += ", " + addr["ln2"]
                            yield SgRecord(
                                page_url=_["shop_now_button_url"],
                                store_number=_["id"],
                                location_name=_["name"],
                                street_address=street_address,
                                city=_["city"],
                                state=addr["state"],
                                latitude=_["latitude"],
                                longitude=_["longitude"],
                                zip_postal=" ".join(address[1].split(" ")[1:]),
                                country_code="CA",
                                phone=_["phone_number"],
                                locator_domain=locator_domain,
                                hours_of_operation="; ".join(hours),
                            )

                            break


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
