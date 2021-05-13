import re
import csv
import json
from bs4 import BeautifulSoup as bs
from datetime import datetime
from sglogging import SgLogSetup
from sgselenium.sgselenium import SgChrome
from selenium import webdriver  # noqa
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium_stealth import stealth

logger = SgLogSetup().get_logger("napaonline_com")

addresses = []
base_url = "https://www.napaonline.com"


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


def get(url, driver):
    return driver.execute_async_script(
        f"""
        var done = arguments[0]
        fetch("{url}")
            .then(res => res.text())
            .then(done)
    """
    )


def crawl_state_url(state_url, driver):
    city_urls = []
    html = get(state_url, driver)
    state_soup = bs(html, "lxml")
    for url in state_soup.find("div", {"class": "store-browse-content"}).find_all("a"):
        city_urls.append(url)
    return city_urls


def scrape_json(data, page_url):
    location_name = data["name"]
    street_address = data["address"]["streetAddress"]
    city = data["address"]["addressLocality"]
    state = data["address"]["addressRegion"]
    zipp = data["address"]["postalCode"]
    country_code = data["address"]["addressCountry"]
    store_number = data["@id"]
    try:
        phone = data["telephone"]
    except:
        phone = "<MISSING>"
    location_type = data["@type"]
    latitude = data["geo"]["latitude"]
    longitude = data["geo"]["longitude"]
    hours = ""
    for hr in data["openingHoursSpecification"]:
        if hours != "":
            hours += ", "
        hours += " " + hr["dayOfWeek"][0]
        if hr["opens"] == "00:00:00" and hr["closes"] == "00:00:00":
            hours += " Closed"
        else:
            hours += (
                " "
                + datetime.strptime(hr["opens"], "%H:%M:%S").strftime("%I:%M %p")
                + " - "
                + datetime.strptime(hr["closes"], "%H:%M:%S").strftime("%I:%M %p")
                + " "
            )

    store = [
        base_url,
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
        str(x).encode("ascii", "ignore").decode("ascii").strip() if x else "<MISSING>"
        for x in store
    ]
    return store


def scrape_store_number(soup):
    html_content = str(soup)
    match = re.search(r"\[\"entityId\"\] = \"(\d+?)\"", html_content)
    return match.group(1) if match else "<MISSING>"


def get_store_key(store):
    # use the page_url as unique key
    return f"{store[-1]}".lower()


def scrape_html(soup, page_url):
    name_elem = soup.find(id="location-name")
    location_name = name_elem.text if name_elem else "<MISSING>"

    addr_elem = soup.find(itemprop="streetAddress")
    street_address = addr_elem["content"] if addr_elem else "<MISSING>"

    city_elem = soup.find(itemprop="addressLocality")
    city = city_elem["content"] if city_elem else "<MISSING>"

    state_elem = soup.find(itemprop="addressRegion")
    state = state_elem.text if state_elem else "<MISSING>"

    zipp_elem = soup.find(itemprop="postalCode")
    zipp = zipp_elem.text if zipp_elem else "<MISSING>"

    country_elem = soup.find(itemprop="addressCountry")
    country_code = country_elem.text if country_elem else "<MISSING>"

    phone_elem = soup.find(itemprop="telephone")
    phone = phone_elem.text if phone_elem else "<MISSING>"

    main_elem = soup.find(id="main")
    location_type = (
        main_elem["itemtype"].replace("http://schema.org/", "")
        if main_elem
        else "<MISSING>"
    )

    lat_elem = soup.find(itemprop="latitude")
    latitude = lat_elem["content"] if lat_elem else "<MISSING>"

    lng_elem = soup.find(itemprop="longitude")
    longitude = lng_elem["content"] if lng_elem else "<MISSING>"

    hours = ""
    hours_table = soup.find(class_="c-hours-details")
    if hours_table:
        hours = " ".join(list(hours_table.find("tbody").stripped_strings))
        hours = re.sub("PM ", "PM, ", hours)

    store_number = scrape_store_number(soup)

    store = [
        base_url,
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
        str(x).encode("ascii", "ignore").decode("ascii").strip() if x else "<MISSING>"
        for x in store
    ]

    return store


def scrape_one_in_city(url, driver):
    link_url = base_url + url["href"]
    html = get(link_url, driver)
    soup = bs(html, "lxml")

    # make sure we're on a store detail page and not a listing page ...
    #   we got here by looking for "(1)" in the url link, but sometimes these links are lying
    #   and we end up at a page with multiple stores instead of one
    is_detail_page = soup.find(class_="store-browse-content-listing") is None
    if not is_detail_page:
        logger.info(
            f"expected store detail page but found multiple store listings on {link_url}"
        )
        return scrape_multiple_in_city(url, driver)

    data = None
    try:
        data = json.loads(
            soup.find(
                lambda tag: (tag.name == "script" and '"streetAddress"' in tag.text)
            ).text
        )
    except:
        logger.info(f">>> json data not found for {link_url} ... scraping html instead")

    if data:
        store = scrape_json(
            data, link_url
        )  # use the final url as page_url in case of redirect
    else:
        store = scrape_html(soup, link_url)

    store_key = get_store_key(store)
    if store_key in addresses:
        return None
    addresses.append(store_key)
    return [store]


def scrape_multiple_in_city(url, driver):
    stores = []
    html = get(base_url + url["href"], driver)
    if not html:
        return stores
    soup = bs(html, "lxml")
    for link in soup.find_all("div", {"class": "store-browse-store-detail"}):

        link_url = base_url + link.a["href"].replace("https://www.napaonline.com", "")
        html = get(link_url, driver)
        soup = bs(html, "lxml")

        data = None
        try:
            data = json.loads(
                soup.find(
                    lambda tag: (tag.name == "script" and '"streetAddress"' in tag.text)
                ).text
            )
        except:
            logger.info(f">>> json data not found for {link_url}")

        if data:
            store = scrape_json(
                data, link_url
            )  # use the final url as page_url in case of redirect
        else:
            store = scrape_html(soup, link_url)

        store_key = get_store_key(store)
        if store_key in addresses:
            continue
        addresses.append(store_key)
        stores.append(store)
    return stores


def crawl_city_url(url, driver):
    # the url argument is of type bs4.element.Tag
    if "(1)" in url.text:
        return scrape_one_in_city(url, driver)
    else:
        return scrape_multiple_in_city(url, driver)


def get_driver():
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
    sgchrome = SgChrome(is_headless=True, user_agent=user_agent)
    chrome_options = webdriver.ChromeOptions()
    sgchrome._SgSelenium__add_common_args(chrome_options, user_agent)
    sgchrome._SgSelenium__add_chrome_arguments(chrome_options, user_agent)

    seleniumwire_options = sgchrome.set_proxy_options()
    seleniumwire_options["auto_config"] = False

    chrome = webdriver.Chrome(
        executable_path=ChromeDriverManager().install(),
        chrome_options=chrome_options,
        seleniumwire_options=seleniumwire_options,
    )
    sgchrome._SgSelenium__configure_chromedriver(chrome, user_agent)

    stealth(
        chrome,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    return chrome


def load_initial_page(driver):
    driver.get("https://www.napaonline.com")
    driver.execute_script('window.open("https://www.napaonline.com")')

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "header-branding-logo"))
        )
    except:
        raise Exception()


def fetch_data():
    state_urls = []
    city_urls = []

    with get_driver() as driver:
        load_initial_page(driver)

        html = get("https://www.napaonline.com/en/auto-parts-stores-near-me", driver)
        soup = bs(html, "lxml")

        for link in soup.find("div", {"class": "store-browse-content"}).find_all("a"):
            logger.info(base_url + link["href"])
            state_urls.append(base_url + link["href"])

        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(crawl_state_url, url, driver) for url in state_urls
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

        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(crawl_city_url, url, driver) for url in city_urls
            ]
            for result in as_completed(futures):
                locations = result.result()
                if locations:
                    for store in locations:
                        yield store


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
