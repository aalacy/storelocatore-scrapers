# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "pizzahutdelivery.ie"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "pizzahutdelivery.ie",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    base = "https://pizzahutdelivery.ie/"
    search_url = "https://pizzahutdelivery.ie/locations.php"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath("//h5[./a]")

    for store in store_list:

        page_url = "".join(store.xpath("./a/@href"))
        if "http" not in page_url:
            page_url = base + page_url
        locator_domain = website

        log.info(page_url)
        store_res = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_res.text)

        store_info = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath('//h2[text()="ADDRESS"]/../div//text()')
                ],
            )
        )

        full_address = store_info[:-1]
        raw_address = " ".join(full_address).strip()
        zip = raw_address.split(",")[-1].strip()
        raw_address = raw_address.replace(zip, "").strip()

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        state = "<MISSING>"
        country_code = "IE"

        location_name = " ".join(store.xpath(".//text()")).strip()
        city = location_name.split(" ")[0].strip()
        street_address = (
            street_address.replace(city, "").strip().replace("  ", " ").strip()
        )
        phone = store_info[-1].strip()

        store_number = "<MISSING>"

        location_type = "<MISSING>"

        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath(
                        '//h2[contains(text(),"HOURS")]/../div//text()'
                    )
                ],
            )
        )
        hours_of_operation = (
            "; ".join(hours).replace(":;", ":").replace("day;", "day:").strip()
        )

        lat_lng_info = (
            store_res.text.split(
                f"""stores[storesc-1][0] = '{location_name.split(" ")[0]}"""
            )[1]
            .strip()
            .split("),(")[0]
            .strip()
            .split("(")[1]
            .strip()
        )
        latitude, longitude = lat_lng_info.split(",")[0], lat_lng_info.split(",")[1]

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


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
