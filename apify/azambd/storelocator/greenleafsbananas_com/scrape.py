import time
from lxml import html

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sglogging import sglog

locator_domain = "greenleafsbananas.com"
website = "https://locations.greenleafsbananas.com"
MISSING = "<MISSING>"
session = SgRequests().requests_retry_session()
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)


def fetchStores(location, stores):
    location = location.replace("../", "")
    response = session.get(website + location)
    body = html.fromstring(response.text, "lxml")
    As = body.xpath('//a[@class="c-directory-list-content-item-link"]')

    count = 0
    for A in As:
        link = A.xpath(".//@href")[0]
        link = link.replace("../", "")
        count = count + 1
        fetchStores("/" + link, stores)

    if count == 0:
        As = body.xpath(
            '//a[text()="View Details" and @class="c-location-grid-item-link"]/@href'
        )
        for link in As:
            link = link.replace("../", "")
            count = count + 1
            fetchStores("/" + link, stores)

    if count == 0:
        stores.append({"link": website + location, "body": body})

    return stores


def fetchData():
    stores = fetchStores("/US.html", [])
    log.info(f"Total stores found = {len(stores)}")

    for store in stores:
        page_url = store["link"]
        log.info(f"Page URL: {page_url}")

        body = store["body"]

        location_name = body.xpath(
            '//span[contains(@class, "location-name-geomodifier")]/text()'
        )[0].strip()
        street_address = body.xpath(
            '//span[contains(@class, "c-address-street")]/text()'
        )[0].strip()
        city = (
            body.xpath('//span[contains(@itemprop, "addressLocality")]/text()')[0]
            .replace(",", "")
            .strip()
        )
        state = body.xpath('//abbr[contains(@itemprop, "addressRegion")]/text()')[
            0
        ].strip()
        zip_postal = body.xpath('//span[contains(@itemprop, "postalCode")]/text()')[
            0
        ].strip()
        phone = body.xpath('//a[contains(@href, "tel:")]/text()')[0].strip()
        latitude = body.xpath('//meta[contains(@itemprop, "latitude")]/@content')[
            0
        ].strip()
        longitude = body.xpath('//meta[contains(@itemprop, "longitude")]/@content')[
            0
        ].strip()

        hours_of_operation = ""
        weekDayTable = body.xpath(
            './/div[@class="c-location-hours-details-wrapper js-location-hours"]/table'
        )[0]

        for texts in weekDayTable.xpath(".//tbody/tr/td"):
            texts = texts.xpath(".//text()")
            if len(texts) == 1:
                hours_of_operation = hours_of_operation + texts[0] + ": "
            else:
                hours_of_operation = hours_of_operation + ("").join(texts) + ", "
        hours_of_operation = hours_of_operation[:-2].strip()

        # Raw Address
        raw_address = (
            street_address + ", " + city + ", " + state + " " + zip_postal or MISSING
        )

        yield SgRecord(
            locator_domain=locator_domain,
            store_number=MISSING,
            page_url=page_url,
            location_name=location_name,
            location_type=MISSING,
            street_address=street_address,
            city=city,
            zip_postal=zip_postal,
            state=state,
            country_code="US",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
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
    log.info(f"Total row added = {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
