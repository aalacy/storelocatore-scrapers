import os
import re
import csv
import json
import threading
from time import sleep
from random import randint
from bs4 import BeautifulSoup as bs
from datetime import datetime as dt
from sglogging import SgLogSetup
from sgselenium.sgselenium import SgChrome
from concurrent.futures import ThreadPoolExecutor, as_completed

from tenacity import retry, stop_after_attempt

logger = SgLogSetup().get_logger("napaonline_com")

addresses = []
base_url = "https://www.napaonline.com/stores"

local = threading.local()


def get_driver():
    if not hasattr(local, "driver"):
        local.driver = SgChrome(seleniumwire_auto_config=False).driver()
        load_initial_page(local.driver)

    return local.driver


class PageConfig:
    def __init__(
        self,
        name,
        base_url,
        location_path,
        directory_page_selector,
        details_link_selector,
        dedup_tracker,
        initial_page="",
    ):
        self.name = name
        self.base_url = base_url.strip("/")
        self.location_path = location_path.strip("/")
        self.initial_page = initial_page.strip("/") or self.location_path
        self.directory_page_selector = directory_page_selector
        self.details_link_selector = details_link_selector
        self.dedup_tracker = dedup_tracker

    def has_multiple_locations(self, link):
        if link.has_attr("data-count"):
            return "(1)" not in link.attrs["data-count"]

        return "(1)" not in link.text

    def is_directory_page(self, soup):
        return soup.find(class_=self.directory_page_selector) is not None

    def get_next_url(self, path):
        next_path = self.clean_path(path)

        if self.__is_from_root__(next_path):
            return os.path.join(self.base_url, next_path)

        return os.path.join(self.get_base_location_url(), next_path)

    def get_state_links(self, soup):
        return soup.select(self.directory_page_selector)

    def get_city_links(self, soup):
        return soup.select(self.directory_page_selector)

    def get_details_links(self, soup):
        return soup.select(self.details_link_selector)

    def get_tracking_id(self, store):
        # use the store_number as unique key
        return f"{store[7]}".lower()

    def track_location(self, id):
        return self.dedup_tracker.append(id)

    def is_location_tracked(self, id):
        return id in self.dedup_tracker

    def get_base_location_url(self):
        return os.path.join(self.base_url, self.location_path)

    def get_initial_page(self):
        return os.path.join(self.base_url, self.initial_page)

    def clean_path(self, path):
        return re.sub(
            f"{self.base_url}|{self.location_path}(?!-)|\\.\\.", "", path
        ).strip("/")

    def __is_from_root__(self, path):
        return "stores/" in path or "en/auto-parts-stores-near-me" in path


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch(url, driver):
    sleep(randint(2, 3))
    return driver.execute_async_script(
        f"""
        var done = arguments[0]
        fetch("{url}")
            .then(res => res.text())
            .then(done)
    """
    )


def scrape_store_number(soup):
    html_content = str(soup)
    match = re.search(r"\[\"entityId\"\] = \"(\d+?)\"", html_content)
    return match.group(1) if match else None


def get_store_key(store):
    # use the store_number as unique key
    return f"{store[7]}".lower()


def get_details(soup):
    for tag in soup.find_all("script", type="application/ld+json"):
        if "BreadcrumbList" not in tag.string:
            return json.loads(tag.string)
    return {}


MISSING = "<MISSING>"


def get(entity, key, default=MISSING):
    return entity.get(key, default)


def scrape_html(soup, page_url):
    try:
        details = get_details(soup)

        name_elem = soup.find(id="location-name")
        location_name = name_elem.text if name_elem else get(details, "name")

        address = get(details, "address", {})
        addr_elem = soup.find(itemprop="streetAddress")
        street_address = (
            addr_elem["content"] if addr_elem else get(address, "streetAddress")
        )

        if location_name == MISSING and street_address == MISSING:
            return None

        city_elem = soup.find(itemprop="addressLocality")
        city = city_elem["content"] if city_elem else get(address, "addressLocality")

        state_elem = soup.find(itemprop="addressRegion")
        state = state_elem.text if state_elem else get(address, "addressRegion")

        zipp_elem = soup.find(itemprop="postalCode")
        zipp = zipp_elem.text if zipp_elem else get(address, "postalCode")

        country_elem = soup.find(itemprop="addressCountry")
        country_code = (
            country_elem.text if country_elem else get(address, "addressCountry")
        )

        phone_elem = soup.find(itemprop="telephone")
        phone = phone_elem.text if phone_elem else get(details, "telephone")

        location_type = None
        main = soup.select_one("#main")
        if main and main.has_attr("itemtype"):
            location_type = re.sub(
                "http://schema.org/",
                "",
                main["itemtype"],
            )

        if not location_type:
            location_type = get(details, "@type", MISSING)

        geo = get(details, "geo", {})
        lat_elem = soup.find(itemprop="latitude")
        latitude = lat_elem["content"] if lat_elem else get(geo, "latitude")

        lng_elem = soup.find(itemprop="longitude")
        longitude = lng_elem["content"] if lng_elem else get(geo, "longitude")

        hours = ""
        hours_table = soup.find(class_="c-hours-details")
        if hours_table:
            hours = " ".join(list(hours_table.find("tbody").stripped_strings))
            hours = re.sub("PM ", "PM, ", hours)
        else:
            hours = ", ".join(
                f'{day["dayOfWeek"][0]}: {day["opens"]}-{day["closes"]}'
                for day in get(details, "openingHoursSpecification", [])
            )
            if not hours:
                hours = MISSING

        store_number = scrape_store_number(soup) or get(details, "@id")

        store = [
            "napaonline.com",
            location_name,
            street_address,
            city,
            state,
            zipp,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours.strip(),
            page_url,
        ]
        store = [
            str(x).encode("ascii", "ignore").decode("ascii").strip()
            if x
            else "<MISSING>"
            for x in store
        ]

        return store
    except Exception as e:
        logger.error(e)


def scrape_one_in_city(url, page, driver):
    link_url = page.get_next_url(url["href"])
    html = fetch(link_url, driver)
    soup = bs(html, "lxml")

    # make sure we're on a store detail page and not a listing page ...
    #   we got here by looking for "(1)" in the url link, but sometimes these links are lying
    #   and we end up at a page with multiple stores instead of one
    is_directory_page = page.is_directory_page(soup)
    if is_directory_page:
        return scrape_multiple_in_city(url, page, driver)

    store = scrape_html(soup, link_url)

    if not store:
        return []

    id = page.get_tracking_id(store)
    if page.is_location_tracked(id):
        return []

    page.track_location(id)
    return [store]


@retry(stop=stop_after_attempt(3), reraise=True)
def scrape_multiple_in_city(url, page, driver):
    stores = []
    link_url = page.get_next_url(url["href"])
    html = fetch(link_url, driver)
    if not html:
        return stores
    soup = bs(html, "lxml")

    for link in page.get_details_links(soup):
        locations_link_url = page.get_next_url(link["href"])
        html = fetch(locations_link_url, driver)
        soup = bs(html, "lxml")

        store = scrape_html(soup, locations_link_url)
        if not store:
            continue

        id = page.get_tracking_id(store)
        if page.is_location_tracked(id):
            continue

        page.track_location(id)

        stores.append(store)

    if not len(stores):
        logger.error(f"unable to scrape multiple locations: {link_url}")

    return stores


def crawl_state_url(link, page):
    driver = get_driver()
    state_url = page.get_next_url(link["href"])
    html = fetch(state_url, driver)
    soup = bs(html, "lxml")
    return page.get_city_links(soup)


def crawl_city_url(url, page):
    driver = get_driver()

    # the url argument is of type bs4.element.Tag
    if page.has_multiple_locations(url):
        return scrape_multiple_in_city(url, page, driver)
    else:
        return scrape_one_in_city(url, page, driver)


@retry(stop=stop_after_attempt(3), reraise=True)
def load_initial_page(driver):
    driver.get("https://www.napaonline.com")
    driver.execute_script('window.open("https://www.napaonline.com")')
    sleep(15)


def fetch_data():
    tracker = []

    stores_config = PageConfig(
        name="stores",
        base_url="https://www.napaonline.com",
        initial_page="/stores/index.html",
        location_path="/stores",
        directory_page_selector=".Directory-content a",
        details_link_selector=".Teaser-titleLink",
        dedup_tracker=tracker,
    )

    near_me_config = PageConfig(
        name="auto parts",
        base_url="https://www.napaonline.com",
        location_path="/en/auto-parts-stores-near-me",
        directory_page_selector=".store-browse-content a",
        details_link_selector=".store-browse-store-detail .store-listing-title:first-child",
        dedup_tracker=tracker,
    )

    with ThreadPoolExecutor() as executor, get_driver() as driver:
        for page in (near_me_config, stores_config):
            count = 0
            state_urls = []
            city_urls = []
            html = fetch(page.get_initial_page(), driver)
            soup = bs(html, "lxml")

            state_urls = page.get_state_links(soup)

            futures = [
                executor.submit(crawl_state_url, url, page) for url in state_urls
            ]
            # return when all finished or after 20 min regardless
            for result in as_completed(futures):
                try:
                    cities_in_state = result.result()
                    city_urls.extend(cities_in_state)
                except Exception as ex:
                    logger.info(
                        f"crawl_state_url with result {result} threw exception: {ex}"
                    )

            logger.info(f"found {len(city_urls)} city urls")

            futures = [executor.submit(crawl_city_url, url, page) for url in city_urls]

            for result in as_completed(futures):
                locations = result.result()
                if locations:
                    for store in locations:
                        count += 1
                        yield store

            logger.info(f"{page.name}: {count}")


def scrape():
    now = dt.now()
    data = fetch_data()
    write_output(data)
    logger.info(f"duration: {dt.now() - now}")


if __name__ == "__main__":
    scrape()
