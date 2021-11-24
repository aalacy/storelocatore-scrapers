# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape import sgpostal as parser

website = "dintaifungusa.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    """ US LOCATIONS """

    search_url = "https://dintaifungusa.com/us/locations.html"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//ul[@class="locations"]/li/a[@class="cta-link"]/@href')

    for store_url in stores:
        page_url = "https://dintaifungusa.com" + store_url
        log.info(page_url)
        store_req = session.get(page_url)
        store_sel = lxml.html.fromstring(store_req.text)
        locator_domain = website
        location_name = "".join(
            store_sel.xpath('//header[@class="location-header"]/h1//text()')
        ).strip()
        try:
            location_name = location_name.split("-", 1)[0].strip()
        except:
            pass
        address = store_sel.xpath('//section[@class="layout__block"]//address/text()')
        add_list = []
        for add in address:
            if len("".join(add).strip()) > 0:
                add_list.append("".join(add).strip())

        street_address = ", ".join(add_list[:-1])
        if street_address[-1] == ",":
            street_address = "".join(street_address[:-1]).strip()

        city = add_list[-1].strip().split(",")[0].strip()
        state = add_list[-1].strip().split(",")[1].strip().split(" ")[0].strip()
        zip = add_list[-1].strip().split(",")[1].strip().split(" ")[-1].strip()
        country_code = "US"

        phone = "".join(
            store_sel.xpath('//section[@class="layout__block"]//address/a/text()')
        ).strip()

        store_number = "<MISSING>"
        location_type = "<MISSING>"

        hours = store_sel.xpath('//ul[@class="hours"]/li')
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath("time/text()")).strip()
            time = "".join(hour.xpath("time/span/text()")).strip()
            hours_list.append(day + time)

        hours_of_operation = "; ".join(hours_list).strip()
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        map_link = "".join(
            store_sel.xpath(
                '//section[@class="layout__block"]//a[contains(@href,"maps/")]/@href'
            )
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

    """ UK LOCATIONS """
    global_loc_req = session.get(
        "https://www.dintaifung.com.tw/eng/store_world.php", headers=headers
    )
    global_sel = lxml.html.fromstring(global_loc_req.text)
    countries = global_sel.xpath('//a[contains(@class,"worldname ")]')
    for country in countries:
        search_url = "https://www.dintaifung.com.tw/eng/" + "".join(
            country.xpath("@href")
        ).strip().replace("store_world", "store_list")
        log.info(search_url)
        country_code = "".join(country.xpath("text()")).strip()

        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//div[@class="info"]')

        for store in stores:
            page_url = search_url
            locator_domain = website
            location_name = "".join(store.xpath('div[@class="name"]/text()')).strip()

            address = "".join(store.xpath('.//div[@class="addr"]//text()')).strip()
            street_address = ""
            city = ""
            state = ""
            zip = ""
            raw_address = "<MISSING>"
            if country_code == "United Kingdom":
                street_address = ", ".join(address.split(",")[:-1]).strip()
                city = address.split(",")[-1].strip().split(" ", 1)[0].strip()
                state = "<MISSING>"
                zip = address.split(",")[-1].strip().split(" ", 1)[-1].strip()
            else:
                raw_address = address
                formatted_addr = parser.parse_address_intl(address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                state = formatted_addr.state
                zip = formatted_addr.postcode

            phone = "".join(store.xpath('.//div[@class="line"][2]/div/text()')).strip()

            store_number = "<MISSING>"
            location_type = "<MISSING>"

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
                raw_address=raw_address,
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
