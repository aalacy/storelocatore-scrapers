from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def get_driver(url, class_name, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()
            driver.get(url)

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            break
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


def get_data():
    days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    url = "https://www.dreamdoors.co.uk/kitchen-showrooms"
    class_name = "empty"

    driver = get_driver(url, class_name)
    response = driver.page_source
    soup = bs(response, "html.parser")

    li_tags = soup.find_all("li", attrs={"class": "empty"})

    page_urls = []
    for li_tag in li_tags:
        a_tags = li_tag.find_all("a")

        for a_tag in a_tags:
            page_urls.append(a_tag["href"].strip())

    for page_url in page_urls:
        if " " in page_url:
            continue

        try:
            driver = get_driver(page_url, "gm-style", driver=driver)
            response = driver.page_source

            lat_lon_part = response.split(
                "https://maps.googleapis.com/maps/api/js/ViewportInfoService.GetViewportInfo"
            )[1]
            latitude = lat_lon_part.split(";1d")[1].split(";2d")[0]
            longitude = lat_lon_part.split(";2d")[1].split("&")[0]

        except Exception:
            driver = get_driver(page_url, "moduletable", driver=driver)
            response = driver.page_source
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        soup = bs(response, "html.parser")

        locator_domain = "https://www.dreamdoors.co.uk/"
        location_name = soup.find("h1").text.strip()
        address_parts = (
            soup.find("div", attrs={"class": "address"})
            .get_text(strip=True, separator="\n")
            .splitlines()[1:]
        )
        address = address_parts[0]
        zipp = address_parts[-1]

        if len(address_parts) == 3:
            city = address_parts[-2]
            state = "<MISSING>"

        if len(address_parts) == 4:
            city = address_parts[-3]
            state = address_parts[-2]

        if len(address_parts) > 4:
            address = address + " " + address_parts[1]
            city = address_parts[-3]
            state = address_parts[-2]

        phone = (
            soup.find("div", attrs={"class": "telephone"})
            .find("a")["href"]
            .replace("tel:", "")
        )
        location_type = "<MISSING>"
        country_code = "UK"
        times = soup.find_all("span", attrs={"class": "time"})

        y = 0
        hours = ""
        for time_part in times:
            day = days[y]
            y = y + 1
            time = time_part.text.strip()
            hours = hours + day + " " + time + ", "
        hours = hours[:-2]

        if "coming soon" in address.lower():
            continue

        if city == "Springkerse Industrial Estate":
            address = address + " " + city
            city = state
            state = "<MISSING>"

        store_number = "<LATER>"
        yield {
            "locator_domain": locator_domain,
            "page_url": page_url,
            "location_name": location_name,
            "latitude": latitude,
            "longitude": longitude,
            "city": city,
            "store_number": store_number,
            "street_address": address,
            "state": state,
            "zip": zipp,
            "phone": phone,
            "location_type": location_type,
            "hours": hours,
            "country_code": country_code,
        }

    driver.quit()


def scrape():

    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"], part_of_record_identity=True),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"], is_required=False),
        longitude=sp.MappingField(mapping=["longitude"], is_required=False),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"]),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["store_number"], part_of_record_identity=True
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"], is_required=False),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=get_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )
    pipeline.run()


scrape()
