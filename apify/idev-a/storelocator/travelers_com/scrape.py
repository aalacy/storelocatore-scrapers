from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from urllib.parse import urljoin
import math
from concurrent.futures import ThreadPoolExecutor

logger = SgLogSetup().get_logger("travelers")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
session = SgRequests(proxy_rotation_failure_threshold=10).requests_retry_session()

max_workers = 24


def fetchConcurrentSingle(data):
    response = request_with_retries(data)
    return data, bs(response.text, "lxml"), response.text


def fetchConcurrentList(list, occurrence=max_workers):
    output = []
    total = len(list)
    reminder = math.floor(total / 50)
    if reminder < occurrence:
        reminder = occurrence

    count = 0
    with ThreadPoolExecutor(
        max_workers=occurrence, thread_name_prefix="fetcher"
    ) as executor:
        for result in executor.map(fetchConcurrentSingle, list):
            count = count + 1
            if count % reminder == 0:
                logger.debug(f"Concurrent Operation count = {count}")
            output.append(result)
    return output


def request_with_retries(url):
    return session.get(url, headers=_headers)


def fetch_data():
    locator_domain = "https://www.travelers.com/"
    base_url = "https://agent.travelers.com/"
    with SgRequests(proxy_rotation_failure_threshold=10) as session:
        states = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "li.Directory-listItem a"
        )
        logger.info(f"{len(states)} found")
        for state in states:
            state_url = base_url + state["href"]
            cities = bs(session.get(state_url, headers=_headers).text, "lxml").select(
                "li.Directory-listItem a"
            )
            for city in cities:
                city_url = base_url + city["href"]
                logger.info(f"[{state.text}] {city_url}")
                sp0 = bs(session.get(city_url, headers=_headers).text, "lxml")
                locations = []
                for _ in sp0.select("li.Directory-listTeaser"):
                    if _.select_one("a.Teaser-titleLink"):
                        locations.append(
                            urljoin(
                                base_url, _.select_one("a.Teaser-titleLink")["href"]
                            )
                        )

                if locations:
                    for page_url, sp1, res in fetchConcurrentList(locations):
                        logger.info(f"[{state.text}] [{city.text}] {page_url}")
                        street_address = sp1.select_one(".c-address-street-1").text
                        if sp1.select_one(".c-address-street-2"):
                            street_address += (
                                " " + sp1.select_one(".c-address-street-2").text
                            )
                        zip_postal = ""
                        if sp1.select_one(".c-address-postal-code"):
                            zip_postal = sp1.select_one(".c-address-postal-code").text
                        phone = ""
                        if sp1.select_one("#phone-main"):
                            phone = sp1.select_one("#phone-main").text.strip()
                        coord = sp1.select_one('meta[name="geo.position"]')[
                            "content"
                        ].split(";")

                        yield SgRecord(
                            page_url=page_url,
                            store_number=res.split('{"ids":')[1]
                            .split(',"pageSetId"')[0]
                            .strip(),
                            location_name=sp1.select_one("h1.Core-name").text.strip(),
                            street_address=street_address,
                            city=city.text.strip(),
                            state=state.text.strip(),
                            zip_postal=zip_postal,
                            country_code="us",
                            phone=phone,
                            latitude=coord[0],
                            longitude=coord[1],
                            locator_domain=locator_domain,
                        )
                else:
                    locations = sp0.select(
                        "ul.Directory-listTeasers li.Directory-listTeaser"
                    )
                    for _ in locations:
                        street_address = _.select_one(".c-address-street-1").text
                        if _.select_one(".c-address-street-2"):
                            street_address += (
                                " " + _.select_one(".c-address-street-2").text
                            )
                        zip_postal = ""
                        if _.select_one(".c-address-postal-code"):
                            zip_postal = _.select_one(".c-address-postal-code").text
                        phone = ""
                        if _.select_one("#phone-main"):
                            phone = _.select_one("#phone-main").text.strip()
                        yield SgRecord(
                            page_url=city_url,
                            location_name=_.h2.text.strip(),
                            street_address=street_address,
                            city=city.text.strip(),
                            state=state.text.strip(),
                            zip_postal=zip_postal,
                            country_code="US",
                            phone=phone,
                            locator_domain=locator_domain,
                        )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
