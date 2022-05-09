import json
from lxml import html

from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

MISSING = SgRecord.MISSING
website = "https://www.istorage.com"
session = SgRequests()
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


def getHourOperation(url):
    hourOperations = []
    response = request_with_retries(url)
    body = html.fromstring(response.text, "lxml")
    parentDivs = body.xpath("//div[@class='facility-properties-office-hours']")
    for parentDiv in parentDivs:
        headerText = parentDiv.xpath(".//p/text()")
        isOfficeHourAvailable = (
            len(headerText) > 1 and "Office Hours" in headerText[1].strip()
        )
        if not isOfficeHourAvailable:
            continue
        hourDivs = parentDiv.xpath(".//table/tr/td/text()")
        if len(hourDivs) % 2 == 1:
            hourDivs = hourDivs[:-1]

        for index in range(0, int(len(hourDivs) / 2)):
            hourOperations.append(f"{hourDivs[index * 2]} {hourDivs[index * 2 + 1]}")
        return ", ".join(hourOperations)
    return MISSING


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

            try:
                geoLocation = geoLocations[index]
                latitude = geoLocation[1]
                longitude = geoLocation[2]
            except:
                latitude = MISSING
                longitude = MISSING

            facilityCard = facilityCards[index]

            url = facilityCard.xpath('.//p[@class="facility-name"]/a/@href')[0]
            if url in allUrls:
                continue
            allUrls.append(url)

            try:
                store_number = url.split("-")[len(url.split("-")) - 1]
                if "testtoken" in str(store_number):
                    store_number = store_number.split("||")[1]
            except:
                store_number = MISSING
            try:
                location_name = getTextFromDiv(
                    facilityCard.xpath('.//p[@class="facility-name"]/a/text()')
                )
            except:
                location_name = MISSING
            try:

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
            except:
                street_address = zip = state = city = MISSING
            try:
                phone = getTextFromDiv(
                    facilityCard.xpath('.//p[@class="facility-phone"]/a/text()')
                )
            except:
                phone = MISSING

            page_url = website + url

            if "securcareselfstorage.com" in str(url):
                page_url = url
                hours_of_operation = MISSING
            else:
                hours_of_operation = getHourOperation(website + url)

            yield SgRecord(
                locator_domain=website,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip,
                country_code="US",
                store_number=store_number,
                phone=phone,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetchData()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
