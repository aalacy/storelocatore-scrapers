from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("passporthealthglobal")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

uk_url = "https://www.passporthealthglobal.com/en-gb/locations/"
ca_url = "https://www.passporthealthglobal.com/ca/locations/"
us_url = "https://www.passporthealthusa.com/locations/"
locator_domain = "https://www.passporthealthglobal.com"


def _c(val):
    if val.strip().endswith(","):
        return val[:-1]
    return val


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(us_url, headers=_headers).text, "lxml")
        links = soup.select("map#Map2 area")
        for link in links:
            state_url = "https://www.passporthealthusa.com" + link["href"]
            logger.info(f"[US] [state] {state_url}")
            sp = bs(session.get(state_url, headers=_headers).text, "lxml")
            for _ in sp.select("div.l_listing"):
                page_url = (
                    "https://www.passporthealthusa.com"
                    + _.select_one("span.locations a")["href"]
                )
                logger.info(f"[US] {page_url}")
                yield SgRecord(
                    page_url=page_url,
                    location_name=_.select_one('span[itemprop="name"]').text.strip(),
                    street_address=_.select_one('span[itemprop="streetAddress"]').text,
                    city=_c(_.select("span.streetAddress span")[1].text),
                    state=_.select_one('span[itemprop="addressRegion"]').text,
                    zip_postal=_.select_one('span[itemprop="postalCode"]').text,
                    country_code="US",
                    latitude=_.select_one("a.showMap")["lat"],
                    longitude=_.select_one("a.showMap")["lon"],
                    phone=_.select_one('span[itemprop="telephone"]').text,
                    locator_domain=locator_domain,
                )

        soup = bs(session.get(uk_url, headers=_headers).text, "lxml")
        links = soup.select('ul li[itemprop="name"] a')
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(f"[UK] {page_url}")
            sp = bs(session.get(page_url, headers=_headers).text, "lxml")
            yield SgRecord(
                page_url=page_url,
                location_name=sp.select_one('div[itemprop="name"]')
                .text.replace("\n", "")
                .strip(),
                street_address=sp.select_one('span[itemprop="streetAddress"]').text,
                city=_c(sp.select_one('span[itemprop="addressLocality"]').text),
                zip_postal=sp.select_one('span[itemprop="postalCode"]').text,
                country_code="UK",
                latitude=sp.select_one('meta[itemprop="latitude"]')["content"],
                longitude=sp.select_one('meta[itemprop="longitude"]')["content"],
                phone=sp.select_one('meta[itemprop="telephone"]')["content"],
                locator_domain=locator_domain,
            )

        soup = bs(session.get(ca_url, headers=_headers).text, "lxml")
        links = soup.select('ul li[itemprop="name"] a')
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(f"[CA] {page_url}")
            sp = bs(session.get(page_url, headers=_headers).text, "lxml")
            yield SgRecord(
                page_url=page_url,
                location_name=sp.select_one('div[itemprop="name"]')
                .text.replace("\n", "")
                .strip(),
                state=sp.select_one('span[itemprop="addressRegion"]').text,
                street_address=sp.select_one('span[itemprop="streetAddress"]').text,
                city=sp.select_one('span[itemprop="addressLocality"]').text,
                zip_postal=sp.select_one('span[itemprop="postalCode"]').text,
                country_code="CA",
                latitude=sp.select_one('meta[itemprop="latitude"]')["content"],
                longitude=sp.select_one('meta[itemprop="longitude"]')["content"],
                phone=sp.select_one('meta[itemprop="telephone"]')["content"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
