from xml.etree import ElementTree as ET
import time
import json
import csv

from lxml import html

from urllib.parse import urlparse

from sgselenium import SgChrome
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "daynurseries.co.uk"
website = "https://www.daynurseries.co.uk"
MISSING = "<MISSING>"

headers1 = {
    "authority": "www.daynurseries.co.uk",
    "pragma": "no-cache",
    "cache-control": "no-cache",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9",
    "cookie": 'visid_incap_927307=3oaEFGlNTVOtB8+TQ4eQ6bQ6kGAAAAAAQUIPAAAAAAD/ku2k71f1yaivILPzxrg9; _ga=GA1.3.1472771204.1620064951; _gid=GA1.3.1236226554.1620064951; CFCLIENT_DN=""; CFID=122574883; CFTOKEN=93e43837e8c7ecba-4E7B99D3-D5A1-46C4-CEF3F5C9BE832DD9; RECENTVIEWED=65432219576; CFGLOBALS=urltoken%3DCFID%23%3D122574883%26CFTOKEN%23%3D93e43837e8c7ecba%2D4E7B99D3%2DD5A1%2D46C4%2DCEF3F5C9BE832DD9%23lastvisit%3D%7Bts%20%272021%2D05%2D05%2006%3A42%3A10%27%7D%23hitcount%3D36%23timecreated%3D%7Bts%20%272021%2D05%2D03%2019%3A02%3A29%27%7D%23cftoken%3D93e43837e8c7ecba%2D4E7B99D3%2DD5A1%2D46C4%2DCEF3F5C9BE832DD9%23cfid%3D122574883%23; incap_ses_968_927307=LQxSBOFrVzCgVACWIgdvDTIwkmAAAAAA3WTStY3J/wnHJ+g+CyAhCQ==; __atuvc=7%7C18; __atuvs=60923033a602cd14000; visid_incap_927307=i7yyIkqFQKC2awh34BKTP9g3kmAAAAAAQUIPAAAAAADFegi96Ptu2cKwIcPeKrOE; CFGLOBALS=urltoken%3DCFID%23%3D122574883%26CFTOKEN%23%3D93e43837e8c7ecba%2D4E7B99D3%2DD5A1%2D46C4%2DCEF3F5C9BE832DD9%23lastvisit%3D%7Bts%20%272021%2D05%2D05%2007%3A58%3A09%27%7D%23hitcount%3D39%23timecreated%3D%7Bts%20%272021%2D05%2D03%2019%3A02%3A29%27%7D%23cftoken%3D93e43837e8c7ecba%2D4E7B99D3%2DD5A1%2D46C4%2DCEF3F5C9BE832DD9%23cfid%3D122574883%23; incap_ses_968_927307=HXTeTm2Loxk3PkyYIgdvDd2+k2AAAAAAD5YVs585xhJkffRFoPFcmQ==',
}

CSV_FILENAME = "data.csv"
COLUMNS = [
    "page_url",
    "location_name",
    "street_address",
    "city",
    "state",
    "zip_postal",
    "country_code",
    "store_number",
    "phone",
    "location_type",
    "latitude",
    "longitude",
    "locator_domain",
    "hours_of_operation",
    "brand_website",
]


session = SgRequests().requests_retry_session()
log = sglog.SgLogSetup().get_logger(logger_name=website)
driver = SgChrome(is_headless=True).driver()


def fetchStores():
    stores = []
    response = session.get(website + "/sitemaps/profile.xml", headers=headers1)
    root = ET.fromstring(response.text)
    for elem in root:
        for var in elem:
            if "loc" in var.tag:
                stores.append(var.text)
    return stores


def fetchSinglePage(data_url, findRedirect=False):
    session = SgRequests()
    driver.get(data_url)
    incap_str = "/_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3"
    incap_url = website + incap_str
    session.get(incap_url)

    for request in driver.requests:
        headers = request.headers
        try:
            response = session.get(data_url, headers=headers)
            response_text = response.text

            test_html = response_text.split("div")

            if findRedirect and response_text.find("window.location.replace") > -1:
                try:
                    return response_text.split("window.location.replace('")[1].split(
                        "')"
                    )[0]
                except Exception:
                    continue
            elif len(test_html) < 2:
                continue
            else:
                return {
                    "response": response_text,
                    "hours_of_operation": getHoursOfOperation(),
                    "phone": getPhone(),
                }

        except Exception:
            continue


def getHoursOfOperation():
    try:
        hours_of_operation = []
        profileRows = driver.find_elements_by_xpath(
            "//div[contains(@class, 'profile-rows')]/div/ul"
        )

        for profileRow in profileRows:
            texts = []
            for li in profileRow.find_elements_by_xpath(".//li"):
                texts.append(li.text)
            if len(texts) > 1 and texts[0] == "Opening Days":
                hours_of_operation.append(f"Opening Days: {texts[1].strip()}")
            if len(texts) > 1 and texts[0] == "Opening Hours":
                hours_of_operation.append(f"Opening Hours: {texts[1].strip()}")
            if len(texts) > 1 and texts[0] == "When Closed":
                hours_of_operation.append(f"Closed: {texts[1].strip()}")
        hours_of_operation = "; ".join(hours_of_operation)
        return hours_of_operation
    except Exception as e:
        log.error("error loading hours_of_operation", e)
    return MISSING


def getPhone():
    try:
        driver.find_element_by_xpath("//a[@id='brochure_phone']").click()

        phones = driver.find_elements_by_xpath(
            "//div[@id='contacts_telephone_general']/p/strong/a"
        )
        for phone in phones:
            return phone.get_attribute("innerHTML")
    except Exception as e:
        log.error("error loading phone", e)
    return MISSING


def getScriptWithGeo(body):
    scripts = body.xpath("//script/text()")
    for script in scripts:
        if '"geo":{' in script:
            return json.loads(script)
    return None


def fetchData():
    stores = fetchStores()
    log.info(f"Total stores = {len(stores)}")
    result = []
    for page_url in stores:

        split_url = page_url.split("/")
        if len(split_url) != 6:
            log.error(f"Ignored {page_url} ...")
            continue
        log.info(f"Scrapping {page_url} ...")
        store_number = split_url[5]
        store_response = fetchSinglePage(page_url)

        hours_of_operation = store_response["hours_of_operation"]
        phone = store_response["phone"].strip()
        body = html.fromstring(store_response["response"], "lxml")

        geoJSON = getScriptWithGeo(body)
        location_name = (geoJSON["name"].strip()).split(" at ")
        location_name = location_name[0]

        street_address = geoJSON["address"]["streetAddress"].strip()
        city = geoJSON["address"]["addressLocality"].strip()
        state = geoJSON["address"]["addressRegion"].strip()
        zip = geoJSON["address"]["postalCode"].strip()

        latitude = str(geoJSON["geo"]["latitude"])
        longitude = str(geoJSON["geo"]["longitude"])

        redirect_urls = body.xpath('//a[contains(@class, "button-website")]/@href')
        if len(redirect_urls) > 0:
            brand_website = fetchSinglePage(redirect_urls[0], True)
            brand_website = (urlparse(brand_website).netloc).replace("www.", "")
        else:
            brand_website = MISSING

        result.append(
            {
                "page_url": page_url,
                "store_number": store_number,
                "location_name": location_name,
                "locator_domain": DOMAIN,
                "street_address": street_address,
                "city": city,
                "state": state,
                "zip_postal": zip,
                "latitude": latitude,
                "longitude": longitude,
                "hours_of_operation": hours_of_operation,
                "brand_website": brand_website,
                "phone": phone,
                "country_code": "UK",
                "location_type": MISSING,
            }
        )

    driver.quit()
    return result


def generatingOutput(result):
    log.info("generating Output ...")
    count = 0
    with open(CSV_FILENAME, "w") as file:
        writer = csv.writer(file)
        writer.writerow(COLUMNS)

        for data in result:
            count = count + 1
            row = []
            for column in COLUMNS:
                if column in data and data[column] != "":
                    row.append(data[column])
                else:
                    row.append(MISSING)
            writer.writerow(row)
    log.info(f"Total Rows Added= {count}")


def scrape():
    start = time.time()
    result = fetchData()
    generatingOutput(result)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
