import time
import re
from lxml import html
from concurrent.futures import ThreadPoolExecutor

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sglogging import sglog

website = "https://www.mosquedirectory.co.uk"
MISSING = "<MISSING>"
max_workers = 24

session = SgRequests().requests_retry_session()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetchSingleState(stateDetails):
    response = session.get(stateDetails["stateLink"])
    body = html.fromstring(response.text, "lxml")
    cities = body.xpath('//li/a[contains(@href, "../../search")]')
    stateDetails["cities"] = cities
    return stateDetails


def fetchSingleCity(cityDetails):
    cityLink = cityDetails["cityLink"]
    cityName = cityDetails["cityName"]
    stateName = cityDetails["stateName"]
    countryName = cityDetails["countryName"]

    response = session.get(cityLink)
    body = html.fromstring(response.text, "lxml")
    mosqueLinks = body.xpath('///a[contains(text(), "Read More")]/@href')
    mosques = []
    for mosqueLink in mosqueLinks:
        mosques.append(
            {
                "page_url": website + mosqueLink.replace("..", ""),
                "city": cityName,
                "state": stateName,
                "country": countryName,
            }
        )
    return mosques


def fetchMosques():
    response = session.get(website + "/browse/")
    body = html.fromstring(response.text, "lxml")
    countries = body.xpath('//div[@id="section"]/a')
    log.info(f"Total Countries = {len(countries)}")
    mosques = []
    stateDetails = []
    cityDetails = []
    for countryNode in countries:
        countryName = countryNode.xpath(".//text()")[0]
        country = countryNode.xpath(".//@href")[0]
        countryPart = country.split("/")[0]
        countryLink = website + "/browse/" + country
        response = session.get(countryLink)
        body = html.fromstring(response.text, "lxml")
        states = body.xpath('//div[@id="directory_listing_body"]/h2/a')
        log.info(f"Total states in {countryName} = {len(states)}")
        for stateNode in states:
            stateName = stateNode.xpath(".//text()")[0].split(" (")[0]
            state = stateNode.xpath(".//@href")[0]
            stateLink = website + "/browse/" + countryPart + "/" + state
            stateDetails.append(
                {
                    "stateLink": stateLink,
                    "stateName": stateName,
                    "countryName": countryName,
                }
            )
    log.info(f"States = {len(stateDetails)}")

    with ThreadPoolExecutor(
        max_workers=max_workers, thread_name_prefix="fetcher"
    ) as executor:
        for stateCities in executor.map(fetchSingleState, stateDetails):
            for cityNode in stateCities["cities"]:
                cityName = cityNode.xpath(".//text()")[0].split(" (")[0]
                city = cityNode.xpath(".//@href")[0].replace("../../", "")
                cityLink = website + "/browse/" + city
                cityDetails.append(
                    {
                        "cityLink": cityLink,
                        "cityName": cityName,
                        "stateName": stateCities["stateName"],
                        "countryName": stateCities["countryName"],
                    }
                )
    log.info(f"Total cities = {len(cityDetails)}")

    count = 0

    duplicate = 0
    links = []
    with ThreadPoolExecutor(
        max_workers=max_workers, thread_name_prefix="fetcher"
    ) as executor:
        for cityMosques in executor.map(fetchSingleCity, cityDetails):
            count = count + 1
            for mosque in cityMosques:
                page_url = mosque["page_url"]
                if page_url in links:
                    duplicate = duplicate + 1
                else:
                    mosques.append(mosque)
                    links.append(page_url)
            if count % 100 == 0:
                log.info(
                    f"Cities discovers = {count}; mosques found = {len(mosques)} duplicate={duplicate}"
                )

    log.info(f"Total {duplicate} duplicate links found among all the mosques")
    return mosques


def getPhone(Source):
    phone = MISSING
    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
    return phone


def fetchSingleMosque(mosque):
    url = mosque["page_url"]
    urlParts = url.split("/")
    mosque["store_number"] = urlParts[len(urlParts) - 1]
    mosque["locator_domain"] = website
    mosque["location_name"] = MISSING
    mosque["location_type"] = MISSING
    mosque["street_address"] = MISSING
    mosque["zip_postal"] = MISSING
    mosque["raw_address"] = MISSING
    mosque["phone"] = MISSING

    response = session.get(url)
    body = html.fromstring(response.text, "lxml")
    header = body.xpath('//div[@id="result_list_header_details"]')
    if response.status_code != 200 or len(header) == 0:
        log.error(f"Can't load {url} :{response.status_code}")
        return None

    header = header[0]
    location_names = header.xpath(".//h2/text()")
    if len(location_names) > 0:
        mosque["location_name"] = location_names[0].strip()

    location_types = header.xpath('.//span[contains(@class, "tag-")]/text()')
    if len(location_types) > 0:
        mosque["location_type"] = location_types[0].strip()

    ps = header.xpath(".//p/text()")
    pbs = header.xpath(".//p/b/text()")

    for index, value in enumerate(pbs):
        if "ADDRESS" in value:
            address = ps[index].replace("\n", "").strip()
            addressParts = address.split(",")
            lenParts = len(addressParts)
            zip_postal = MISSING
            state = mosque["state"]
            city = mosque["state"]
            if lenParts > 2:
                city = addressParts[lenParts - 3].strip()
                state = addressParts[lenParts - 2].strip()
                zip_postal = addressParts[lenParts - 1].strip()

            street_address = (
                address.replace(f", {zip_postal}", "")
                .replace(f", {city}", "")
                .replace(f", {state}", "")
                .replace(f", {mosque['city']}", "")
                .replace(f", {mosque['state']}", "")
                .replace(f", {mosque['country']}", "")
                .strip()
            )

            if len(city) > 0:
                mosque["city"] = city
            if len(state) > 0:
                mosque["state"] = state
            if len(zip_postal) > 0:
                mosque["zip_postal"] = zip_postal

            mosque["street_address"] = street_address
            mosque["raw_address"] = address

        if "TEL" in value:
            phone = ps[index].replace("\n", "").strip()
            if phone == "none" or phone == "n/a" or phone == "N/A":
                phone = MISSING
            else:
                phone = getPhone(phone)

            mosque["phone"] = phone
    if mosque["zip_postal"] == "n/a" or mosque["zip_postal"] == "N/A":
        mosque["zip_postal"] = MISSING
    return mosque


def fetchData():
    mosques = fetchMosques()
    log.info(f"Total mosques found = {len(mosques)}")
    count = 0
    failed = 0
    with ThreadPoolExecutor(
        max_workers=max_workers, thread_name_prefix="fetcher"
    ) as executor:
        for details in executor.map(fetchSingleMosque, mosques):
            count = count + 1
            if count % 100 == 0:
                log.info(f"updated {count} mosques")
            if details is None:
                failed = failed + 1
                continue
            yield SgRecord(
                locator_domain=details["locator_domain"],
                store_number=details["store_number"],
                page_url=details["page_url"],
                location_name=details["location_name"],
                location_type=details["location_type"],
                street_address=details["street_address"],
                city=details["city"],
                zip_postal=details["zip_postal"],
                state=details["state"],
                country_code="UK",
                phone=details["phone"],
                raw_address=details["raw_address"],
            )

    log.error(f"{failed} failed responses ...")


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
    log.info(f"Total row added = {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
