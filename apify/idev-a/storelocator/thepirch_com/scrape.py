from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import dirtyjson as json
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("pirch")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _c(val):
    if val.startswith(";"):
        val = val[1:]
    return val


def fetch_data():
    locator_domain = "https://www.pirch.com"
    base_url = "https://www.pirch.com/home"
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var StoreLocation =")[1]
            .split("DATA.Stores")[0]
            .strip()[:-1]
        )
        logger.info(f"{len(locations)} found")
        for _ in locations:
            page_url = locator_domain + _["st_page_url"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = parse_address_intl(
                " ".join(list(sp1.select_one("div.store_info p").stripped_strings)[:-1])
            )
            street_address = addr.street_address_1
            if not street_address:
                street_address = ""
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = []
            for hh in _["st_schedule"]:
                hours.append(f"{hh['day']}: {hh['open']}-{hh['close']}")
            try:
                coord = (
                    sp1.select_one("a#mapStoreLocationDesktop")["href"]
                    .split("/%40")[1]
                    .split("/data")[0]
                    .split(",")
                )
            except:
                coord = ["", ""]
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=_["st_contact"][0]["phone"],
                locator_domain=locator_domain,
                latitude=_c(coord[0]),
                longitude=_c(coord[1]),
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
