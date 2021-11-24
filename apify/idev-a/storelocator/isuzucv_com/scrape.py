from sgscrape import simple_scraper_pipeline as sp
from sgselenium import SgChrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import json
from sglogging import SgLogSetup
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("isuzucv")
locator_domain = "https://www.isuzucv.com/"
base_url = "https://www.isuzucv.com/en/app/locator"


def pull_data(url, ext, zipcode, auth, max_attempts):
    attempts = 0
    with SgChrome() as driver:
        while attempts < max_attempts:
            attempts += 1
            if not auth:
                driver.get(url)
                auth = driver.page_source.split(
                    'method="post"><input type="hidden" name="', 1
                )[1].split('"', 1)[0]
                logger.info(f"auth grabbed with success: {auth}")
                data = driver.get(str(url + ext).format(auth=auth, zipcode=zipcode))
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//div[contains(@class, 'locator_results')]//div[@class='dealer_list']",
                        )
                    )
                )
                data = driver.page_source
                if "var dealers = " not in data:
                    if "lookups from your address" in data:
                        auth = None
                else:
                    data = json.loads(
                        data.split("var dealers = ", 1)[1].split("];", 1)[0] + "]"
                    )
                    break
            else:
                logger.info(auth)
                data = driver.get(str(url + ext).format(auth=auth, zipcode=zipcode))
                data = driver.page_source
                data = json.loads(
                    data.split("var dealers = ", 1)[1].split("];", 1)[0] + "]"
                )
        if attempts < max_attempts:
            return data
    return None


def fetch_data():
    url = "https://www.isuzucv.com/en/app/locator"
    ext = "?{auth}=&AddressForm%5BAddress%5D=&AddressForm%5BCity%5D=&AddressForm%5BState%5D=&AddressForm%5BZip%5D=10002&AddressForm%5BLatitude%5D=&AddressForm%5BLongitude%5D=&AddressForm%5BZipPriority%5D=1&AddressForm%5BRadius%5D=500000&AddressForm%5BDealerType%5D=0&yt0=Continue"
    zipcode = "10002"
    identities = set()
    total = 0
    son = pull_data(url, ext, zipcode, auth=None, max_attempts=5)
    if not son:
        logger.info(
            f"Reached retry limit, was blocked everytime\nzipcode | {zipcode}"
        )  # noqa
        raise
    found = 0
    for i in son:
        if str(str(i[0]) + str(i[1]) + str(i[2])) not in identities:
            identities.add(str(str(i[0]) + str(i[1]) + str(i[2])))
            found += 1
            yield i
        total += found
        logger.info(f"{zipcode} | found: {found} | total: {total}")
    logger.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(locator_domain),
        page_url=sp.ConstantField(base_url),
        location_name=sp.MappingField(
            mapping=[0],
        ),
        latitude=sp.MappingField(
            mapping=[1],
        ),
        longitude=sp.MappingField(
            mapping=[2],
        ),
        street_address=sp.MultiMappingField(
            mapping=[[3], [4]],
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
        ),
        city=sp.MappingField(
            mapping=[5],
        ),
        state=sp.MappingField(
            mapping=[6],
        ),
        zipcode=sp.MappingField(
            mapping=[7],
        ),
        country_code=sp.ConstantField("US"),
        phone=sp.MappingField(
            mapping=[8],
        ),
        store_number=sp.MissingField(),
        hours_of_operation=sp.MissingField(),
        location_type=sp.MissingField(),
        raw_address=sp.MissingField(),
    )
    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )
    pipeline.run()


if __name__ == "__main__":
    scrape()
