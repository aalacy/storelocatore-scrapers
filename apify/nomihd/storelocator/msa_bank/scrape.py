# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "msa.bank"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.msa.bank/about/convenient-locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="entry"]/div[@class="row one-location"]')
    store_hours = stores_sel.xpath('//div[@class="entry"]/div[@class="row"]')

    for index in range(0, len(stores)):
        page_url = search_url

        locator_domain = website

        location_name = "".join(stores[index].xpath("div[2]/h2/text()")).strip()

        raw_info = stores[index].xpath("div[2]/p/text()")

        raw_list = []
        for index in range(0, len(raw_info)):
            if len("".join(raw_info[index]).strip()) > 0:
                raw_list.append("".join(raw_info[index]).strip())

        street_address = raw_list[0].strip().split("(")[0].strip()
        city_state_zip = raw_list[1].strip()
        city = city_state_zip.split(",")[0].strip()
        state = city_state_zip.split(",")[-1].strip().split(" ")[0].strip()
        zip = city_state_zip.split(",")[-1].strip().split(" ")[-1].strip()

        country_code = "US"

        store_number = "<MISSING>"

        phone = raw_list[2].strip().replace("Phone:", "").strip()

        location_type = "<MISSING>"
        hours = store_hours[index].xpath(
            'div[./strong[contains(text(),"Lobby Hours")]]/table//tr'
        )
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath("td[1]/text()")).strip()
            time = "".join(hour.xpath("td[2]/text()")).strip()
            hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()

        latitude = "<MISSING>"
        longitude = "<MISSING>"

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
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
