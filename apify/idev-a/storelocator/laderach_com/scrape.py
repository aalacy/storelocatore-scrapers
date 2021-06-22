from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
import json

logger = SgLogSetup().get_logger("laderach")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _time(val):
    val = str(val)
    if len(val) == 3:
        val = "0" + val
    return val[:2] + ":" + val[2:]


locator_domain = "https://laderach.com/"
base_url = "https://us.laderach.com/our-locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        stores = soup.select("div.store-row-container div.store-row")
        logger.info(f"{len(stores)} found")
        for store in stores:
            url = f"https://data.accentapi.com/feed/{store.iframe['src'].split('/')[-1]}.json?nocache=1622049836522"
            logger.info(url)
            _ = session.get(url, headers=_headers).json()
            _addr = _["content"]["location"]
            addr = parse_address_intl(_addr)
            city = addr.city
            state = addr.state
            zip_postal = addr.postcode
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if street_address.isdigit() and len(_addr.split(",")) > 1:
                street_address = _addr.split(",")[0]
            country_code = addr.country
            if not country_code and "Singapore" in _addr:
                country_code = "Singapore"
            if country_code == "United Arab Emirates":
                street_address = " ".join(_addr.split("-")[:-3])
                city = _addr.split("-")[-3]
                state = _addr.split("-")[-2]
                zip_postal = ""
            hours = []
            if _["content"]["open_hours"]:
                for hh in json.loads(_["content"]["open_hours"]):
                    if not hh["time_end"]:
                        continue
                    hours.append(
                        f"{hh['day']} {_time(hh['time_start'])}-{_time(hh['time_end'])}"
                    )
            yield SgRecord(
                page_url=_["content"]["website"],
                location_name=_["content"]["place_name"],
                store_number=store["id"].split("-")[-1],
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                phone=_["content"]["phone"],
                locator_domain=locator_domain,
                location_type=_["content"]["place_type"],
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
