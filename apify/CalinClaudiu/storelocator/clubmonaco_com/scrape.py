from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="clubmonaco")
    urlUS = "https://www.clubmonaco.com/on/demandware.store/Sites-ClubMonaco_US-Site/en_US/Stores-ViewResults?country=US&postal=96701&radius=15000"
    urlCA = "https://www.clubmonaco.com/on/demandware.store/Sites-ClubMonaco_US-Site/en_US/Stores-ViewResults?country=CA&postal=K1Y%202B8&radius=15000"

    # K1Y 2B8
    # acting oddly, expecting 60 ish results in US, a 10000 radius query only brings 45
    # tried east coast search and lookd for west-most result
    # tried hawaii search and all east coast results are included. Might just be only 45 locations.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
    }
    session = SgRequests()
    son = session.post(urlUS, headers=headers)
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
            if store["main"]["telephone"] != store["tert"]["phone"]:
                logzilla.info(
                    f"\n !!!!! !!!!! !!!!! \n This store might be incorrectly scraped!! \n {store}"
                )
            count += 1
            yield store

    son = session.post(urlCA, headers=headers)
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
            if store["main"]["telephone"] != store["tert"]["phone"]:
                logzilla.info(
                    f"\n !!!!! !!!!! !!!!! \n This store might be incorrectly scraped!! \n {store}"
                )
            count += 1
            yield store

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
        city=MappingField(mapping=["tert", "city"]),
        state=MappingField(mapping=["tert", "stateCode"]),
        zipcode=MappingField(mapping=["tert", "postalCode"]),
        country_code=MappingField(mapping=["sec", "address", "addressCountry"]),
        phone=MappingField(mapping=["tert", "phone"], value_transform=good_phone),
        store_number=MappingField(mapping=["tert", "id"]),
        hours_of_operation=MappingField(
            mapping=["main", "openingHours"], value_transform=fix_hours
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
