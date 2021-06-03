import time
from lxml import html

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sglogging import sglog


website = "https://www.securitas.ca"
session = SgRequests().requests_retry_session()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(url):
    response = session.get(url)
    return html.fromstring(response.text, "lxml")


def fetchAllContactLinks():
    body = request_with_retries(website)
    headerLis = body.xpath('//li[@class="header__link--wrapper"]')

    for headerLi in headerLis:
        isContactUs = headerLi.xpath('.//a[@href="/contact-us/"]')
        if len(isContactUs) != 1:
            continue
        return headerLi.xpath('.//a[@class="card__link"]/@href')

    return []


def fetchData():
    allContacts = fetchAllContactLinks()
    log.info(f"Total contacts = {len(allContacts)}")

    contacts = []
    for contact in allContacts:
        url = website + contact
        log.info(f"Scrapping {url} ...")
        body = request_with_retries(url)

        location_name = body.xpath("//h1/text()")[0].strip()

        inputs = body.xpath('//div[@class="office-page__map"]/input')
        result = {}
        for input in inputs:
            name = input.xpath(".//@name")[0]
            value = input.xpath(".//@value")[0].strip()
            result[name] = value

        lis = body.xpath('//ul[@class="office-page__contact"]/li')
        for li in lis:
            values = li.xpath(".//div/text()")
            if len(values) > 1:
                result["li-" + values[0]] = values[1].strip()

        contacts.append(
            SgRecord(
                locator_domain=website,
                page_url=url,
                location_name=location_name,
                street_address=result["StreetAddress"],
                city=result["Town"],
                state=result["li-State:"],
                country_code=result["li-Country:"],
                zip_postal=result["Zip"],
                phone=result["Phone"].split(" or ")[0],
                latitude=str(result["Latitude"]),
                longitude=str(result["Longitude"]),
            )
        )
    return contacts


def scrape():
    start = time.time()
    result = fetchData()
    with SgWriter() as writer:
        for rec in result:
            writer.write_row(rec)

    end = time.time()
    log.info(f"Total contact-us = {len(result)}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
