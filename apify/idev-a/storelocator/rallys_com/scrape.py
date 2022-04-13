from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from urllib.parse import urljoin

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.rallys.com/"
base_url = "https://locations.rallys.com/"
start_url = "https://locations.rallys.com/index.html"


def _d(_, page_url):
    if not _:
        return None
    latitude, longitude = _.select_one('meta[name="geo.position"]')["content"].split(
        ";"
    )
    street_address = _.select_one("span.Address-field.Address-line1").text.strip()
    if _.select_one("span.Address-field.Address-line2"):
        street_address += (
            " " + _.select_one("span.Address-field.Address-line2").text.strip()
        )
    city = state = zip_postal = ""
    if _.select_one("span.Address-field.Address-city"):
        city = _.select_one("span.Address-field.Address-city").text.strip()
    if _.select_one("abbr.Address-region"):
        state = _.select_one("abbr.Address-region").text.strip()
    if _.select_one("span.Address-postalCode"):
        zip_postal = _.select_one("span.Address-postalCode").text.strip()
    hours = []
    for hh in _.select("table.c-hours-details tbody tr"):
        td = hh.select("td")
        hours.append(f"{td[0].text.strip()}: {' '.join(td[1].stripped_strings)}")

    return SgRecord(
        page_url=page_url,
        location_name=_.h1.text.strip(),
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zip_postal,
        latitude=latitude,
        longitude=longitude,
        country_code="US",
        locator_domain=locator_domain,
        hours_of_operation="; ".join(hours),
        raw_address=" ".join(_.select_one("div.Address").stripped_strings),
    )


def _g(session, url):
    res = session.get(url, headers=_headers)
    if res.status_code != 200:
        return None
    return bs(res.text, "lxml")


def fetch_data():
    with SgRequests() as session:
        states = bs(session.get(start_url, headers=_headers).text, "lxml").select(
            "div.Main-content a"
        )
        for state in states:
            state_url = base_url + state["href"]
            logger.info(state_url)
            sp1 = _g(session, state_url)
            if not sp1:
                continue
            cities = sp1.select("li.Directory-listItem a")
            if cities:
                for city in cities:
                    city_url = urljoin(base_url, city["href"])
                    logger.info(f"[{state.text}] {city_url}")
                    sp2 = _g(session, city_url)
                    if not sp2:
                        continue
                    locations = sp2.select("li.Directory-listTeaser")
                    if locations:
                        for loc in locations:
                            page_url = urljoin(base_url, loc.a["href"])
                            logger.info(f"[{city.text.strip()}] {page_url}")
                            sp3 = _g(session, page_url)
                            yield _d(sp3, page_url)
                    else:
                        yield _d(sp2, city_url)
            else:
                locs = sp1.select("li.Directory-listTeaser")
                if locs:
                    for loc1 in locs:
                        page_url1 = urljoin(base_url, loc1.a["href"])
                        logger.info(f"[{city.text.strip()}] {page_url1}")
                        sp2 = _g(session, page_url1)
                        yield _d(sp2, page_url1)
                else:
                    yield _d(sp1, city_url)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            if rec:
                writer.write_row(rec)
