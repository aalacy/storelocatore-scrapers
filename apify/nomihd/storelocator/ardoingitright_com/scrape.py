# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "ardoingitright.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "ardoingitright.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://ardoingitright.com/locations/"
    states_req = session.get(search_url, headers=headers)
    states_sel = lxml.html.fromstring(states_req.text)
    states = states_sel.xpath(
        '//li[./a/span[contains(text(),"LOCATIONS")]]/ul/li/a/@href'
    )
    for state_url in states:
        log.info(state_url)
        stores_req = session.get(state_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            '//div[contains(@class,"elementor-column elementor-col-33 elementor-top-column elementor-element elementor-element-") or contains(@class,"elementor-column elementor-col-50 elementor-top-column elementor-element elementor-element-")]'
        )
        for store in stores:
            page_url = state_url

            locator_domain = website

            location_name = "".join(
                store.xpath(
                    'div[1]/div[1]/section[1]//h2[@class="elementor-heading-title elementor-size-default"]/text()'
                )
            ).strip()
            if len(location_name) <= 0 or "Rail Storage Yards" in location_name:
                continue

            raw_info = store.xpath("div[1]/div[1]/section")
            temp_raw_info = raw_info[-1]
            raw_info = temp_raw_info.xpath(
                './/div[@class="elementor-row"]/div[1]//div[@class="elementor-text-editor elementor-clearfix"]/p/text()'
            )

            raw_list = []
            for index in range(0, len(raw_info)):
                if len("".join(raw_info[index]).strip()) > 0:
                    raw_list.append("".join(raw_info[index]).strip())

            street_address = raw_list[0].strip()
            city_state_zip = raw_list[-1].strip()
            city = city_state_zip.split(",")[0].strip()
            state = city_state_zip.split(",")[-1].strip().split(" ")[0].strip()
            zip = city_state_zip.split(",")[-1].strip().split(" ")[-1].strip()

            country_code = "US"

            store_number = "<MISSING>"

            phone = "<MISSING>"

            location_type = ", ".join(
                temp_raw_info.xpath(
                    './/div[@class="elementor-row"]/div[2]//div[@class="elementor-text-editor elementor-clearfix"]/p/text()'
                )
            ).strip()
            hours_of_operation = "<MISSING>"

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
