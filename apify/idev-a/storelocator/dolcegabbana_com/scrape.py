from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
from urllib.parse import urljoin

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("dolcegabbana")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://boutique.dolcegabbana.com/"
base_url = "https://boutique.dolcegabbana.com/directory"


def _time(val):
    val = str(val)
    if len(val) == 3:
        val = "0" + val
    return val[:2] + ":" + val[2:]


def _entities(sp, url):
    try:
        return json.loads(sp.select_one("script#js-map-config-dir-map").string.strip())[
            "entities"
        ]
    except:
        logger.info(url)
        return []


def parse_data(entity, page_url):
    _ = entity["profile"]
    street_address = _["address"]["line1"]
    if _["address"]["line2"]:
        street_address = _["address"]["line2"]
    latitude = longitude = ""
    if "cityCoordinate" in _:
        latitude = _["cityCoordinate"]["lat"]
        longitude = _["cityCoordinate"]["long"]
    elif "geocodedCoordinate" in _:
        latitude = _["geocodedCoordinate"]["lat"]
        longitude = _["geocodedCoordinate"]["long"]
    hours = []
    for hh in _["hours"]["normalHours"]:
        times = "closed"
        if not hh["isClosed"]:
            times = f"{_time(hh['intervals'][0]['start'])}-{_time(hh['intervals'][0]['end'])}"
        hours.append(f"{hh['day']}: {times}")
    location_type = ""
    if "temporary closed" in _.get("additionalHoursText", ""):
        location_type = "Temporary closed"
    if "c_locationPageMetaTitle" in _:
        location_name = _["c_locationPageMetaTitle"]
    elif "geomodifier" in _:
        location_name = _["geomodifier"]

    return SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=_["address"]["city"],
        state=_["address"]["region"],
        zip_postal=_["address"]["postalCode"],
        latitude=latitude,
        longitude=longitude,
        phone=_.get("mainPhone", {}).get("display", ""),
        country_code=_["address"]["countryCode"],
        locator_domain=locator_domain,
        location_type=location_type,
        hours_of_operation="; ".join(hours),
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        continents = soup.select("ul.Directory-listLinks li.Directory-listItem a")
        logger.info(f"[continents] {len(continents)} found")
        for continent in continents:
            continent_url = urljoin(locator_domain, continent["href"])
            sp1 = bs(session.get(continent_url, headers=_headers).text, "lxml")
            countries = sp1.select("ul.Directory-listLinks li.Directory-listItem a")
            if not countries:
                for entity in _entities(sp1, continent_url):
                    yield parse_data(entity, continent_url)
            else:
                logger.info(f"[{continent.text}] [country] {len(countries)} found")
                for country in countries:
                    state_url = urljoin(locator_domain, country["href"])
                    sp2 = bs(session.get(state_url, headers=_headers).text, "lxml")
                    cities = sp2.select(
                        "ul.Directory-listLinks li.Directory-listItem a"
                    )
                    if not cities:
                        teasers = sp2.select(
                            "ul.Directory-listTeasers li.Directory-listTeaser a.Teaser-titleLink"
                        )
                        if not teasers:
                            for entity in _entities(sp2, state_url):
                                yield parse_data(entity, state_url)
                        else:
                            logger.info(
                                f"[{country.text}] [teaser] {len(teasers)} found"
                            )
                            for teaser in teasers:
                                teaser_url = urljoin(locator_domain, teaser["href"])
                                sp2_1 = bs(
                                    session.get(teaser_url, headers=_headers).text,
                                    "lxml",
                                )
                                for entity in _entities(sp2_1, teaser_url):
                                    yield parse_data(entity, teaser_url)
                    else:
                        logger.info(f"[{country.text}] [city] {len(cities)} found")
                        for city in cities:
                            city_url = urljoin(locator_domain, city["href"])
                            sp3 = bs(
                                session.get(city_url, headers=_headers).text, "lxml"
                            )
                            locs = sp3.select(
                                "ul.Directory-listLinks li.Directory-listItem a"
                            )
                            if not locs:
                                teasers = sp3.select(
                                    "ul.Directory-listTeasers li.Directory-listTeaser a.Teaser-titleLink"
                                )
                                if not teasers:
                                    for entity in _entities(sp3, city_url):
                                        yield parse_data(entity, city_url)
                                else:
                                    logger.info(
                                        f"[{city.text}] [teaser] {len(teasers)} found"
                                    )
                                    for teaser in teasers:
                                        teaser_url = urljoin(
                                            locator_domain, teaser["href"]
                                        )
                                        sp3_1 = bs(
                                            session.get(
                                                teaser_url, headers=_headers
                                            ).text,
                                            "lxml",
                                        )
                                        for entity in _entities(sp3_1, teaser_url):
                                            yield parse_data(entity, teaser_url)
                            else:
                                logger.info(f"[{city.text}] [locs] {len(locs)} found")
                                for loc in locs:
                                    loc_url = urljoin(locator_domain, loc["href"])
                                    sp4 = bs(
                                        session.get(loc_url, headers=_headers).text,
                                        "lxml",
                                    )
                                    for entity in _entities(sp4, loc_url):
                                        yield parse_data(entity, loc_url)


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
