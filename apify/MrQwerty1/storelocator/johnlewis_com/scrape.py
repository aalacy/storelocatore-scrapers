import json
from sglogging import sglog
from concurrent import futures
from lxml import html
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address, International_Parser
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "johnlewis.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "www.johnlewis.com",
    "cache-control": "max-age=0",
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
    r = session.get("https://www.johnlewis.com/our-shops", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='store-locator-list__store-link']")


def get_data(url):
    locator_domain = "https://www.johnlewis.com/"
    page_url = f"https://www.johnlewis.com{url}"
    log.info(page_url)
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = " ".join(
        "".join(tree.xpath("//h1[@class='shop-title']//text()")).split()
    )
    line = "".join(tree.xpath("//p[@class='shop-details-address']/text()")).strip()
    postal = " ".join(line.split()[-2:])
    if postal.find("London") != -1:
        postal = postal.split()[-1].strip()
    line = line.replace(postal, "").strip()
    adr = parse_address(International_Parser(), line, postcode=postal)
    street_address = (
        f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
            "None", ""
        ).strip()
        or "<MISSING>"
    )

    city = adr.city or "<MISSING>"
    if city == "<MISSING>":
        city = location_name.split(",")[-1].strip()

    state = adr.state or "<MISSING>"
    postal = adr.postcode or "<MISSING>"
    if street_address == "<MISSING>" and city == "London":
        street_address = line.split("London")[0].strip()

    country_code = "GB"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath("//span[@class='shop-details-telephone-number']/text()")
        ).strip()
        or "<MISSING>"
    )
    text = "".join(tree.xpath("//script[@id='jsonPageData']/text()")) or "{}"
    js = json.loads(text)
    latitude = js.get("latitude") or "<MISSING>"
    longitude = js.get("longitude") or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    days = tree.xpath("//dt[@class='opening-day']/text()")
    times = tree.xpath("//dd[@class='opening-time']/text()")

    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()}: {t.strip()}")

    hours_of_operation = ";".join(_tmp).replace("*", "") or "<MISSING>"
    if hours_of_operation.count("Temporarily Closed") == 7:
        hours_of_operation = "Temporarily Closed"

    if (
        street_address == "<MISSING>"
        and phone == "<MISSING>"
        and hours_of_operation == "<MISSING>"
    ):
        return

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
    stores_list = get_urls()

    for store in stores_list:
        if "(Permanently closed)" not in "".join(store.xpath("text()")).strip():
            url = "".join(store.xpath("@href")).strip()
            with futures.ThreadPoolExecutor(max_workers=10) as executor:
                future_to_url = {executor.submit(get_data, url)}
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
