import re
import time
from lxml import html

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord

DOMAIN = "annabella.ca"

website = "https://annabella.ca"
MISSING = "<MISSING>"


session = SgRequests().requests_retry_session()
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
}


def request_with_retries(url):
    return session.get(url, headers=headers)


def getPhone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
        return phone
    return phone


def fetchStores():
    response = session.get(f"{website}/pages/store-location")
    body = html.fromstring(response.text, "lxml")
    mainDiv = body.xpath('//div[contains(@class, "PageContent")]')[0]

    location_names = mainDiv.xpath('//div[contains(@class, "PageContent")]/h4/text()')
    map_links = mainDiv.xpath('//div[contains(@class, "PageContent")]/p/a/@href')
    p1s = mainDiv.xpath('//div[contains(@class, "PageContent")]/p/text()')

    allPs = []
    ps = []
    for p in p1s:
        if len(p) == 1:
            allPs.append(ps)
            ps = []
        else:
            ps.append(p)
    allPs.append(ps)

    stores = []
    count = 0
    for ps in allPs:
        cs = ps[1].split(",")
        stores.append(
            {
                "location_name": location_names[count].strip(),
                "map_link": map_links[count].strip(),
                "street_address": f"{ps[0]}, {ps[2]}".strip(),
                "zip_postal": ps[3].strip(),
                "phone": getPhone(" ".join(ps)),
                "city": cs[0].strip(),
                "state": cs[1].strip(),
            }
        )
        count = count + 1

    return stores


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


def fetchData():
    stores = fetchStores()
    log.info(f"Total stores = {len(stores)}")
    for store in stores:
        latitude, longitude = getLatLongFromGMap(store["map_link"])
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=website,
            location_type="Clothing Stores",
            location_name=store["location_name"],
            street_address=store["street_address"],
            city=store["city"],
            zip_postal=store["zip_postal"],
            state=store["state"],
            phone=store["phone"],
            country_code="CA",
            latitude=latitude,
            longitude=longitude,
        )


def scrape():
    log.info("Started")
    count = 0
    start = time.time()
    result = fetchData()
    with SgWriter() as writer:
        for rec in result:
            writer.write_row(rec)
            count = count + 1

    end = time.time()
    log.info(f"Total rows added = {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
