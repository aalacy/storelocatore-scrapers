from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("cnb")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.cnb.com"
base_url = "https://locations.cnb.com/"


def _detail(_, page_url):
    hours = []
    if _.select("section.Core table.c-hours-details"):
        for hh in _.select("section.Core table.c-hours-details")[0].select("tbody tr"):
            td = hh.select("td")
            hours.append(f"{td[0].text}: {td[1].text}")

    location_type = _.select_one("span.LocationName-brand").text.strip()
    if location_type.split("-")[-1].strip() == "CLOSED":
        location_type = location_type.split("-")[0]
        hours = ["CLOSED"]
    if _.select_one("div.Core-hoursTemporarilyClosed"):
        hours = ["Temporarily Closed"]
    return SgRecord(
        page_url=page_url,
        location_name=_.select_one("span.LocationName-geo").text.strip(),
        street_address=_.select_one('meta[itemprop="streetAddress"]')["content"],
        city=_.select_one('meta[itemprop="addressLocality"]')["content"],
        state=_.select_one('span[itemprop="addressRegion"]').text.strip(),
        latitude=_.select_one('meta[itemprop="latitude"]')["content"],
        longitude=_.select_one('meta[itemprop="longitude"]')["content"],
        zip_postal=_.select_one('span[itemprop="postalCode"]').text.strip(),
        country_code="US",
        phone=_.select_one("a.Phone-link").text.strip(),
        locator_domain=locator_domain,
        location_type=location_type,
        hours_of_operation="; ".join(hours),
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        states = soup.select("ul.Directory-listLinks li a")
        logger.info(f"[total] {len(states)} found")
        for state in states:
            state_url = f"{base_url}{state['href']}"
            sp1 = bs(session.get(state_url, headers=_headers).text, "lxml")
            cities = sp1.select("ul.Directory-listLinks li a")
            if cities:
                for city in cities:
                    city_url = f"{base_url}{city['href']}"
                    sp2 = bs(session.get(city_url, headers=_headers).text, "lxml")
                    dirs = sp2.select("ul.Directory-listTeasers li a.Teaser-titleLink")
                    if dirs:
                        for link in dirs:
                            href = link["href"]
                            if href.startswith(".."):
                                href = href[2:]
                            url = f"https://locations.cnb.com{href}"
                            sp3 = bs(session.get(url, headers=_headers).text, "lxml")
                            logger.info(f"[{city['href']}] {url}")
                            yield _detail(sp3, url)
                    else:
                        logger.info(city_url)
                        yield _detail(sp2, city_url)
            else:
                logger.info(state_url)
                yield _detail(sp1, state_url)


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
