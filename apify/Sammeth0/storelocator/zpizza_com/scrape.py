import json
from sgrequests import SgRequests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium import SgSelenium
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

session = SgRequests()
DOMAIN = "zpizza.com"
BASE_URL = "https://www.zpizza.com/"
LOCATION_URL = "https://www.zpizza.com/locations"
headers = {
    "Accept": "*/*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
}

MISSING = "<MISSING>"


log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def wait_load(driver, number=0):
    number += 1
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "locations"))
        )
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="locations"]/div[2]/div')
            )
        )
    except:
        driver.refresh()
        if number < 3:
            log.info(f"Try to Refresh for ({number}) times")
            return wait_load(driver, number)


def fetch_data():
    driver = SgSelenium().chrome()
    driver.get("https://www.zpizza.com/locations")
    wait_load(driver)
    content_script = driver.find_element_by_xpath("/html/body/script[2]").get_attribute(
        "innerHTML"
    )
    driver.quit()
    info = content_script.split(
        '"galleryImages":[],"giftCardImages":[],"giftCardShopItem":null,"locations":'
    )[3].split(',"socialHandles":[]}],"menus":[]', 1)[0]
    info = info + ',"socialHandles":[]}]'
    p = 0
    loclist = json.loads(info)
    for loc in loclist:
        page_url = "https://www.zpizza.com/" + loc["slug"]
        if page_url.find("bend-tap-room") > -1:
            page_url = page_url.split("-")[0]
        location_name = loc["name"]
        store_number = loc["id"]
        street_address = loc["streetAddress"]
        state = loc["state"]
        city = loc["city"]
        zip_postal = loc["postalCode"]
        country_code = loc["country"]
        latitude = loc["lat"]
        longitude = loc["lng"]
        hourlist = loc["schemaHours"]
        phone = (
            loc["phone"][0:3]
            + "-"
            + loc["phone"][3:6]
            + "-"
            + loc["phone"][6 : len(loc["phone"])]
        )
        location_type = "zpizza"
        hours_of_operation = ""
        hourd = []
        hourd.append("none")
        try:
            for hr in hourlist:
                dt = hr.split(" ", 1)[0]
                if dt in hourd:
                    pass
                else:
                    hourd.append(dt)
                    day = (int)(hr.split("-")[1].split(":")[0])
                    if day > 12:
                        day = day - 12
                    hours_of_operation = (
                        hours_of_operation
                        + hr.split("-")[0]
                        + " am "
                        + " - "
                        + str(day)
                        + ":00 PM"
                    )
                    hours_of_operation = hours_of_operation + " "
            hours_of_operation = (
                hours_of_operation.replace("Su", "Sunday")
                .replace("Mo", "Monday")
                .replace("Tu", "Tuesday")
                .replace("We", "Wednesday")
                .replace("Th", "Thursday")
                .replace("Fr", "Friday")
                .replace("Sa", "Saturday")
            )
        except:
            hours_of_operation = MISSING

        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address}, {city}, {state} {zip_postal}",
        )
        p += 1


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.RAW_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
