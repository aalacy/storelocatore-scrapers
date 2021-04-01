from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


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
        for _ in locations:
            addr = list(bs(_["address"], "lxml").stripped_strings)
            street_address = " ".join(addr[0].replace("–", "-").split(" ")[:-1])
            hours = []
            for x, hh in _["days"].items():
                time = f"{hh['open']}-{hh['close']}"
                if hh["is_closed"]:
                    time = "closed"
                hours.append(f"{days[int(x)]}: {time}")
            yield SgRecord(
                page_url=_["shop_now_button_url"],
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=addr[0].split(" ")[-1],
                latitude=_["latitude"],
                longitude=_["longitude"],
                zip_postal=" ".join(addr[1].split(" ")[1:]),
                country_code="CA",
                phone=_["phone_number"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
