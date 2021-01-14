from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sgselenium import SgChrome
from selenium import webdriver
from bs4 import BeautifulSoup as b4
from sgrequests import SgRequests
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json
import time


def fetch_data():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    
    with driver as driver:
    #with SgChrome() as driver:
        url = "https://locations.geisinger.org/?clinicName%3D%26specialty%3D%26distance%3D30000%26zip%3D10004"
        driver.get(url)
        # json location
        k = (
            WebDriverWait(driver, 120)
            .until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="bottom"]/script'))
            )
            .get_attribute("innerHTML")
        )
        k = k.split("var results= ")[1]
        k = k.split("[", 1)[1]
        k = k.split("}];")[0]
        k = '{"stores":[' + k + "}]}"
        son = json.loads(k)
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
        }
        session = SgRequests()
        for i in son["stores"]:
            soup = session.get(
                str(
                    "https://locations.geisinger.org/details.cfm?id="
                    + str(i["CLINICID"])
                )
            )

            soup = b4(soup.text, "lxml")
            try:
                i["hours"] = "; ".join(
                    list(
                        soup.find("div", {"class": "officeHours"})
                        .find("p")
                        .stripped_strings
                    )
                )
            except Exception:
                try:
                    i["hours"] = "; ".join(
                        list(
                            soup.find("div", {"class": "officeHours"}).stripped_strings
                        )
                    )
                except Exception:
                    try:
                        i["hours"] = soup.find(
                            "div", {"class": "officeHours"}
                        ).text.strip()
                    except Exception:
                        i["hours"] = "<MISSING>"

            try:
                coords = soup.find("", {"href": lambda x: x and "maps" in x})["href"]
                print(coords)
                print("suc")
                coords = coords.split("/@", 1)[1].split("/", 1)[0].split(",")
            except Exception:
                coords = ["<MISSING>", "<MISSING>"]
            i["lon"] = coords[1]
            i["lat"] = coords[0]
            yield i


def parse_features(x):
    s = b4(str(x), "lxml")
    return "; ".join(list(s.stripped_strings))


def scrape():
    url = "https://www.geisinger.org/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(
            mapping=["CLINICID"],
            value_transform=lambda x: "https://locations.geisinger.org/details.cfm?id="
            + str(x),
        ),
        location_name=MappingField(
            mapping=["NAME"], value_transform=lambda x: x.replace("&amp; ", "")
        ),
        latitude=MappingField(mapping=["lat"]),
        longitude=MappingField(mapping=["lat"]),
        street_address=MappingField(mapping=["ADDRESS1"]),
        city=MappingField(mapping=["CITY"]),
        state=MappingField(mapping=["STATE"]),
        zipcode=MappingField(
            mapping=["ZIPCODE"], value_transform=lambda x: x.replace(" ", "")
        ),
        country_code=MissingField(),
        phone=MappingField(mapping=["PHONE"], is_required=False),
        store_number=MappingField(mapping=["CLINICID"]),
        hours_of_operation=MappingField(mapping=["hours"], is_required=False),
        location_type=MappingField(
            mapping=["OTHERSERVICES"], value_transform=parse_features, is_required=False
        ),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="scr",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
