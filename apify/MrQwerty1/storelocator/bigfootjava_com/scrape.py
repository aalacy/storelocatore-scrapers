from sglogging import sglog
from concurrent import futures
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

log = sglog.SgLogSetup().get_logger(logger_name="bigfootjava.com")


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }
    r = session.get("https://bigfootjava.com/locations/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='locationsList-item-link']/@href")


def get_data(page_url):
    locator_domain = "https://bigfootjava.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }

    session = SgRequests()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//span[@class='locationName']/text()")).strip()
    if len(location_name) <= 0:
        return
    line = tree.xpath("//span[@class='locationAddress']/text()")
    line = list(filter(None, [l.strip() for l in line]))
    iscoming = "".join(line).lower()
    if iscoming.find("coming soon") != -1:
        return

    street_address = line[0]
    if street_address.endswith(","):
        street_address = street_address[:-1]
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = " ".join(line.split()[:-1])
    postal = line.split()[-1]
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//p[@class='locationPhone']/text()"))
        .replace("Phone:", "")
        .strip()
        or "<MISSING>"
    )
    latitude = "".join(tree.xpath("//div[@data-lat]/@data-lat")) or "<MISSING>"
    longitude = "".join(tree.xpath("//div[@data-lat]/@data-long")) or "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = "<MISSING>"

    return SgRecord(
        locator_domain=locator_domain,
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=hours_of_operation,
    )


def fetch_data():
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                yield row


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
