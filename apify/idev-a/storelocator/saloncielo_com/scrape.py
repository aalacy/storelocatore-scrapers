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
    val = str(val)
    if len(val) == 3:
        val = "0" + val
    return val[:2] + ":" + val[2:]


def fetch_data():
    locator_domain = "https://www.saloncielo.com"
    base_url = "https://locations.saloncielo.com"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.c-location-grid-col")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            _page_url = _.h2.a["href"]
            if not _page_url.startswith("/"):
                _page_url = "/" + _page_url
            page_url = base_url + _page_url
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = []
            for hh in json.loads(_.select_one("span.js-location-hours")["data-days"]):
                times = "closed"
                if hh["intervals"]:
                    times = f"{_time(hh['intervals'][0]['start'])}-{_time(hh['intervals'][0]['end'])}"
                hours.append(f"{hh['day']}: {times}")
            _name = _.select_one("span.location-name-brand").text.strip().split("-")
            location_name = _name[0].strip()
            location_name += " " + _.select_one("span.location-name-geo").text.strip()
            location_type = ""
            if _name[-1].strip().lower() == "closed":
                location_type = "Closed"
            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=" ".join(
                    _.select_one("span.c-address-street").stripped_strings
                ),
                city=_.select_one("span.c-address-city span").text.strip(),
                state=_.select_one("abbr.c-address-state").text.strip(),
                zip_postal=_.select_one("span.c-address-postal-code").text.strip(),
                country_code=_.select_one("abbr.c-address-country-name").text.strip(),
                phone=_.select_one("div.c-location-grid-item-phone a").text.strip(),
                locator_domain=locator_domain,
                latitude=sp1.select_one('meta[itemprop="latitude"]')["content"],
                longitude=sp1.select_one('meta[itemprop="longitude"]')["content"],
                location_type=location_type,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
