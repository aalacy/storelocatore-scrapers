from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgselenium import SgChrome
import json
import time


def get_codes(url):
    with SgChrome() as driver:
        driver.get(url)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "lxml")
        time.sleep(10)
    codes = list(
        i["value"]
        for i in soup.find("select", {"id": "dwfrm_storelocator_country"}).find_all(
            "option"
        )
    )
    return codes


def yield_data(country_code):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
    }
    url = "https://www.clubmonaco.com/on/demandware.store/Sites-ClubMonaco_US-Site/en_US/Stores-ViewResults?country={cCode}&postal=null&radius=15000"
    session = SgRequests()
    son = session.post(url.format(cCode=country_code), headers=headers)
    soup = BeautifulSoup(son.text, "lxml")
    soup1 = soup.find("div", {"class": "storeJSON hide"})["data-storejson"]
    soup1 = '{"store":' + soup1 + "}"
    soup = soup.find("script", {"type": "application/ld+json"})
    son = json.loads(soup.text)
    sony = json.loads(soup1)
    count = 0
    for idex, i in enumerate(son["store"]):
        if idex % 2 == 0:
            store = {}
            store["main"] = i
            store["sec"] = son["store"][idex + 1]
            store["tert"] = sony["store"][count]
            count += 1
            yield store


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="clubmonaco")
    domain = "https://www.clubmonaco.com/en/StoreLocator"
    countries = get_codes(domain)
    for code in countries:
        count = 0
        for record in yield_data(code):
            count += 1
            yield record
        logzilla.info(f"For country {code} we found {count} stores")  # noqa
    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_hours(x):
    x = (
        x.replace("</p>\n", "; ")
        .replace("<p>", "")
        .replace("\n", "")
        .replace("</p>", "")
        .replace("<br />", "; ")
        .replace("&nbsp;", " ")
        .replace("</br></br>", "")
        .replace("</br>", "; ")
        .replace(";  ;", ";")
    )
    if "Curb" in x:
        x = "".join(x.split("Curb")[:-1])
    return x


def good_phone(x):
    x = x.replace("-", "")
    if "Curb" in x:
        x = "".join(x.split("Curb")[:-1])
    if "WedSun" in x:
        x = x.replace("WedSun", "")
    return x


def scrape():
    url = "https://clubmonaco.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MissingField(),
        location_name=MappingField(mapping=["main", "legalName"]),
        latitude=MappingField(mapping=["tert", "latitude"]),
        longitude=MappingField(mapping=["tert", "longitude"]),
        street_address=MappingField(
            mapping=["sec", "address", "streetAddress"],
            value_transform=lambda x: " ".join(x.split(",")[:-1]),
        ),
        city=MappingField(
            mapping=["tert", "city"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        state=MappingField(
            mapping=["tert", "stateCode"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        zipcode=MappingField(
            mapping=["tert", "postalCode"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        country_code=MappingField(mapping=["sec", "address", "addressCountry"]),
        phone=MappingField(mapping=["tert", "phone"], value_transform=good_phone),
        store_number=MappingField(mapping=["tert", "id"]),
        hours_of_operation=MappingField(
            mapping=["main", "openingHours"],
            value_transform=fix_hours,
            is_required=False,
        ),
        location_type=MappingField(mapping=["sec", "@type"]),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="clubmonaco.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=25,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
