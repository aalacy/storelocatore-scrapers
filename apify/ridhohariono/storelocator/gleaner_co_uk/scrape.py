from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium import SgSelenium
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
import re
import ssl
from sgscrape.sgpostal import parse_address_intl


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

DOMAIN = "gleaner.co.uk"
LOCATION_URL = "https://www.gleaner.co.uk/services/service-stations/"

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
MISSING = "<MISSING>"


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode
            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data():
    log.info("Fetching store_locator data")
    driver = SgSelenium().chrome()
    driver.get("https://www.google.com/maps/d/embed?mid=1MyMR7itOOLUAqV_XjISiG4G3mq0")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "i4ewOd-pzNkMb-ornU0b-b0t70b-Bz112c")
        )
    )
    latlong_content = driver.find_element_by_xpath(
        "/html/body/div[1]/script[1]"
    ).get_attribute("innerHTML")
    latlong = re.findall(
        r"\[([\d]*\.[\d]*),(-?[\d]*\.[\d]*)\],\n?\[0,-32\]", latlong_content
    )
    driver.find_element_by_class_name("i4ewOd-pzNkMb-ornU0b-b0t70b-Bz112c").click()
    single_store = driver.find_elements_by_class_name("HzV7m-pbTTYe-ibnC6b-V67aGc")
    num = 0
    for row in single_store:
        driver.execute_script("arguments[0].click();", row)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "qqvbed-p83tee-lTBxed"))
        )
        location_name = row.find_element_by_xpath(
            '//*[@id="featurecardPanel"]/div/div/div[4]/div[1]/div[1]/div[2]'
        ).text.strip()
        content = (
            driver.find_element_by_xpath(
                '//*[@id="featurecardPanel"]/div/div/div[4]/div[1]/div[2]/div[2]'
            )
            .text.replace("\n\n", ",")
            .replace("\n", ",")
            .strip()
        )
        if "Summer Opening Hours" in content:
            info = content.split("Summer Opening Hours")
        else:
            if "Opening Hours:" in content:
                info = content.split("Opening Hours:")
            else:
                info = content.split("Opening Hours")
        addr = info[0].split("Tel:")
        raw_address = re.sub(
            r"Diesel.*", "", addr[0].replace(location_name + ",", "").strip(",").strip()
        )
        street_address, city, state, zip_postal = getAddress(raw_address)
        phone = re.sub(
            r",?Diesel.*", "", addr[1].split(",")[0].replace(".", " ").strip()
        )
        try:
            hours_of_operation = (
                re.sub(
                    r"\(May-Sept\),|,?Diesel.*|,24-Hour.*|\(Winter:\s+\d{1,2}am\s+–\s+\d{1,2}pm\)|,Winter Opening Hours.*",
                    "",
                    info[1],
                )
                .strip(",")
                .strip()
            )
        except:
            hours_of_operation = MISSING
        latitude, longitude = latlong[num]
        country_code = "UK"
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=LOCATION_URL,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=MISSING,
            phone=phone,
            location_type=MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )
        num += 1
    driver.quit()


def scrape():
    log.info("Start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
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
