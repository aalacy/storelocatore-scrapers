from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("saloncielo")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _time(val):
    return str(val)[:2] + ":" + str(val)[2:]


def fetch_data():
    locator_domain = "https://www.saloncielo.com/"
    base_url = "https://locations.saloncielo.com"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.c-location-grid-col")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            page_url = base_url + _.h2.a["href"]
            hours = []
            for hh in json.loads(_.select_one("span.js-location-hours")["data-days"]):
                times = "closed"
                if hh["intervals"]:
                    times = f"{_time(hh['intervals'][0]['start'])}-{_time(hh['intervals'][0]['end'])}"
                hours.append(f"{hh['day']}: {times}")
            yield SgRecord(
                page_url=page_url,
                location_name=_.h2.text.strip().split("-")[0],
                street_address=" ".join(
                    _.select_one("span.c-address-street").stripped_strings
                ),
                city=_.select_one("span.c-address-city span").text.strip(),
                state=_.select_one("abbr.c-address-state").text.strip(),
                zip_postal=_.select_one("span.c-address-postal-code").text.strip(),
                country_code=_.select_one("abbr.c-address-country-name").text.strip(),
                phone=_.select_one("div.c-location-grid-item-phone").text.strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
