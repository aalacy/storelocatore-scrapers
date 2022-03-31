from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4
from sgselenium import SgChrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import ssl
from sgscrape.pause_resume import SerializableRequest, CrawlStateSingleton
import json

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")


def no_json(soup):
    soup = b4(soup, "lxml")
    k = {}
    k["mainEntity"] = {}
    k["mainEntity"]["address"] = {}
    try:
        address = soup.find(
            "span",
            {"class": lambda x: x and all(i in x for i in ["item-info", "t-address"])},
        ).text.strip()
    except Exception:
        address = "<MISSING>"

    try:
        telephone = soup.find(
            "span",
            {"class": lambda x: x and all(i in x for i in ["item-info", "t-phone"])},
        ).text.strip()
    except Exception:
        telephone = "<MISSING>"

    try:
        city = soup.find("span", {"class": "t-city"})
    except Exception:
        city = "<MISSING>"

    try:
        state = soup.find("span", {"class": "t-state"})
    except Exception:
        state = "<MISSING>"

    try:
        zipcode = soup.find("span", {"class": "t-zip"})
    except Exception:
        zipcode = "<MISSING>"

    try:
        country = soup.find("span", {"class": "t-country"})
    except Exception:
        country = "<MISSING>"

    k["mainEntity"]["address"]["streetAddress"] = address
    k["mainEntity"]["address"]["telephone"] = []
    k["mainEntity"]["address"]["telephone"].append(telephone)
    k["mainEntity"]["address"]["addressLocality"] = city
    k["mainEntity"]["address"]["addressRegion"] = state
    k["mainEntity"]["address"]["postalCode"] = zipcode
    k["mainEntity"]["address"]["addressCountry"] = country
    return k


def clean_record(k):
    try:
        k["sub"] = k["sub"]
    except Exception:
        k["sub"] = {}
        k["sub"]["mainEntity"] = {}
        k["sub"]["mainEntity"]["address"] = {}
        k["sub"]["mainEntity"]["address"]["streetAddress"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressLocality"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressRegion"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["postalCode"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressCountry"] = "<MISSING>"
        k["sub"]["mainEntity"]["telephone"] = ["<MISSING>"]
        k["sub"]["mainEntity"]["@type"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"] = k["sub"]["mainEntity"]
    except Exception:
        k["sub"]["mainEntity"] = {}
        k["sub"]["mainEntity"]["address"] = {}
        k["sub"]["mainEntity"]["address"]["streetAddress"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressLocality"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressRegion"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["postalCode"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressCountry"] = "<MISSING>"
        k["sub"]["mainEntity"]["telephone"] = ["<MISSING>"]
        k["sub"]["mainEntity"]["@type"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["address"] = k["sub"]["mainEntity"]["address"]
    except Exception:
        k["sub"]["mainEntity"]["address"] = {}
        k["sub"]["mainEntity"]["address"]["streetAddress"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressLocality"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressRegion"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["postalCode"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressCountry"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["address"]["streetAddress"] = k["sub"]["mainEntity"][
            "address"
        ]["streetAddress"]
    except Exception:
        k["sub"]["mainEntity"]["address"]["streetAddress"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["address"]["addressLocality"] = k["sub"]["mainEntity"][
            "address"
        ]["addressLocality"]
    except Exception:
        k["sub"]["mainEntity"]["address"]["addressLocality"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["address"]["addressRegion"] = k["sub"]["mainEntity"][
            "address"
        ]["addressRegion"]
    except Exception:
        k["sub"]["mainEntity"]["address"]["addressRegion"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["address"]["postalCode"] = k["sub"]["mainEntity"][
            "address"
        ]["postalCode"]
    except Exception:
        k["sub"]["mainEntity"]["address"]["postalCode"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["address"]["addressCountry"] = k["sub"]["mainEntity"][
            "address"
        ]["addressCountry"]
    except Exception:
        k["sub"]["mainEntity"]["address"]["addressCountry"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["telephone"] = k["sub"]["mainEntity"]["telephone"]
    except Exception:
        k["sub"]["mainEntity"]["telephone"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["@type"] = k["sub"]["mainEntity"]["@type"]
    except Exception:
        k["sub"]["mainEntity"]["@type"] = ""

    try:
        k["main"] = k["main"]
    except Exception:
        k["main"] = {}
        k["main"]["coordinates"] = {}
        k["main"]["coordinates"]["latitude"] = "<MISSING>"
        k["main"]["coordinates"]["longitude"] = "<MISSING>"
        k["main"]["code"] = "<MISSING>"
        k["main"]["name"] = "<MISSING>"

    try:
        k["main"]["coordinates"] = k["main"]["coordinates"]
    except Exception:
        k["main"]["coordinates"] = {}
        k["main"]["coordinates"]["latitude"] = "<MISSING>"
        k["main"]["coordinates"]["longitude"] = "<MISSING>"

    try:
        k["main"]["code"] = k["main"]["code"]
    except Exception:
        k["main"]["code"] = "<MISSING>"

    try:
        k["main"]["name"] = k["main"]["name"]
    except Exception:
        k["main"]["name"] = "<MISSING>"

    return k


def try_again(session, url):
    headers = {}
    headers["accept"] = "application/json, text/plain, */*"
    headers["accept-encoding"] = "gzip, deflate, br"
    headers["accept-language"] = "en-us"
    headers["cache-control"] = "no-cache"
    headers["pragma"] = "no-cache"
    headers["referer"] = "https://www.radissonhotels.com/en-us/destination"
    headers[
        "sec-ch-ua"
    ] = '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"'
    headers["sec-ch-ua-mobile"] = "?0"
    headers["sec-ch-ua-platform"] = '"Windows"'
    headers["sec-fetch-dest"] = "empty"
    headers["sec-fetch-mode"] = "cors"
    headers["sec-fetch-site"] = "same-origin"
    headers[
        "user-agent"
    ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36"
    response = SgRequests.raise_on_err(session.get(url, headers=headers))
    return response.json()


def get_subpage(session, url):
    headers = {}
    headers["accept"] = "application/json, text/plain, */*"
    headers["accept-encoding"] = "gzip, deflate, br"
    headers["accept-language"] = "en-us"
    headers["cache-control"] = "no-cache"
    headers["pragma"] = "no-cache"
    headers[
        "sec-ch-ua"
    ] = '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"'
    headers["sec-ch-ua-mobile"] = "?0"
    headers["sec-ch-ua-platform"] = '"Windows"'
    headers["sec-fetch-dest"] = "empty"
    headers["sec-fetch-mode"] = "cors"
    headers["sec-fetch-site"] = "same-origin"
    headers[
        "user-agent"
    ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36"

    data = {}
    if len(url) > 0:
        try:
            response = SgRequests.raise_on_err(session.get(url, headers=headers))
            soup = b4(response.text, "lxml")
            logzilla.info(f"URL\n{url}\nLen:{len(response.text)}\n")
            if len(response.text) < 400:
                logzilla.info(f"Content\n{response.text}\n\n")
        except Exception as e:
            logzilla.error(f"err\n{str(e)}\nUrl:{url}\n\n")
            try:
                logzilla.error(f"{response}")
                logzilla.error(f"{response.text}")
            except Exception:
                pass
        if len(response.text) < 400:
            try:
                response = try_again(session, url)
                if len(response.text) < 400:
                    logzilla.info(f"Content\n{response.text}\n\n")
                soup = b4(response.text, "lxml")
            except Exception as e:
                logzilla.error(f"{str(e)}")
                raise

        try:
            data = json.loads(
                str(
                    soup.find(
                        "script",
                        {"type": "application/ld+json", "id": "schema-webpage"},
                    ).text
                )
                .replace("\u0119", "e")
                .replace("\u011f", "g")
                .replace("\u0144", "n")
                .replace("\u0131", "i"),
                strict=False,
            )
        except Exception:
            try:
                data = no_json(response.text)
            except Exception:
                data = {}
        data["requrl"] = url
        data["STATUS"] = True
    else:
        data["requrl"] = "<MISSING>"
        data["STATUS"] = False
    return data


def initial(driver, url, state):
    with SgChrome() as driver:
        driver.get(url)
        try:
            locator = WebDriverWait(driver, 10).until(  # noqa
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "/html/body/main/section/div/div/div/div/p/p/a",
                    )
                )
            )  # noqa
        except Exception:
            locator2 = WebDriverWait(driver, 10).until(  # noqa
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "/html/body/main/div[3]/div/div/div/div/span",
                    )
                )
            )  # noqa

        time.sleep(15)
        time.sleep(5)
        reqs = list(driver.requests)
        logzilla.info(f"Length of driver.requests: {len(reqs)}")
        for r in reqs:
            x = r.url
            # logzilla.info(x)
            if "zimba" in x and "hotels?" in x:
                son = json.loads(r.response.body)
                for item in son["hotels"]:
                    state.push_request(
                        SerializableRequest(url=item["overviewPath"], context=item)
                    )


def record_initial_requests(driver, state):
    for url in [
        "https://www.radissonhotels.com/en-us/destination",
        "https://www.radissonhotelsamericas.com/en-us/destination",
    ]:
        initial(driver, url, state)


def data_fetcher(session, state):
    for next_r in state.request_stack_iter():
        k = {}
        k["main"] = next_r.context
        k["sub"] = get_subpage(session, next_r.url)
        try:
            k["sub"]["requrl"] = k["sub"]["requrl"]
        except Exception:
            k["sub"]["requrl"] = next_r.url
        k = clean_record(k)
        yield k


def fetch_data():
    state = CrawlStateSingleton.get_instance()
    with SgChrome() as driver:
        state.get_misc_value(
            "init", default_factory=lambda: record_initial_requests(driver, state)
        )

    with SgRequests() as session:
        for item in data_fetcher(session, state):
            yield item


def fix_phone(x):
    if len(x) < 3:
        return "<MISSING>"
    return x


def scrape():
    url = "https://www.radissonhotels.com/en-us/destination"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["sub", "requrl"],
            is_required=False,
            part_of_record_identity=True,
        ),
        location_name=sp.MappingField(
            mapping=["main", "name"],
            is_required=False,
            part_of_record_identity=True,
        ),
        latitude=sp.MappingField(
            mapping=["main", "coordinates", "latitude"],
            is_required=False,
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["main", "coordinates", "longitude"],
            is_required=False,
        ),
        street_address=sp.MappingField(
            mapping=["sub", "mainEntity", "address", "streetAddress"],
            is_required=False,
            part_of_record_identity=True,
        ),
        city=sp.MappingField(
            mapping=["sub", "mainEntity", "address", "addressLocality"],
            is_required=False,
        ),
        state=sp.MappingField(
            mapping=["sub", "mainEntity", "address", "addressRegion"],
            is_required=False,
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        zipcode=sp.MappingField(
            mapping=["sub", "mainEntity", "address", "postalCode"],
            is_required=False,
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        country_code=sp.MappingField(
            mapping=["sub", "mainEntity", "address", "addressCountry"],
            is_required=False,
        ),
        phone=sp.MappingField(
            mapping=["sub", "mainEntity", "telephone", 0],
            is_required=False,
            value_transform=fix_phone,
        ),
        store_number=sp.MappingField(
            mapping=["main", "code"],
            is_required=False,
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MissingField(),
        location_type=sp.MappingField(
            mapping=["@type"],
            is_required=False,
        ),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=30,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
