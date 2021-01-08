from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sglogging import sglog
from sgselenium import SgChrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as b4


def parse_store(store):
    k = {}
    try:
        crappyaddr = store.find(
            "div", {"class": lambda x: x and "store-address" in x}
        ).text.strip()
        crappyaddr = crappyaddr.split("  ")
    except Exception:
        crappyaddr = "<MISSING>"

    if len(crappyaddr) > 3:
        if (len(crappyaddr[-1])) < 4:
            crappyaddr[-2] = crappyaddr[-2] + " " + crappyaddr[-1]
            crappyaddr.pop(-1)
        else:
            crappyaddr[1] = crappyaddr[0] + ", " + crappyaddr[1]
            crappyaddr.pop(0)

    try:
        k["Name"] = store.find(
            "div", {"class": lambda x: x and "store-location" in x}
        ).text.strip()
    except Exception:
        k["Name"] = "<MISSING>"

    try:
        coords = (
            store.find(
                "a",
                {"href": lambda x: x and x.startswith("https://maps.google.com/maps")},
            )["href"]
            .split("(")[1]
            .split(")")[0]
            .split(",")
        )
    except Exception:
        coords = "<MISSING>"

    try:
        k["Latitude"] = coords[0].strip()
    except Exception:
        k["Latitude"] = "<MISSING>"

    try:
        k["Longitude"] = coords[1].strip()
    except Exception:
        k["Longitude"] = "<MISSING>"

    try:
        k["Address"] = crappyaddr[0].strip()
        crappyaddr.pop(0)
        while any(i.isdigit() for i in crappyaddr[0]):
            k["Address"] = k["Address"] + ", " + crappyaddr[0].strip()
            crappyaddr.pop(0)
        if len(k["Address"]) < 5:
            k["Address"] = k["Address"] + ", " + crappyaddr[0].strip()
            crappyaddr.pop(0)
        if crappyaddr[0] == "Lapiniere" and k["Address"] == "2151 boulevard":
            k["Address"] = k["Address"] + ", " + crappyaddr[0].strip()
            crappyaddr.pop(0)

    except Exception:
        k["Address"] = "<MISSING>"

    try:
        k["City"] = crappyaddr[0].strip()
        crappyaddr.pop(0)
    except Exception:
        k["City"] = "<MISSING>"

    try:
        k["State"] = crappyaddr[-1].strip()
        k["State"] = k["State"].split(" ")[0]
    except Exception:
        k["State"] = "<MISSING>"

    try:
        k["Zip"] = crappyaddr[-1].strip()
        k["Zip"] = k["Zip"].split(" ")
        k["Zip"].pop(0)
        k["Zip"] = " ".join(k["Zip"])
    except Exception:
        k["Zip"] = "<MISSING>"

    k["CountryCode"] = "<MISSING>"

    try:
        k["Phone"] = store.find(
            "div", {"class": lambda x: x and "store-tel" in x}
        ).text.strip()
    except Exception:
        k["Phone"] = "<MISSING>"

    try:
        k["StoreId"] = store.find(
            "div", {"class": lambda x: x and "store-description" in x}
        ).text.strip()
    except Exception:
        k["StoreId"] = "<MISSING>"

    try:
        k["hours"] = "; ".join(
            list(
                store.find(
                    "div", {"class": lambda x: x and "store-operating-hours" in x}
                ).stripped_strings
            )
        ).replace("&nbsp;", " ")
    except Exception:
        k["hours"] = "<MISSING>"

    try:
        k["StatusName"] = "/".join(
            list(
                store.find(
                    "div", {"class": lambda x: x and "store-description" in x}
                ).stripped_strings
            )
        ).replace("&nbsp;", " ")
    except Exception:
        k["StatusName"] = "<MISSING>"

    return k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://thaiexpress.ca/"
    soup = "3"
    count = 0
    while soup == "3" and count < 20:
        try:
            with SgChrome() as driver:
                logzilla.info(f"Getting page..")  # noqa
                driver.get(url)
                menu = WebDriverWait(driver, 120).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="page"]/div[2]/div[2]/div[1]/a')
                    )
                )
                driver.execute_script("arguments[0].click();", menu)
                menu = WebDriverWait(driver, 120).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="mobile-menu"]/li[4]/a')
                    )
                )
                driver.execute_script("arguments[0].click();", menu)

                logzilla.info(f"Waiting for response to load.")  # noqa
                locs = WebDriverWait(driver, 120).until(  # noqa
                    EC.visibility_of_element_located((By.XPATH, '//*[@id="store0"]'))
                )
                soup = b4(driver.page_source, "lxml")
        except Exception:
            count += 1
            continue

    stores = soup.find("span", {"id": "storeLocator__storeList"})
    stores = stores.find_all("div", {"class": "store-locator__infobox"})
    for i in stores:
        yield (parse_store(i))

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []
    x.replace("None", "<MISSING>")
    try:
        x = x.split(",")
        for i in x:
            if len(i) > 1:
                h.append(i)
        h = ", ".join(h)
    except Exception:
        h = x

    return h


def clean_hours(x):

    try:
        x = x.split(">")[1]
        x = x.split("<")[0]
        if len(x) < 3:
            return "<MISSING>"
        return (
            x.replace("day", "day:")
            .replace("::", ":")
            .replace("\n", "; ")
            .replace("\r", "; ")
            .replace(": ;", ": Closed;")
            .replace("&nbsp;", " ")
            .replace("Â", " ")
        )
    except Exception:
        return (
            x.replace("day", "day:")
            .replace("::", ":")
            .replace("\n", "; ")
            .replace("\r", "; ")
            .replace(": ;", ": Closed;")
            .replace("&nbsp;", " ")
            .replace("Â", " ")
        )


def scrape():
    url = "https://www.thaiexpress.ca/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MissingField(),
        location_name=MappingField(
            mapping=["Name"],
            is_required=False,
            part_of_record_identity=True,
        ),
        latitude=MappingField(mapping=["Latitude"]),
        longitude=MappingField(mapping=["Longitude"]),
        street_address=MappingField(
            mapping=["Address"],
            value_transform=fix_comma,
            part_of_record_identity=True,
        ),
        city=MappingField(
            mapping=["City"],
            is_required=False,
            value_transform=fix_comma,
            part_of_record_identity=True,
        ),
        state=MappingField(
            mapping=["State"],
            is_required=False,
            value_transform=fix_comma,
            part_of_record_identity=True,
        ),
        zipcode=MappingField(
            mapping=["Zip"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        country_code=MappingField(mapping=["CountryCode"]),
        phone=MappingField(
            mapping=["Phone"],
            value_transform=lambda x: x.replace("() -", "<MISSING>"),
            is_required=False,
        ),
        store_number=MappingField(mapping=["StoreId"]),
        hours_of_operation=MappingField(
            mapping=["hours"], is_required=False, value_transform=clean_hours
        ),
        location_type=MappingField(
            mapping=["StatusName"],
            is_required=False,
            part_of_record_identity=True,
        ),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="pinkberry.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
