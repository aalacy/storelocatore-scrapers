from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("era")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

streets = []


def fetch_data():
    locator_domain = "https://www.era.com"
    base_url = "https://www.era.com/real-estate-agents"
    with SgRequests() as session:
        states = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "ul.hide-list-bullets a"
        )
        logger.info(f"{len(states)} states found")
        for state in states:
            state_url = locator_domain + state["href"]
            locations = bs(
                session.get(state_url, headers=_headers).text, "lxml"
            ).select("ul.hide-list-bullets a")
            for _ in locations:
                list_url = locator_domain + _["href"]
                logger.info(f"[List] {list_url}")
                sp1 = bs(session.get(list_url, headers=_headers).text, "lxml")
                details = sp1.select(".pod__office h3 a")
                for detail in details:
                    page_url = locator_domain + detail["href"]
                    logger.info(f"[{state.text}][page] {page_url}")
                    res = session.get(page_url, headers=_headers).text
                    sp2 = bs(res, "lxml")
                    latitude = (
                        res.split("window._METRO_LATITUDE =")[1]
                        .split("window._METRO_LONGITUDE =")[0]
                        .strip()[:-1]
                    )
                    longitude = (
                        res.split("window._METRO_LONGITUDE =")[1]
                        .split("var")[0]
                        .strip()[:-1]
                    )
                    street_address = sp2.select_one(
                        'span[itemprop="streetAddress"]'
                    ).text.strip()
                    _street = street_address + latitude + longitude
                    if _street in streets:
                        continue
                    streets.append(_street)
                    yield SgRecord(
                        page_url=page_url,
                        location_name=sp2.select_one("h1.heading-std").text.strip(),
                        street_address=street_address,
                        city=sp2.select_one(
                            'span[itemprop="addressLocality"]'
                        ).text.strip(),
                        state=sp2.select_one(
                            'span[itemprop="addressRegion"]'
                        ).text.strip(),
                        zip_postal=sp2.select_one(
                            'span[itemprop="postalCode"]'
                        ).text.strip(),
                        country_code="US",
                        phone=sp2.select_one('meta[itemprop="telephone"]')["content"],
                        locator_domain=locator_domain,
                        latitude=latitude,
                        longitude=longitude,
                    )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
