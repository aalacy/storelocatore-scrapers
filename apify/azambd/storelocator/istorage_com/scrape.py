import json
from lxml import html

from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

MISSING = "<MISSING>"
website = "https://www.istorage.com"
session = SgRequests().requests_retry_session()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(url):
    return session.get(url)


def fetchCityLinks():
    response = request_with_retries(website + "/storage")
    body = html.fromstring(response.text, "lxml")
    return body.xpath("//ul[@id='state-list']/li/a/@href")


def fetchCityStores(cityLink):
    response = request_with_retries(f"{website}{cityLink}")
    return html.fromstring(response.text, "lxml")


def getScriptVariable(body, varName):
    scripts = body.xpath("//script/text()")
    for script in scripts:
        if "var facilities = " in script:
            data = script.split(f"var {varName} = ", 1)[-1].rsplit(";", 1)[0].strip()
            data = script.split("var facilities =")[1]
            data = data.split(";")[0]

            if len(data) > 0:
                return json.loads(data)
    return []


def getTextFromDiv(values):
    result = []
    for value in values:
        value = value.replace("\n", "").strip()
        if len(value):
            result.append(value)
    return " ".join(result).strip()


def fetchData():
    cityLinks = fetchCityLinks()
    log.info(f"Cities = {len(cityLinks)}")
    allUrls = []

    for cityLink in cityLinks:
        cityResponse = fetchCityStores(cityLink)
        facilityCards = cityResponse.xpath("//div[@class='well facility-card']")
        geoLocations = getScriptVariable(cityResponse, "facilities")
        log.info(f"city = {cityLink}; stores= {len(geoLocations)}")
        if len(geoLocations) == 0 or len(facilityCards) != len(geoLocations):
            return []

        for index in range(0, len(geoLocations)):
            if len(geoLocations[index]) < 2 or len(facilityCards) < index:
                continue
            geoLocation = geoLocations[index]
            facilityCard = facilityCards[index]

            url = facilityCard.xpath('.//p[@class="facility-name"]/a/@href')[0]

            if url in allUrls:
                continue
            allUrls.append(url)

            store_number = url.split("-")[len(url.split("-")) - 1]

            location_name = getTextFromDiv(
                facilityCard.xpath('.//p[@class="facility-name"]/a/text()')
            )
            address = getTextFromDiv(
                facilityCard.xpath('.//p[@class="facility-address"]/text()')
            )
            address_parts = address.split(",")
            street_address = address_parts[len(address_parts) - 1]
            street_parts = street_address.strip().split(" ")
            zip = str(street_parts[len(street_parts) - 1].strip())
            state = str(street_parts[len(street_parts) - 2].strip())
            street_address = address.replace("," + street_address, "")
            street_parts2 = street_address.split(" ")
            city = street_parts2[len(street_parts2) - 1]
            phone = getTextFromDiv(
                facilityCard.xpath('.//p[@class="facility-phone"]/a/text()')
            )

            yield SgRecord(
                locator_domain=website,
                page_url=website + url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip,
                country_code="US",
                store_number=store_number,
                phone=phone,
                location_type=MISSING,
                latitude=geoLocation[1],
                longitude=geoLocation[2],
                hours_of_operation=MISSING,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetchData()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
