import time
from lxml import html

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord

DOMAIN = "westcornwallpasty.co.uk"
website = "http://westcornwallpasty.co.uk"
locationUrl = f"{website}/visit-us"
MISSING = "<MISSING>"


session = SgRequests().requests_retry_session()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def getLatLongArray(body):
    scripts = body.xpath("//script/text()")
    for script in scripts:
        if "window.APP_INITIALIZATION_STATE" in script:
            data = (
                script.split("window.APP_INITIALIZATION_STATE=[[[")[-1]
                .rsplit("]", 1)[0]
                .strip()
            )
            return data.split("]")[0].split(",")


def getLatLongFromGMap(url):
    response = session.get(url)
    body = html.fromstring(response.text, "lxml")
    data = getLatLongArray(body)
    return data[1], data[2]


def remove_empty_string_from_array(param):
    data = param
    while True:
        try:
            data.remove("")
        except:
            return data


def fetchStores():
    response = session.get(locationUrl)
    body = html.fromstring(response.text, "lxml")
    return body.xpath('//div[@class="storeLocator"]/div/ul/li/ul/li')


def fetchData():
    stores = fetchStores()
    log.info(f"Total stores = {len(stores)}")
    for store in stores:
        country_code = "UK"
        map_link = store.xpath(".//a[@target='_blank']")[0]
        location_name = map_link.xpath(".//text()")[0].strip()
        phone = store.xpath('.//a[@class="visitUsTel"]/text()')

        if len(phone) == 0:
            phone = MISSING
        else:
            phone = phone[0].replace("Tel: ", "").strip()

        address = store.xpath(".//p/text()")[0]
        if "\r\n" in address:
            address = address.split("\r\n")
        else:
            address = address.split(", ")
        address = remove_empty_string_from_array(address)
        raw_address = ", ".join(address)

        zip_postal = address.pop()
        zip_data = zip_postal.split(" ")
        zip_data = remove_empty_string_from_array(zip_data)
        if len(zip_data) > 2:
            zip_postal = " ".join(zip_data[-2:]).strip()
            city = " ".join(zip_data[:-2]).strip()
        else:
            city = address.pop().strip()
        city = city[:-1] if city.endswith(",") else city
        street_address = " ".join(address)

        hours_of_operation = (
            "".join(store.xpath(".//div[@class='openingTimes']")[0].itertext())
            .replace("\n", "")
            .replace("\r", " ")
            .strip()
            .replace("  ", ";")
        )
        if len(hours_of_operation) == 0 or "N/A" == hours_of_operation:
            hours_of_operation = MISSING

        longitude, latitude = getLatLongFromGMap(map_link.xpath(".//@href")[0])

        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=locationUrl,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=zip_postal,
            country_code=country_code,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
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
