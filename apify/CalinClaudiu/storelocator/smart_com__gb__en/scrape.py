from sgscrape import simple_scraper_pipeline as sp
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from sgselenium import SgChrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


def para(tup):
    headers = tup[1]
    session = SgRequests()
    k = tup[0]
    url = "https://api.corpinter.net/dlc/dms/v2/dealers/search?marketCode=GB&fields=*&whiteList="
    son = session.get(url + k["baseInfo"]["externalId"], headers=headers).json()
    k = son

    return k


def specialheaders():

    url = "https://www.mercedes-benz.co.uk/passengercars/mercedes-benz-cars/dealer-locator.html"

    headers = {}
    headers["x-apikey"] = ""
    headers[
        "User-Agent"
    ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"

    with SgChrome() as driver:
        driver.get(url)
        try:
            accept = WebDriverWait(driver, 50).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id="uc-btn-accept-banner"]')
                )
            )
            driver.execute_script("arguments[0].click();", accept)
        except Exception:
            headers["x-apikey"] = ""

        driver.switch_to.frame("dlc-cont")
        byname = WebDriverWait(driver, 50).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="mb-dl-spa"]/div/section[2]/div/form/ul/li[2]/a')
            )
        )
        driver.execute_script("arguments[0].click();", byname)
        sbar = WebDriverWait(driver, 50).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="mb-dl-spa"]/div/section[2]/div/form/div/input')
            )
        )
        sbar.send_keys("Benz")
        sbar.send_keys(Keys.RETURN)

        dealer = WebDriverWait(driver, 50).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="mb-dl-spa"]/div/section[2]/section/div[1]')
            )
        )
        driver.execute_script("arguments[0].click();", dealer)

        for r in driver.requests:
            if "/dlc/dms/v2/dealers/search" in r.path:
                try:
                    headers["x-apikey"] = r.headers["x-apikey"]
                except Exception:
                    try:
                        headers["x-apikey"] = r.response.headers["x-apikey"]
                    except Exception:
                        headers["x-apikey"] = headers["x-apikey"]

    return headers


def determine_brand(k):
    brands = []
    for i in k["brands"]:
        brands.append(
            str(i["brand"]["name"]) + str("(" + str(i["brand"]["code"]) + ")")
        )

    return ", ".join(brands)


def determine_smart(brand):
    return "mart" in brand or "SMT" in brand


def determine_hours(k, brand, which):
    hours = "<MISSING>"
    h = []
    if which != "LITERALLYANYTHING" and which != "SUPERLITERALLYANYTHING":
        try:
            for i in k["functions"]:
                if (
                    i["brandCode"] == brand
                    and i["activityCode"] == which
                    and len(h) == 0
                ):
                    try:
                        for j in list(i["openingHours"]):
                            if i["openingHours"][j]["open"]:
                                h.append(
                                    str(j)
                                    + ": "
                                    + str(
                                        i["openingHours"][j]["timePeriods"][0]["from"]
                                    )
                                    + "-"
                                    + str(i["openingHours"][j]["timePeriods"][0]["to"])
                                )
                            else:
                                h.append(str(j) + ": Closed")
                    except Exception:
                        continue
            if len(h) == 0:
                hours = determine_hours(k, brand, "LITERALLYANYTHING")
            else:
                return "; ".join(h)
        except Exception:
            return hours

    if which == "LITERALLYANYTHING":
        for i in k["functions"]:
            if i["brandCode"] == brand and len(h) == 0:
                try:
                    for j in list(i["openingHours"]):
                        if i["openingHours"][j]["open"]:
                            h.append(
                                str(j)
                                + ": "
                                + str(i["openingHours"][j]["timePeriods"][0]["from"])
                                + "-"
                                + str(i["openingHours"][j]["timePeriods"][0]["to"])
                            )
                        else:
                            h.append(str(j) + ": Closed")
                except Exception:
                    continue
        if len(h) == 0:
            hours = determine_hours(k, brand, "SUPERLITERALLYANYTHING")
        else:
            return "; ".join(h)

    if which == "SUPERLITERALLYANYTHING":
        for i in k["functions"]:
            if hours == "<MISSING>" and len(h) == 0:
                try:
                    for j in list(i["openingHours"]):
                        if i["openingHours"][j]["open"]:
                            h.append(
                                str(j)
                                + ": "
                                + str(i["openingHours"][j]["timePeriods"][0]["from"])
                                + "-"
                                + str(i["openingHours"][j]["timePeriods"][0]["to"])
                            )
                        else:
                            h.append(str(j) + ": Closed")
                except Exception:
                    continue
        if len(h) == 0:
            return hours
        else:
            return "; ".join(h)

    return hours


def fetch_data():

    logzilla = sglog.SgLogSetup().get_logger(logger_name="CRAWLER")
    # x-apikey:45ab9277-3014-4c9e-b059-6c0542ad9484

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
        "x-apikey": "45ab9277-3014-4c9e-b059-6c0542ad9484",
    }

    headers = specialheaders()
    resultsList = (
        "https://api.corpinter.net/dlc/dms/v2/dealers/search?marketCode=GB&fields="
    )
    session = SgRequests()
    results = session.get(resultsList, headers=headers).json()

    lize = utils.parallelize(
        search_space=[[i, headers] for i in results["results"]],
        fetch_results_for_rec=para,
        max_threads=20,
        print_stats_interval=20,
    )
    for i in lize:
        i["results"][0]["brandino"] = determine_brand(i["results"][0])
        i["results"][0]["isSmart"] = determine_smart(i["results"][0]["brandino"])
        i["results"][0]["salesHours"] = determine_hours(i["results"][0], "SMT", "SALES")

        # Fixes random issue with multi-mapping-concat and raw_value_transform

        try:
            i["results"][0]["address"]["region"]["region"] = i["results"][0]["address"][
                "region"
            ]["region"]
        except Exception:
            try:
                backup = i["results"][0]["address"]["region"]["subRegion"]
            except Exception:
                backup = ""
            i["results"][0]["address"]["region"] = {}
            i["results"][0]["address"]["region"]["region"] = ""
            i["results"][0]["address"]["region"]["subRegion"] = backup

        try:
            i["results"][0]["address"]["region"]["subRegion"] = i["results"][0][
                "address"
            ]["region"]["subRegion"]
        except Exception:
            try:
                backup = i["results"][0]["address"]["region"]["region"]
            except Exception:
                backup = ""
            i["results"][0]["address"]["region"] = {}
            i["results"][0]["address"]["region"]["region"] = backup
            i["results"][0]["address"]["region"]["subRegion"] = ""

        try:
            i["results"][0]["address"]["line2"] = i["results"][0]["address"]["line2"]
        except Exception:
            i["results"][0]["address"]["line2"] = ""

        try:
            i["results"][0]["address"]["latitude"] = i["results"][0]["address"][
                "latitude"
            ]
        except Exception:
            i["results"][0]["address"]["latitude"] = ""

        try:
            i["results"][0]["address"]["longitude"] = i["results"][0]["address"][
                "longitude"
            ]
        except Exception:
            i["results"][0]["address"]["longitude"] = ""

        try:
            i["results"][0]["contact"] = i["results"][0]["contact"]
        except Exception:
            i["results"][0]["contact"] = {}
            i["results"][0]["contact"]["phone"] = ""
            i["results"][0]["contact"]["website"] = ""
        try:
            i["results"][0]["contact"]["phone"] = i["results"][0]["contact"]["phone"]
        except Exception:
            i["results"][0]["contact"]["phone"] = ""

        try:
            i["results"][0]["contact"]["website"] = i["results"][0]["contact"][
                "website"
            ]
        except Exception:
            i["results"][0]["contact"]["website"] = ""

        # Fixes random issue with multi-mapping-concat and raw_value_transform

        yield i["results"][0]  # don't worry, there's always only one.

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []
    try:
        x = x.split(",")
        for i in x:
            st = i.strip()
            if len(st) >= 1:
                h.append(st)
        h = ", ".join(h)
    except Exception:
        h = x

    return h


def scrape():
    url = "https://www.smart.com/gb/en/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["contact", "website"],
            is_required=False,
        ),
        location_name=sp.MappingField(
            mapping=["baseInfo", "name1"],
            is_required=False,
        ),
        latitude=sp.MappingField(
            mapping=["address", "latitude"],
            is_required=False,
        ),
        longitude=sp.MappingField(
            mapping=["address", "longitude"],
            is_required=False,
        ),
        street_address=sp.MultiMappingField(
            mapping=[["address", "line1"], ["address", "line2"]],
            multi_mapping_concat_with=", ",
            is_required=False,
            value_transform=fix_comma,
        ),
        city=sp.MappingField(mapping=["address", "city"], is_required=False),
        state=sp.MultiMappingField(
            mapping=[
                ["address", "region", "region"],
                ["address", "region", "subRegion"],
            ],
            multi_mapping_concat_with=": ",
            is_required=False,
        ),
        zipcode=sp.MappingField(
            mapping=["address", "zipcode"],
            is_required=False,
        ),
        country_code=sp.MappingField(mapping=["address", "country"], is_required=False),
        phone=sp.MappingField(
            mapping=["contact", "phone"],
            is_required=False,
        ),
        store_number=sp.MappingField(
            mapping=["baseInfo", "externalId"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(mapping=["salesHours"]),
        location_type=sp.MappingField(mapping=["brandino"]),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
