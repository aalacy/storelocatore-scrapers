import re
import json
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgzip.dynamic import SearchableCountries
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

logger = SgLogSetup().get_logger("jdsports_co_ul")


class ScrapableSite:
    def __init__(self, domain, country_code):
        self.locator_domain = domain
        self.stores_url = f"https://www.{domain}/store-locator/all-stores/"
        self.country_code = country_code
        self.store_css_selector = ".storeCard"
        self.session = None

    def get_session(self, refresh):
        if not self.session or refresh:
            self.session = SgChrome(is_headless=True).driver()
            self.session.set_page_load_timeout(30)

        return self.session

    def get_locations(self, retry=0):
        try:
            session = self.get_session(retry)
            session.get(self.stores_url)
            soup = bs(session.page_source, "html.parser")

            locations = [
                f'https://www.{self.locator_domain}{a["href"]}'
                for a in soup.select(self.store_css_selector)
            ]

            if not len(locations):
                raise Exception(f"Unable to fetch locations for {self.country_code}")

            return locations
        except Exception as e:
            if retry < 3:
                return self.get_locations(retry + 1)

            raise e

    def get_data(self, url, retry=0):
        try:
            session = self.get_session(retry)
            session.get(url)
            soup = bs(session.page_source, "html.parser")
            script = soup.find("script", type="application/ld+json")

            return json.loads(re.sub(r"\t", "", script.string))
        except Exception as e:
            if retry < 3:
                return self.get_data(url, retry + 1)

            raise Exception(f"Unable to fetch {url}: {e}")


sites = [
    ScrapableSite("jdsports.co.uk", SearchableCountries.BRITAIN),
    ScrapableSite("jdsports.es", SearchableCountries.SPAIN),
    ScrapableSite("jdsports.se", SearchableCountries.SWEDEN),
    ScrapableSite("jdsports.be", SearchableCountries.BELGIUM),
    ScrapableSite("jd-sports.com.au", SearchableCountries.AUSTRALIA),
    ScrapableSite("jdsports.de", SearchableCountries.GERMANY),
    ScrapableSite("jdsports.dk", SearchableCountries.DENMARK),
    ScrapableSite("jdsports.com.sg", SearchableCountries.SINGAPORE),
    ScrapableSite("jdsports.fr", SearchableCountries.FRANCE),
    ScrapableSite("jdsports.fi", SearchableCountries.FINLAND),
    ScrapableSite("jdsports.my", SearchableCountries.MALAYSIA),
    ScrapableSite("jdsports.it", SearchableCountries.ITALY),
    ScrapableSite("jdsports.nl", SearchableCountries.NETHERLANDS),
    ScrapableSite("jdsports.co.th", SearchableCountries.THAILAND),
    ScrapableSite("jdsports.at", SearchableCountries.AUSTRIA),
    ScrapableSite("jdsports.pt", SearchableCountries.PORTUGAL),
    ScrapableSite("jdsports.co.nz", SearchableCountries.NEW_ZEALAND),
]


def format_hours(hours):
    data = []
    for hour in hours:
        data.append(f'{hour["dayOfWeek"]}: {hour["opens"]}-{hour["closes"]}')

    return ", ".join(data)


def fetch_data():
    pois = []

    for site in sites:
        count = 0
        locations = site.get_locations()
        for location in locations:
            data = site.get_data(location)

            count += 1
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


def scrape():
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for row in fetch_data():
            writer.write_row(row)


scrape()
