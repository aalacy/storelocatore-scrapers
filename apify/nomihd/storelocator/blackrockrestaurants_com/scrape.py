# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "blackrockrestaurants.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    """ US LOCATIONS """

    search_url = "https://www.blackrockrestaurants.com/"
    states_req = session.get(search_url, headers=headers)
    states_sel = lxml.html.fromstring(states_req.text)
    states = states_sel.xpath(
        '//span[contains(text(),"See Menus, Hours & More for our locations in")]/span//a/@href'
    )
    for state_url in states:
        log.info(state_url)
        stores_req = session.get(state_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//h1[@class="font_0"]/a/@href')

        for store_url in stores:
            if "https://www.blackrockrestaurants.com" == store_url:
                continue

            page_url = store_url
            log.info(page_url)
            store_req = session.get(page_url)
            store_sel = lxml.html.fromstring(store_req.text)
            locator_domain = website
            location_name = "".join(
                store_sel.xpath('//h2[@class="font_2"]/span/text()')
            ).strip()

            address = ""
            hours_list = []
            raw_info = store_sel.xpath('//p[@class="font_8"]//text()')
            for index in range(0, len(raw_info)):
                if "(find us)" in raw_info[index]:
                    address = raw_info[:index]
                    hours_list = raw_info[index + 4 : -2]

            street_address = ", ".join(address[:-1])
            city = address[-1].strip().split(",")[0].strip()
            state = address[-1].strip().split(",")[1].strip().split(" ")[0].strip()
            zip = address[-1].strip().split(",")[1].strip().split(" ")[-1].strip()
            country_code = "US"

            phone = "".join(
                store_sel.xpath(
                    '//p[@class="font_8"]//a[contains(@href,"tel:")]//text()'
                )
            )

            store_number = "<MISSING>"
            location_type = "<MISSING>"

            hours_of_operation = (
                " ".join(hours_list)
                .strip()
                .replace("*Hours are subject to change", "")
                .strip()
            )
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            map_link = "".join(
                store_sel.xpath('//a[contains(@href,"google.com/maps")]/@href')
            ).strip()
            if len(map_link) > 0:
                if "/@" in map_link:
                    latitude = map_link.split("/@")[1].strip().split(",")[0].strip()
                    longitude = map_link.split("/@")[1].strip().split(",")[1]
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
