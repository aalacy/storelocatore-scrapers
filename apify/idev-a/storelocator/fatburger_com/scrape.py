from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from urllib.parse import urljoin


logger = SgLogSetup().get_logger("fatburger")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://fatburger.com/"
base_url = "https://locations.fatburger.com/index.html"
url = "https://locations.fatburger.com/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("ul.Directory-listLinks li a")
        logger.info(f"{len(links)} found")
        for link in links:
            country_url = urljoin(url, link["href"])
            states = bs(session.get(country_url, headers=_headers).text, "lxml").select(
                "ul.Directory-listLinks li a"
            )
            logger.info(f'{link["href"]} [{len(states)}]')
            for state in states:
                state_url = urljoin(url, state["href"])
                cities = bs(
                    session.get(state_url, headers=_headers).text, "lxml"
                ).select("ul.Directory-listLinks li a")
                logger.info(f'{state["href"]} [{len(cities)}]')
                for city in cities:
                    city_url = urljoin(url, city["href"])
                    locs = bs(
                        session.get(city_url, headers=_headers).text, "lxml"
                    ).select("li.Directory-listTeaser h2 a")
                    if locs:
                        for loc in locs:
                            page_url = urljoin(url, loc["href"])
                            logger.info(page_url)
                            sp1 = bs(
                                session.get(page_url, headers=_headers).text, "lxml"
                            )
                            state = zip_postal = city = street_address = ""
                            if sp1.select_one(".c-address-state"):
                                state = sp1.select_one(".c-address-state").text.strip()
                            if sp1.select_one(".c-address-postal-code"):
                                zip_postal = sp1.select_one(
                                    ".c-address-postal-code"
                                ).text.strip()
                            if sp1.select_one('meta[itemprop="streetAddress"]'):
                                street_address = sp1.select_one(
                                    'meta[itemprop="streetAddress"]'
                                )["content"]
                            if sp1.select_one('meta[itemprop="addressLocality"]'):
                                city = sp1.select_one(
                                    'meta[itemprop="addressLocality"]'
                                )["content"]
                            phone = ""
                            if sp1.select_one("span#telephone"):
                                phone = sp1.select_one("span#telephone").text.strip()
                            try:
                                coord = (
                                    sp1.select_one('link[itemprop="hasMap"]')["href"]
                                    .split("center=")[1]
                                    .split("&")[0]
                                    .split("%2C")
                                )
                            except:
                                coord = ["", ""]
                            hours = [
                                hh["content"]
                                for hh in sp1.select(
                                    "table.c-location-hours-details tbody tr"
                                )
                            ]
                            yield SgRecord(
                                page_url=page_url,
                                location_name=loc.text.strip(),
                                street_address=street_address,
                                city=city,
                                state=state,
                                zip_postal=zip_postal,
                                country_code=link.text.strip(),
                                phone=phone,
                                locator_domain=locator_domain,
                                latitude=coord[0],
                                longitude=coord[1],
                                hours_of_operation="; ".join(hours).replace("–", "-"),
                            )
                    else:
                        import pdb

                        pdb.set_trace()


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
