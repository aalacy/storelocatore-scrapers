import time
import json
import ssl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
from sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("maxandermas.com")
user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)
try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def initiateDriver(driver=None):
    if driver is not None:
        driver.quit()

    return SgChrome(
        is_headless=True,
        user_agent=user_agent,
        executable_path=ChromeDriverManager().install(),
    ).driver()


def _valid(val):
    return (
        val.replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0", "")
        .replace("\\xa0\\xa", "")
        .replace("\\xae", "")
        .replace("\\u2022", "")
    )


days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN", "DINE-IN"]


def _filter(blocks):
    hours = []
    for block in blocks:
        for _ in block.stripped_strings:
            if "DINE" in _valid(_).upper():
                continue
            if (
                _.split(" ")[0]
                .split("-")[0]
                .split("–")[0]
                .split("&")[0]
                .strip()
                .upper()
                in days
            ):
                hours += _valid(_).split("|")

    return hours


def fetch_data():
    logger.info("Started Crawling")
    locator_domain = "https://www.maxandermas.com/"
    base_url = "https://www.maxandermas.com/locations/"
    json_url = "https://www.maxandermas.com/wp-json/wpgmza/v1/features/"
    with SgChrome(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"
    ) as driver:
        driver.get(base_url)
        exist = False
        while not exist:
            time.sleep(2)
            for rr in driver.requests:
                if rr.url.startswith(json_url) and rr.response:
                    logger.info(f"Crawling Kicked Off {rr.url}")
                    exist = True
                    driver.get(rr.url)
                    locations = json.loads(bs(driver.page_source, "lxml").text.strip())[
                        "markers"
                    ]
                    for location in locations:
                        logger.info(f"Now processing Page: {location['link']}")
                        location_type = "<MISSING>"
                        driver = initiateDriver()
                        driver.get(location["link"])
                        time.sleep(5)
                        soup = bs(driver.page_source, "lxml")
                        blocks = soup.select("div.et_pb_text_inner h2")
                        hours = _filter(blocks)
                        if not hours:
                            blocks = soup.select("div.et_pb_text_inner p")
                            hours = _filter(blocks)
                        if (
                            soup.select_one('span[color="#808080"]')
                            and "TEMPORARILY CLOSED"
                            in soup.select_one('span[color="#808080"]').text
                        ):
                            hours = ["TEMPORARILY CLOSED"]
                            location_type = "TEMPORARILY CLOSED"

                        addr = parse_address_intl(location["address"])
                        phone = [
                            _
                            for _ in bs(
                                location["description"], "lxml"
                            ).stripped_strings
                        ][-1]
                        _phone = (
                            phone.encode("unicode-escape").decode("utf8").split("\\xa0")
                        )
                        if len(_phone) > 1:
                            phone = _phone[1]

                        location_name = _valid(location["title"])
                        if "TEMPORARILY CLOSED" in location_name:
                            location_name = location_name.split("-")[0].strip()
                            location_type = "TEMPORARILY CLOSED"
                            hours = ["TEMPORARILY CLOSED"]

                        yield SgRecord(
                            page_url=location["link"],
                            store_number=location["id"],
                            location_name=location_name,
                            street_address=addr.street_address_1,
                            city=addr.city,
                            state=addr.state,
                            zip_postal=addr.postcode,
                            country_code="US",
                            location_type=location_type,
                            latitude=location["lat"],
                            longitude=location["lng"],
                            phone=phone,
                            locator_domain=locator_domain,
                            hours_of_operation="; ".join(hours),
                        )

                    break


if __name__ == "__main__":
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    logger.info(f"Finished Data Grabbing, Total Locations {count}")
