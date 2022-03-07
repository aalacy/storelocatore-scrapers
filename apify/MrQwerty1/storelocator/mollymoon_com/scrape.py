from sglogging import sglog
from concurrent import futures
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name="mollymoon.com")

headers = {
    "authority": "www.mollymoon.com",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def get_urls():
    r = session.get("https://www.mollymoon.com/locations", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='definition-list footer__locations']//a/@href")


def get_coords_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_data(url):
    locator_domain = "https://www.mollymoon.com/"
    page_url = f"https://www.mollymoon.com{url}"
    log.info(page_url)
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//a[@class='active section-navigation__item']/text()")
    ).strip()
    line = tree.xpath("//div[@class='location-contact']/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1])
    line = line[-1].split()
    postal = line.pop()
    state = line.pop()
    city = " ".join(line)
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//div[@class='location-contact']/span/text()")).strip()
        or "<MISSING>"
    )
    text = "".join(tree.xpath("//script[contains(text(), 'var mmLink')]/text()"))
    latitude, longitude = get_coords_from_google_url(text)
    location_type = "<MISSING>"
    hours_of_operation = (
        "".join(tree.xpath("//div[@class='location-contact']/h2/text()"))
        .replace("OPEN", "")
        .strip()
        or "<MISSING>"
    )

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
