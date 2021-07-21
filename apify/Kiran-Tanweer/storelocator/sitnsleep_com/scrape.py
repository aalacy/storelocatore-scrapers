import ssl
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import sglog
from sgselenium import SgChrome
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from lxml import html

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


website = "sitnsleep_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.sitnsleep.com/"
MISSING = "<MISSING>"


def fetch_data():
    with SgChrome(
        executable_path=ChromeDriverManager().install(), is_headless=True
    ) as driver:
        driver.get("https://www.sitnsleep.com/storelocator")
        WebDriverWait(driver, 40)
        response_text = driver.page_source
        data = html.fromstring(response_text, "lxml")
        js_app_slug = data.xpath('//link[contains(@href, "/js/app")]/@href')
        js_app_slug = "".join(js_app_slug)
        log.info(f"slug: {js_app_slug}")
        url = f"{DOMAIN}{js_app_slug}"
        log.info(f"js app file URL: {url}")
        driver.get(url)
        response_text2 = driver.page_source
    soup = BeautifulSoup(response_text2, "html.parser")
    bs = str(soup)
    bs = bs.split("stores:")[1].split('}}};t["a"]=s},')[0]
    locs = bs.split("{about:")
    for loc in locs:
        if loc != "[":
            page_url = loc.split('route:"')[1].split('",')[0]
            page_url = "https://www.sitnsleep.com/store/" + page_url
            page_url = page_url.replace('"},', "")
            log.info(page_url)
            loc = loc.split("address:")[1].split(",reviews:")[0]
            location_name = loc.split(',name:"')[1].split('",')[0]

            street_address = loc.split(',street:"')[1].split('",zip:')[0]
            street_address = street_address.replace("<br/>", " ")
            if "Long Beach" in location_name:
                street_address = (
                    loc.split(',street:"')[1].split('",zip:')[0].rsplit(";")[-1]
                )
            if "(" in street_address:
                street_address = street_address.split("(")[0]
            if "&" in street_address:
                street_address = street_address.split("&")[0]
            city = loc.split('{city:"')[1].split('",')[0]
            state = loc.split(',state:"')[1].split('",')[0]
            zip_postal = loc.split(',zip:"')[1].split('"}')[0]
            country_code = loc.split(',country:"')[1].split('",')[0]
            hours_of_operation = loc.split(",hours:'")[1].split("',l")[0]
            hours_of_operation = (
                hours_of_operation.replace("&lt;p&gt;&lt;strong&gt;", "")
                .replace("&lt;p&gt;", "")
                .replace("&lt;/strong&gt;", "")
                .replace("&lt;/p&gt;", "")
            )
            hours_of_operation = (
                hours_of_operation.replace("pm", "pm ")
                .replace('class="location__hours-saturday"&gt;', "")
                .replace('class="location__hours-sunday"&gt;', "")
                .replace("&lt;strong ", "")
            )
            latitude = loc.split('latitude:"')[1].split('",')[0]
            longitude = loc.split('longitude:"')[1].split('",')[0]
            phone = loc.split(',phone:"')[1].split('",')[0].replace('"', "")
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
