import time
import json
from ast import literal_eval
from sgscrape import simple_scraper_pipeline as sp
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgselenium import SgChrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def fetch_data():
    logzilla = SgLogSetup().get_logger(logger_name="chanel_com__en___gb")
    url = "https://services.chanel.com/en_GB/storelocator/crp/@{lat},{lng},10z/?"
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN],
        max_radius_miles=15,
        max_search_results=200,
    )
    identities = set()
    maxZ = search.items_remaining()
    total = 0
    with SgChrome() as driver:
        for lat, lng in search:
            if search.items_remaining() > maxZ:
                maxZ = search.items_remaining()
            found = 0
            driver.get(url.format(lat=lat, lng=lng))
            search_box_xpath = (
                '//input[@aria-label="Search - Enter an address or city"]'
            )
            WebDriverWait(driver, 40).until(
                EC.element_to_be_clickable((By.XPATH, search_box_xpath))
            )
            timeout = 40
            waited = 0
            found = False
            son = {"stores": []}
            while waited < timeout and not found:
                for r in driver.requests:
                    if "getStoreList" in r.path:
                        timeout2 = 5
                        waited2 = 0
                        if not r.response:
                            continue

                        while not r.response.body and waited2 < timeout2:
                            time.sleep(1)
                            waited2 += 1
                        son = json.loads(r.response.body)
                        found = True
                if not found:
                    time.sleep(1)
                    waited += 1
            for i in son["stores"]:
                search.found_location_at(i["latitude"], i["longitude"])
                if str(i["id"] + i["latitude"] + i["longitude"]) not in identities:
                    identities.add(str(i["id"] + i["latitude"] + i["longitude"]))
                    found += 1
                    if len(i["translations"]) > 1:
                        raise i
                    yield i

            total += found
        logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


def hoo_transform(hoo_raw):
    hoo = []
    if hoo_raw:
        data = literal_eval(hoo_raw)
        for i in data:
            days = i["day"]
            opening = i["opening"]
            daystime = days + " " + opening
            hoo.append(daystime)
        hoo = "; ".join(hoo)
        return hoo
    else:
        return "<MISSING>"


def scrape():
    url = "https://www.chanel.com/en_GB/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MissingField(),
        location_name=sp.MappingField(
            mapping=["translations", 0, "name"],
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
        ),
        street_address=sp.MultiMappingField(
            mapping=[["translations", 0, "address1"], ["translations", 0, "address2"]],
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
        ),
        city=sp.MappingField(
            mapping=["translations", 0, "cityname"],
        ),
        state=sp.MappingField(
            mapping=["translations", 0, "statename"],
            is_required=False,
        ),
        zipcode=sp.MappingField(
            mapping=["zipcode"],
        ),
        country_code=sp.MappingField(
            mapping=["legacycountryname"],
            is_required=False,
        ),
        phone=sp.MappingField(
            mapping=["phone"],
            is_required=False,
        ),
        store_number=sp.MappingField(
            mapping=["id"],
        ),
        hours_of_operation=sp.MappingField(
            mapping=["openinghours"],
            value_transform=hoo_transform,
        ),
        location_type=sp.MultiMappingField(
            mapping=[["postypename"], ["translations", 0, "division_name"]],
            multi_mapping_concat_with=" - ",
        ),
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
