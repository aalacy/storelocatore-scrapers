import time
from lxml import html

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sglogging import sglog

session = SgRequests()

website = "easymoneynow.com"

log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def requests_with_retry(url):
    return session.get(url, headers=headers).json()


def hoursOperation(hrsNode):
    h = []
    body = html.fromstring(hrsNode, "lxml")
    nodes = body.xpath("/html/body/table/tr")
    for n in nodes:
        day = "".join(n.xpath(".//text()")[0].split(","))
        hr = "".join(n.xpath(".//text()")[1].split(","))
        h.append(f"{day}: {hr}")
    hours_of_operation = "; ".join(h)

    return hours_of_operation


def fetchData():
    l = "https://www.easymoneynow.com/wp-admin/admin-ajax.php?action=store_search&autoload=1 "
    j = requests_with_retry(l)

    for d in j:
        page_url = d["permalink"]
        location_name = d["store"]
        street_address = d["address"]
        city = d["city"]
        state = d["state"]
        zip_postal = d["zip"]
        country_code = "US"
        phone = d["phone"]
        store_number = d["id"]
        latitude = d["lat"]
        longitude = d["lng"]
        hoo = d["hours"]
        hours_of_operation = hoursOperation(hoo)

        yield SgRecord(
            locator_domain=website,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            phone=phone,
            location_type="",
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
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
    log.info(f"Total contact-us = {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
