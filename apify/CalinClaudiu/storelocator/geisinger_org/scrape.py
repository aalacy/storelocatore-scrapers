from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from tenacity import retry, stop_after_attempt
import tenacity
import ssl
from lxml import html
import json
import time

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("geisinger_org")
MISSING = SgRecord.MISSING
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(f"user-agent={USER_AGENT}")

headers = {
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}

LOCATION_URL = "http://locations.geisinger.org/?utm_source=Locations%20Page&utm_medium=Web&utm_campaign=Locations%20CTA"


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(60))
def get_response(urlnum, url):
    with SgRequests(timeout_config=600) as http:
        logger.info(f"[{urlnum}] Pulling the data from: {url}")
        r = http.get(url, headers=headers)
        if r.status_code == 200 or r.status_code == 500:
            logger.info(f"HTTP Status Code: {r.status_code}")
            return r
        raise Exception(f"{urlnum} : {url} >> Temporary Error: {r.status_code}")


def fix_address(x):

    flag = 0
    unwanted = ["Markets", "Plaza", "Center", "Hospital", "FLoor", "Clinic"]
    isdigit = [0, 0]
    h = []
    added = [0, 0]

    for i in range(len(x)):
        if any(j.isdigit() for j in x[i]):
            isdigit[i] = 1
        if "Level 2:" in x[i]:
            x[i] = x[i].split("Level 2:", 1)[1].strip()
    for i in range(len(x)):
        if any(j in x[i] for j in unwanted):
            flag += 1
            if i == 0:
                if isdigit[0] == 1:
                    h.append(x[0])
                    added[0] = 1
                if len(x[1]) > 3 and isdigit[1] == 1:
                    if added[1] == 0:
                        h.append(x[1])
                        added[1] = 1
                else:
                    if added[0] == 0:
                        h.append(x[0])
                        added[0] = 1
            if i == 1 and added[0] == 0:
                h.append(x[0])
                added[0] = 1
        else:
            if added[i] == 0:
                h.append(x[i])
                added[i] = 1
    if flag > 0:
        for i in range(len(h)):
            try:
                h[i] = fix_address(h[i].split(",", 1))
            except Exception:
                h[i] = h[i]
    h = " ".join(h).replace("<br>", " ").strip()
    return h


def get_loc_type(oservices):
    sel_os = html.fromstring(oservices)
    ostext = sel_os.xpath("//text()")
    ostext = [" ".join(i.split()) for i in ostext]
    ostext = [i for i in ostext if i]
    location_type = "; ".join(ostext)
    return location_type


def get_hoo(officehours):
    sel_hoo = html.fromstring(officehours)
    hoo_data = sel_hoo.xpath("//text()")
    hoo_data = [" ".join(i.split()) for i in hoo_data]
    hoo_data = [i for i in hoo_data if i]
    hoo_data = "; ".join(hoo_data)
    return hoo_data


def get_driver(url, class_name, driver=None):
    if driver is not None:
        driver.quit()
    x = 0
    while True:
        x = x + 1
        try:
            driver = webdriver.Chrome(
                executable_path=ChromeDriverManager().install(), options=chrome_options
            )
            driver.get(url)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            logger.info(f"Success : {url}")
            break
        except Exception as e:
            driver.quit()
            if x == 5:
                raise Exception(f"Fix The issue {e} | {url}")
            continue
    return driver


def fetch_data():
    r = get_response(0, LOCATION_URL)
    sel = html.fromstring(r.text, "lxml")
    data_raw = sel.xpath(
        '//script[contains(@type, "text/javascript") and contains(text(), "var results")]/text()'
    )
    data_raw = "".join(data_raw)
    dr1 = data_raw.split("var results=")[1].strip().rstrip(";")
    json_data = json.loads(dr1)
    for idx, _ in enumerate(json_data[0:]):
        store_number = _["CLINICID"]
        store_url = f"https://locations.geisinger.org/details.cfm?id={store_number}"
        logger.info(f"[{idx}] Pulling the data from {store_url}")
        lat = None
        lng = None
        try:
            class_name_pg_sec_full = "page-section--full "
            driver = get_driver(store_url, class_name_pg_sec_full)
            element = driver.find_element_by_tag_name("iframe")
            driver.execute_script("arguments[0].scrollIntoView();", element)
            time.sleep(3)
            driver.switch_to.frame(element)
            coordText = driver.page_source
            sel_latlng = html.fromstring(coordText, "lxml")
            latlng = "".join(sel_latlng.xpath('//a[contains(@href, "maps?ll=")]/@href'))
        except Exception as e:
            logger.info(f"Fix the latlng issue {e} | {store_url}")
        try:
            lat = latlng.split("ll=", 1)[1].split("&", 1)[0].split(",")[0]
            lng = latlng.split("ll=", 1)[1].split("&", 1)[0].split(",")[1]
        except:
            lat = "<INACCESSIBLE>"
            lng = "<INACCESSIBLE>"
        if str(lat) == "0":
            lat = "<INACCESSIBLE>"
        if str(lng) == "0":
            lng = "<INACCESSIBLE>"

        logger.info(f"latlng: {lat}, {lng}")

        sta_list = []
        sta1 = _["ADDRESS1"]
        sta2 = _["ADDRESS2"]
        sta_list.append(sta1)
        sta_list.append(sta2)
        location_type = None
        hours_of_operation = None
        officehours = _["OFFICEHOURS"]
        try:
            if officehours:
                hours_of_operation = get_hoo(officehours)
            else:
                hours_of_operation = MISSING
        except:
            hours_of_operation = MISSING

        otherservices = _["OTHERSERVICES"]
        try:
            if otherservices:
                location_type = get_loc_type(otherservices)
            else:
                location_type = MISSING
        except:
            location_type = MISSING
        zip_postal = None
        zc = _["ZIPCODE"]
        zc = zc.replace("*", "").strip()
        if zc:
            zip_postal = zc
        else:
            zip_postal = MISSING
        item = SgRecord(
            locator_domain="geisinger.org",
            page_url=store_url,
            location_name=_["NAME"] or MISSING,
            street_address=fix_address(sta_list),
            city=_["CITY"] or MISSING,
            state=_["STATE"] or MISSING,
            zip_postal=zip_postal,
            country_code="US",
            store_number=store_number,
            phone=_["PHONE"],
            location_type=location_type,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hours_of_operation,
            raw_address=MISSING,
        )
        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
