from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sgscrape.pause_resume import CrawlStateSingleton, SerializableRequest
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
crawl_state = CrawlStateSingleton.get_instance()


def get_driver(url, class_name):
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


def get_urls():
    url = "https://www.onemainfinancial.com/branches"
    class_name = "state-list-column"
    driver = get_driver(url, class_name)
    response = driver.page_source

    state_soup = bs(response, "html.parser")

    state_list_columns = state_soup.find_all("ul", attrs={"class": "state-list-column"})

    for column in state_list_columns:
        for state_tag in column.find_all("li"):
            state_url = (
                "https://www.onemainfinancial.com/api/v3/branches?state="
                + state_tag.find("a")["href"].split("/")[-1]
            )
            crawl_state.push_request(SerializableRequest(url=state_url))
    crawl_state.set_misc_value("got_urls", True)
    return driver


def get_data():
    day_dict = {
        "2": "Mon",
        "3": "Tue",
        "4": "Wed",
        "5": "Thu",
        "6": "Fri",
        "7": "Sat",
        "1": "Sun",
    }

    if not crawl_state.get_misc_value("got_urls"):
        driver = get_urls()

    else:
        url = "https://www.onemainfinancial.com/branches"
        class_name = "state-list-column"
        driver = get_driver(url, class_name)

    for data_url in crawl_state.request_stack_iter():
        search_url = data_url.url
        script = (
            """
            var done = arguments[0]
            fetch("""
            + '"'
            + search_url
            + '"'
            + """, {
                "headers": {
                    "accept": "application/json, text/plain, */*",
                    "accept-language": "en-US,en;q=0.9",
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "Windows",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin"
                },
                "referrer": "https://www.onemainfinancial.com/branches/al",
                "referrerPolicy": "strict-origin-when-cross-origin",
                "body": null,
                "method": "GET",
                "mode": "cors",
                "credentials": "include"
            })
            .then(res => res.json())
            .then(data => done(data))
        """
        )
        data = driver.execute_async_script(script)

        for location in data["branches"]:
            locator_domain = "onemainfinancial.com"
            page_url = (
                "https://www.onemainfinancial.com/branches/"
                + location["address"]["state"].lower()
                + "/"
                + location["address"]["city"].lower().replace(" ", "-")
                + "/"
                + location["address"]["zip"]
                + "/"
                + location["id"]
            )
            location_name = location["name"]
            latitude = location["location"]["latitude"]
            longitude = location["location"]["longitude"]
            city = location["address"]["city"]
            store_number = location["id"]
            address = (
                location["address"]["line_1"] + " " + location["address"]["line_2"]
            )
            zipp = location["address"]["zip"]
            phone = location["phone_number"]
            location_type = "branch"
            country_code = "US"
            state = location["address"]["state"]
            hours = ""
            try:
                for day_hour in location["hours"].split(","):
                    day = day_dict[day_hour.split(":")[0]]
                    start = day_hour.split(":AM")[0][2:]
                    end = day_hour.split("AM:")[1].split(":PM")[0]
                    hours = hours + day + " " + start + "-" + end + ", "
                hours = hours[:-2]

            except Exception:
                hours = "<MISSING>"

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


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"], part_of_record_identity=True),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"], part_of_record_identity=True),
        longitude=sp.MappingField(mapping=["longitude"], part_of_record_identity=True),
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
