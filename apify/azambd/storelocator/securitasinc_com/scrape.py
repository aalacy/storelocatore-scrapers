import time
from lxml import html

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sglogging import sglog

# F
MISSING = "<MISSING>"
website = "https://www.securitasinc.com"
session = SgRequests().requests_retry_session()
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
}


def request_with_retries(url):
    response = session.get(url, headers=headers)
    return html.fromstring(response.text, "lxml")


def pullAllOfficeLinks():
    officePage = "https://www.securitasinc.com/contact-us/office-listing/"
    body = request_with_retries(officePage)
    contactPages = body.xpath('//div[@class="text-block__inner"]/table')

    for contactPage in contactPages:
        pageLinks = contactPage.xpath(".//a/@href")
        return pageLinks

    return []


def fetchData():
    allOfficePages = pullAllOfficeLinks()
    log.info(f"Total Office = {len(allOfficePages)}")

    known_issues = [
        "https://www.securitasinc.com/Contact-Us/District-of-Columbia/",
        "https://www.securitasinc.com/contact-us/Illinois/Marion/",
    ]

    known_issues.sort()

    for officePage in allOfficePages:
        officeLink = website + officePage
        log.info(f"State Page = {officeLink}")
        cpBody = request_with_retries(officeLink)
        contactLinks = cpBody.xpath('//ul[@class="office-listing-page__locations"]')

        for clink in contactLinks:
            allContacts = clink.xpath(".//a/@href")
            log.info(f"Total Contact Pages = {len(allContacts)}")
            for contact in allContacts:
                url = website + contact
                # known Issue
                if any(url in s for s in known_issues):
                    continue

                log.info(f"Scrapping {url} ...")

                body = request_with_retries(url)
                try:
                    location_name = body.xpath("//h1/text()")[0].strip()
                except:
                    location_name = MISSING

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
                        try:
                            state = result["li-State:"]
                        except:
                            state = MISSING

                yield SgRecord(
                    locator_domain=website,
                    page_url=url,
                    location_name=location_name,
                    street_address=result["StreetAddress"],
                    city=result["Town"],
                    state=state,
                    country_code="US",
                    zip_postal=result["Zip"],
                    phone=result["Phone"].split(" or ")[0],
                    latitude=str(result["Latitude"]),
                    longitude=str(result["Longitude"]),
                )


def scrape():
    count = 0
    start = time.time()
    result = fetchData()
    with SgWriter() as writer:
        for rec in result:
            writer.write_row(rec)
            count = count + 1

    end = time.time()
    log.info(f"Total contact-us = {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
