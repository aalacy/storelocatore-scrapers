# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "benbridge.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    countries = ["US", "CA"]
    for country in countries:
        search_url = "https://www.benbridge.com/jewelry-stores"
        search_req = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_req.text)
        post_url = "".join(
            search_sel.xpath('//form[@id="dwfrm_storelocator"]/@action')
        ).strip()

        data = {
            "dwfrm_storelocator_countryCode": "",
            "dwfrm_storelocator_country": country,
            "dwfrm_storelocator_findbycountry": "Search",
        }
        stores_req = session.post(post_url, data=data, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)

        stores = stores_sel.xpath('//a[@class="storedetail"]/@href')
        for store_url in stores:
            page_url = "https://www.benbridge.com" + store_url
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            locator_domain = website
            location_name = "".join(
                store_sel.xpath(
                    '//span[@class="c-section-contact-info__subheading"]/text()'
                )
            ).strip()

            address = store_sel.xpath(
                '//p[@class="c-section-contact-info__text"]/text()'
            )
            add_list = []
            for add in address:
                if len("".join(add).strip()) > 0:
                    add_list.append("".join(add).strip())

            street_address = add_list[0].strip()
            city = add_list[1].strip().split(",")[0].strip()
            state = add_list[1].strip().split(",")[1].strip().split(" ", 1)[0].strip()
            zip = add_list[1].strip().split(",")[1].strip().split(" ", 1)[1].strip()

            country_code = country

            store_number = "".join(
                store_sel.xpath('//meta[@itemprop="branchCode"]/@content')
            ).strip()
            phone = "".join(
                store_sel.xpath('//meta[@itemprop="telephone"]/@content')
            ).strip()

            location_type = "<MISSING>"
            brands_list = store_sel.xpath(
                '//div[@class="store-brand-list"]/ul/li//text()'
            )

            if "Pandora" in brands_list:
                location_type = "PANDORA"

            hours = store_sel.xpath('//table[@class="store-hours"]/tr')
            hours_list = []
            for hour in hours:
                hours_list.append(
                    "".join(hour.xpath('td[@class="day"]/text()')).strip()
                    + ":"
                    + "".join(hour.xpath('td[@class="time"]/text()')).strip()
                )

            hours_of_operation = "; ".join(hours_list).strip()

            latitude = store_req.text.split("lat:")[1].strip().split(",")[0].strip()
            longitude = store_req.text.split("lng:")[1].strip().split("}")[0].strip()

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
