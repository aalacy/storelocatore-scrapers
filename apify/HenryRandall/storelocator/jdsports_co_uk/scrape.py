from asyncio import as_completed
from concurrent.futures import ThreadPoolExecutor
import re
import json
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgzip.dynamic import SearchableCountries
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


class ScrapableSite:
    def __init__(self, domain, country_code):
        self.locator_domain = domain
        self.stores_url = f"https://www.{domain}/store-locator/all-stores/"
        self.country_code = country_code
        self.store_css_selector = ".storeCard"

    def get_session(self):
        session = SgChrome(is_headless=False).driver()
        session.set_page_load_timeout(30)

        return session

    def refresh_session(self, session):
        session.refresh()

    def get_locations(self, session, retry=0):
        try:
            session.get(self.stores_url)
            session.refresh()
            soup = bs(session.page_source, "html.parser")

            return [
                f'https://www.{self.locator_domain}{a["href"]}'
                for a in soup.select(self.store_css_selector)
            ]
        except:
            if retry < 3:
                return self.get_locations(session, retry + 1)

    def get_data(self, url, session, retry=0):
        try:
            session.get(url)
            soup = bs(session.page_source, "html.parser")
            script = soup.find("script", type="application/ld+json")

            return json.loads(re.sub(r"\t", "", script.string))
        except Exception as e:
            self.refresh_session()
            if retry < 3:
                return self.get_data(url, session, retry + 1)

            raise Exception(f"Unable to fetch {url}: {e}")


sites = [
    ["jdsports.co.uk", SearchableCountries.BRITAIN],
    ["jdsports.es", SearchableCountries.SPAIN],
    ["jdsports.se", SearchableCountries.SWEDEN],
    ["jdsports.be", SearchableCountries.BELGIUM],
    ["jd-sports.com.au", SearchableCountries.AUSTRALIA],
    ["jdsports.de", SearchableCountries.GERMANY],
    ["jdsports.dk", SearchableCountries.DENMARK],
    ["jdsports.com.sg", SearchableCountries.SINGAPORE],
    ["jdsports.fr", SearchableCountries.FRANCE],
    ["jdsports.fi", SearchableCountries.FINLAND],
    ["jdsports.my", SearchableCountries.MALAYSIA],
    ["jdsports.it", SearchableCountries.ITALY],
    ["jdsports.nl", SearchableCountries.NETHERLANDS],
    ["jdsports.co.th", SearchableCountries.THAILAND],
    ["jdsports.at", SearchableCountries.AUSTRIA],
    ["jdsports.pt", SearchableCountries.PORTUGAL],
    ["jdsports.co.nz", SearchableCountries.NEW_ZEALAND],
]


def format_hours(hours):
    data = []
    for hour in hours:
        data.append(f'{hour["dayOfWeek"]}: {hour["opens"]}-{hour["closes"]}')

    return ", ".join(data)


def fetch_locations(country):
    site = ScrapableSite(*country)
    pois = []
    with site.get_session() as driver:
        locations = site.get_locations(driver)
        for location in locations:
            data = site.get_data(location, driver)

            pois.append(
                SgRecord(
                    page_url=data.get("url"),
                    location_name=data.get("name"),
                    street_address=data["address"]["streetAddress"],
                    city=data["address"]["addressLocality"],
                    state=data["address"]["addressRegion"],
                    country_code=site.country_code,
                    zip_postal=data["address"]["postalCode"],
                    store_number=re.sub(
                        f"https://www.{site.locator_domain}/", "", data["@id"]
                    ),
                    phone=data["telephone"],
                    latitude=data["geo"]["latitude"],
                    longitude=data["geo"]["longitude"],
                    locator_domain=site.locator_domain,
                    hours_of_operation=format_hours(data["openingHoursSpecification"]),
                )
            )

        return pois


def fetch_data():
    pois = []

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_locations, site) for site in sites]
        for future in as_completed(futures):
            pois.extend(future.result())

    return pois


def scrape():
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        for row in fetch_data():
            writer.write_row(row)


scrape()
