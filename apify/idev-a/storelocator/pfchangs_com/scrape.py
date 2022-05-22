from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
from urllib.parse import urljoin
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("pfchangs")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.pfchangs.com/"
base_url = "https://www.pfchangs.com/locations/us.html"
locator_url = "https://www.pfchangs.com/locations/"


def _entities(sp, url):
    try:
        return json.loads(sp.select_one("script#js-map-config-dir-map").string.strip())[
            "entities"
        ]
    except:
        logger.info(url)
        return []


def _url(url):
    if url.startswith("../"):
        url = url[3:]
    if url.startswith("../"):
        url = url[3:]
    return urljoin(locator_url, url)


def parse_data(entity, page_url):
    _ = entity["profile"]
    street_address = _["address"]["line1"]
    if _["address"]["line2"]:
        street_address += " " + _["address"]["line2"]
    if _["address"]["line3"]:
        street_address += " " + _["address"]["line3"]
    latitude = longitude = ""
    if "cityCoordinate" in _:
        latitude = _["cityCoordinate"]["lat"]
        longitude = _["cityCoordinate"]["long"]
    elif "geocodedCoordinate" in _:
        latitude = _["geocodedCoordinate"]["lat"]
        longitude = _["geocodedCoordinate"]["long"]
    hours = []
    for hh in _.get("hours", {}).get("normalHours", []):
        times = "closed"
        if not hh["isClosed"]:
            times = f"{hh['intervals'][0]['start']}-{hh['intervals'][0]['end']}"
        hours.append(f"{hh['day']}: {times}")
    location_type = ""
    if "temporary closed" in _.get("additionalHoursText", ""):
        location_type = "Temporary closed"
    if "c_locationPageMetaTitle" in _:
        location_name = _["c_locationPageMetaTitle"]
    elif "c_geomodifier" in _:
        location_name = _["c_geomodifier"]
    elif "geomodifier" in _:
        location_name = _["geomodifier"]
    else:
        location_name = _["address"]["line1"]

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
        sp1 = bs(session.get(base_url, headers=_headers).text, "lxml")
        states = sp1.select("ul.Directory-listLinks li.Directory-listItem a")
        logger.info(f"[states] {len(states)} found")
        for state in states:
            state_url = _url(state["href"])
            sp2 = bs(session.get(state_url, headers=_headers).text, "lxml")
            cities = sp2.select("ul.Directory-listLinks li.Directory-listItem a")
            if not cities:
                teasers = sp2.select(
                    "ul.Directory-listTeasers li.Directory-listTeaser a.Teaser-titleLink"
                )
                if not teasers:
                    for entity in _entities(sp2, state_url):
                        yield parse_data(entity, state_url)
                else:
                    logger.info(f"[{state.text}] [teaser] {len(teasers)} found")
                    for teaser in teasers:
                        teaser_url = _url(teaser["href"])
                        sp2_1 = bs(
                            session.get(teaser_url, headers=_headers).text,
                            "lxml",
                        )
                        for entity in _entities(sp2_1, teaser_url):
                            yield parse_data(entity, teaser_url)
            else:
                logger.info(f"[{state.text}] [city] {len(cities)} found")
                for city in cities:
                    city_url = _url(city["href"])
                    sp3 = bs(session.get(city_url, headers=_headers).text, "lxml")
                    locs = sp3.select("ul.Directory-listLinks li.Directory-listItem a")
                    if not locs:
                        teasers = sp3.select(
                            "ul.Directory-listTeasers li.Directory-listTeaser a.Teaser-titleLink"
                        )
                        if not teasers:
                            for entity in _entities(sp3, city_url):
                                yield parse_data(entity, city_url)
                        else:
                            logger.info(f"[{city.text}] [teaser] {len(teasers)} found")
                            for teaser in teasers:
                                teaser_url = _url(teaser["href"])
                                sp3_1 = bs(
                                    session.get(teaser_url, headers=_headers).text,
                                    "lxml",
                                )
                                for entity in _entities(sp3_1, teaser_url):
                                    yield parse_data(entity, teaser_url)
                    else:
                        logger.info(f"[{city.text}] [locs] {len(locs)} found")
                        for loc in locs:
                            loc_url = _url(loc["href"])
                            sp4 = bs(
                                session.get(loc_url, headers=_headers).text,
                                "lxml",
                            )
                            for entity in _entities(sp4, loc_url):
                                yield parse_data(entity, loc_url)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
