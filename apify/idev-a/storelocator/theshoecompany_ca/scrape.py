from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from urllib.parse import urljoin

logger = SgLogSetup().get_logger("theshoecompany")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.theshoecompany.ca"
base_url = "https://stores.theshoecompany.ca/"


def _d(page_url, session):
    sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
    logger.info(page_url)
    street_address = sp1.select_one("span.c-address-street-1").text.strip()
    if sp1.select_one("span.c-address-street-2"):
        street_address += " " + sp1.select_one("span.c-address-street-2").text.strip()
    hours = [hh["content"] for hh in sp1.select("table.c-hours-details tbody tr")]
    try:
        latitude = (
            sp1.select_one("div.c-uber a")["href"]
            .split("latitude%5D=")[1]
            .split("&")[0]
        )
        longitude = (
            sp1.select_one("div.c-uber a")["href"]
            .split("longitude%5D=")[1]
            .split("&")[0]
        )
    except:
        latitude = longitude = ""

    phone = ""
    if sp1.select_one("div#phone-main"):
        phone = sp1.select_one("div#phone-main").text.strip()
    return SgRecord(
        page_url=page_url,
        location_name=sp1.select_one(
            "span#location-name span.LocationName-geo"
        ).text.strip(),
        street_address=street_address,
        city=sp1.select_one("span.c-address-city").text.strip(),
        state=sp1.select_one(".c-address-state").text.strip(),
        zip_postal=sp1.select_one(".c-address-postal-code").text.strip(),
        country_code=sp1.select_one(".c-address-country-name").text.strip(),
        phone=phone,
        locator_domain=locator_domain,
        location_type=sp1.select_one(
            "span#location-name span.LocationName-brand"
        ).text.strip(),
        latitude=latitude,
        longitude=longitude,
        hours_of_operation="; ".join(hours).replace("–", "-"),
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        states = soup.select("ul.Directory-listLinks a")
        logger.info(f"{len(states)} found")
        for state in states:
            state_url = urljoin(base_url, state["href"])
            cities = bs(session.get(state_url, headers=_headers).text, "lxml").select(
                "ul.Directory-listLinks a"
            )
            for city in cities:
                city_url = urljoin(base_url, city["href"])
                locations = bs(
                    session.get(city_url, headers=_headers).text, "lxml"
                ).select("ul.Directory-listTeasers a")
                if not locations:
                    yield _d(city_url, session)
                for _ in locations:
                    page_url = urljoin(base_url, _["href"])
                    yield _d(page_url, session)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
