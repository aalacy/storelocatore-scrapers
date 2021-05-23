import re
import time
import json
import math
from lxml import html
from concurrent.futures import ThreadPoolExecutor

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord

website = "http://www.primerica.com"
max_workers = 1
MISSING = "<MISSING>"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

session = SgRequests().requests_retry_session()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetchConcurrentSingle(data):
    try:
        response = session.get(data["url"], headers=headers)
        body = html.fromstring(response.text, "lxml")
        return {"data": data, "body": body, "response": response.text}
    except Exception as e:
        log.error(f"can't load {data['url']} and Err:{e}")


def fetchConcurrentList(list, occurrence=max_workers):
    output = []
    total = len(list)
    reminder = math.floor(total / 50)
    if reminder < occurrence:
        reminder = occurrence

    count = 0
    with ThreadPoolExecutor(
        max_workers=occurrence, thread_name_prefix="fetcher"
    ) as executor:
        for result in executor.map(fetchConcurrentSingle, list):
            count = count + 1
            if count % reminder == 0:
                log.debug(f"Concurrent Operation count = {count}")
            if result is not None:
                output.append(result)
    return output


def fetchStores():
    response = session.get(f"{website}/public/locations.html", headers=headers)
    body = html.fromstring(response.text, "lxml")
    states = []
    countryList = body.xpath('//section[@class="content locList"]')

    countCountry = 0
    for stateDiv in countryList:
        if countCountry == 0:
            country_code = "CA"
        else:
            country_code = "US"
        countCountry = 1

        for stateA in stateDiv.xpath(".//a"):
            states.append(
                {
                    "url": f"{website}/public/{stateA.xpath('.//@href')[0]}",
                    "state": stateA.xpath(".//text()")[0],
                    "country_code": country_code,
                }
            )
    log.info(f"Total state = {len(states)}")

    zips = []
    urls = []
    for state in fetchConcurrentList(states):
        data = state["data"]
        body = state["body"]
        mainDiv = body.xpath("//main")[0]
        for A in mainDiv.xpath(".//a"):
            url = website + A.xpath(".//@href")[0]
            zip_postal = A.xpath(".//text()")[0]
            if url in urls:
                continue
            urls.append(url)
            zips.append(
                {
                    "url": url,
                    "zip_postal": zip_postal,
                    "state": data["state"],
                    "country_code": data["country_code"],
                }
            )
    log.info(f"Total zip code = {len(zips)}")

    storeList = []
    urls = []
    zipCount = 0
    for zip in zips:
        response = session.get(zip["url"], headers=headers)
        body = html.fromstring(response.text, "lxml")
        mainDiv = body.xpath("//main")[0]
        page_urls = mainDiv.xpath(".//a/@href")
        count = 0
        for page_url in page_urls:
            page_url = page_url + "&origin=customStandard"
            if page_url in urls:
                continue
            count = count + 1
            urls.append(page_url)
            storeList.append(
                {
                    "url": page_url,
                    "page_url": page_url,
                    "zip_postal": zip["zip_postal"],
                    "state": zip["state"],
                    "country_code": zip["country_code"],
                }
            )
        if len(page_urls) > 0:
            log.debug(
                f"{zip['state']}:{zip['zip_postal']}-->{zip['url']}--> total {len(page_urls)} inserted {count}"
            )
        zipCount = zipCount + 1

        if zipCount % 50 == 0:
            log.debug(f"Updated {zipCount} Total store found {len(storeList)} ...")
    log.info(f"Total store link = {len(storeList)}")

    stores = []
    for store in fetchConcurrentList(storeList):
        stores.append(
            {
                "page_url": store["data"]["page_url"],
                "zip_postal": store["data"]["zip_postal"],
                "state": store["data"]["state"],
                "country_code": store["data"]["country_code"],
                "response": store["response"],
                "body": store["body"],
            }
        )

    return stores


def getScriptWithAddress(body):
    scripts = body.xpath("//script/text()")
    for script in scripts:
        if '"addressLocality"' in script:
            return json.loads(script, strict=False)
    return None


def getVarName(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def getJSONObjectVariable(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = getVarName(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
    return value


def getJSObject(response, varName):
    JSObject = re.findall(f'{varName} = "(.+?)";', response)
    if JSObject is None or len(JSObject) == 0:
        return MISSING
    return JSObject[0]


def fetchData():
    stores = fetchStores()
    log.info(f"Total stores = {len(stores)}")

    for store in stores:
        body = store["body"]
        response = store["response"]
        page_url = store["page_url"]
        zip_postal = store["zip_postal"]
        state = store["state"]
        country_code = store["country_code"]

        location_name = body.xpath('.//div[@class="divResumeName"]/text()')
        if len(location_name) > 0:
            location_name = location_name[0]
        else:
            location_name = MISSING

        jsonData = getScriptWithAddress(body)

        street_address = getJSObject(response, "addressLine1")
        addressLine2 = getJSObject(response, "addressLine2")
        if street_address == MISSING:
            street_address = addressLine2
        elif addressLine2 != MISSING:
            street_address = street_address + " " + addressLine2

        city = getJSObject(response, "addressCity")
        if getJSObject(response, "addressState") != MISSING:
            state = getJSObject(response, "addressState")

        phone = getJSONObjectVariable(jsonData, "address.telephone", MISSING)
        raw_address = ""
        if street_address != MISSING:
            raw_address = street_address

        if city != MISSING:
            raw_address = raw_address + " " + city

        if state != MISSING:
            raw_address = raw_address + ", " + state

        if zip_postal != MISSING:
            raw_address = raw_address + " " + zip_postal

        yield SgRecord(
            locator_domain=website,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=zip_postal,
            state=state,
            country_code=country_code,
            phone=phone,
            raw_address=raw_address,
        )
    return []


def scrape():
    start = time.time()
    result = fetchData()
    with SgWriter() as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
