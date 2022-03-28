# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import lxml.html
from sgpostal import sgpostal as parser

website = "https://ikea.com/se"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "ww8.ikea.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://ww8.ikea.com/ext/iplugins/v2/sv_SE/data/store-selector-lsp-list/data.json"
    search_res = session.get(search_url, headers=headers)

    stores = json.loads(search_res.text)

    for store in stores:

        page_url = store["url"]
        locator_domain = website

        location_name = store["name"]
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        temp_address = store_sel.xpath(
            '//div[.//*[contains(text(),"Adress")]]/p/text()'
        )
        add_list = []
        for temp in temp_address:
            if len("".join(temp).strip()) > 0:
                add_list.append("".join(temp).strip())

        raw_address = ", ".join(add_list).strip()

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        if not city:
            city = raw_address.rsplit(" ", 1)[-1].strip()
        state = formatted_addr.state
        zip = formatted_addr.postcode

        country_code = "SE"

        phone = "<MISSING>"
        store_number = "<MISSING>"

        location_type = "<MISSING>"
        days = store_sel.xpath('//div[./*[contains(text(),"Varuhus")]]/dl[1]/dt/text()')
        time = store_sel.xpath('//div[./*[contains(text(),"Varuhus")]]/dl[1]/dd/text()')
        hours_list = []
        for index in range(0, len(days)):
            hours_list.append(days[index] + ":" + time[index])

        if len(hours_list) <= 0:
            hours = store_sel.xpath(
                '//div[./*[contains(text(),"varuhuset")]]/p[1]//text()'
            )
            if len(hours) <= 0:
                hours = store_sel.xpath('//div[./h2[contains(text(),"ppettider")]]')
                if len(hours) <= 0:
                    hours = store_sel.xpath('//div[./h3[contains(text(),"ppettider")]]')

                if len(hours) > 0:
                    hours = hours[0].xpath("p[1]//text()")

            for hour in hours:
                if len("".join(hour).strip()) > 0:
                    hours_list.append("".join(hour).strip())

        hours_of_operation = "; ".join(hours_list).strip().split("; Handla")[0].strip()

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
