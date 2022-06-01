from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("redribbonbakeshop")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://redribbonbakeshop.us/"
base_url = "https://locations.redribbonbakeshop.us/"


def _d(sp1, page_url):
    street_address = sp1.select_one(
        "address div.Address-line span.Address-line1"
    ).text.strip()
    raw_address = " ".join(
        [" ".join(aa.stripped_strings) for aa in sp1.select("address div.Address-line")]
    )
    city = state = zip_postal = phone = ""
    if sp1.select_one("span.Address-city"):
        city = sp1.select_one("span.Address-city").text.strip()
    if sp1.select_one("span.Address-region"):
        state = sp1.select_one("span.Address-region").text.strip()
    if sp1.select_one("span.Address-postalCode"):
        zip_postal = sp1.select_one("span.Address-postalCode").text.strip()
    hours = []
    for hh in sp1.select("table tr.c-hours-details-row"):
        td = hh.select("td")
        hours.append(f"{td[0].text.strip()}: {' '.join(td[1].stripped_strings)}")
    if sp1.select_one("span.Phone-display"):
        phone = sp1.select_one("span.Phone-display").text.strip()

    return SgRecord(
        page_url=page_url,
        location_name=sp1.h1.text.strip(),
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zip_postal,
        latitude=sp1.select_one('meta[itemprop="latitude"]')["content"],
        longitude=sp1.select_one('meta[itemprop="longitude"]')["content"],
        country_code="US",
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation="; ".join(hours),
        raw_address=raw_address,
    )


def fetch_data():
    with SgRequests() as session:
        states = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "a.Directory-listLink"
        )
        for state in states:
            state_url = base_url + state["href"]
            sp0 = bs(session.get(state_url, headers=_headers).text, "lxml")
            cities = sp0.select("div.Main-content a.Directory-listLink")
            logger.info(f"[{state['href']}] {len(cities)} cities")
            if cities:
                for city in cities:
                    page_url = base_url + city["href"]
                    logger.info(page_url)
                    sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                    teasers = sp1.select(
                        "div.Main-content div.DirectoryPage div.Teaser-card"
                    )
                    logger.info(
                        f"[{state['href']}] [{city['href']}] {len(teasers)} teasers"
                    )
                    if teasers:
                        for teaser in teasers:
                            url = urljoin(
                                page_url, teaser.select_one("a.Teaser-cta")["href"]
                            )
                            logger.info(url)
                            sp2 = bs(session.get(url, headers=_headers).text, "lxml")
                            yield _d(sp2, url)
                    else:
                        yield _d(sp1, page_url)
            else:
                teasers = sp0.select(
                    "div.Main-content div.DirectoryPage div.Teaser-card"
                )
                logger.info(f"[{state['href']}] {len(teasers)} teasers")
                if teasers:
                    for teaser in teasers:
                        url1 = urljoin(
                            state_url, teaser.select_one("a.Teaser-cta")["href"]
                        )
                        logger.info(url1)
                        sp3 = bs(session.get(url, headers=_headers).text, "lxml")
                        yield _d(sp3, url)
                else:
                    yield _d(sp0, state_url)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
