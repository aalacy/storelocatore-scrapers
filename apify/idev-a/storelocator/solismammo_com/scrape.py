from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("solismammo")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.solismammo.com"
    base_url = "https://www.solismammo.com/find-a-center/all-locations"
    with SgRequests() as session:
        sp = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = sp.select("div.geolocation-location")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            page_url = (
                f"{locator_domain}{_.select_one('div.views-field-title').a['href']}"
            )
            addr = list(_.select_one("div.views-field-field-location").stripped_strings)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            logger.info(page_url)
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in sp1.select("div.field--name-field-working-hours .field__item")
            ]
            yield SgRecord(
                page_url=page_url,
                location_name=_.select_one("div.views-field-title").a.text,
                street_address=addr[0],
                city=addr[1].split(",")[0],
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                latitude=_["data-lat"],
                longitude=_["data-lng"],
                country_code="US",
                phone=_.select_one("div.views-field-field-phone").a.text,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
