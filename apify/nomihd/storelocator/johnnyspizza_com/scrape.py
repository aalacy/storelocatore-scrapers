# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "johnnyspizza.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://johnnyspizza.com/"
    states_req = session.get(search_url, headers=headers)
    states_sel = lxml.html.fromstring(states_req.text)
    states = states_sel.xpath('//ul[@id="menu-states"]/li/a/@href')
    for state_url in states:
        stores_req = session.get(state_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//a[@class="result-title"]/@href')

        for store_url in stores:
            page_url = store_url
            locator_domain = website
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            badge = "".join(store_sel.xpath('//img[@class="badge"]/@src')).strip()
            if "coming-soon.png" in badge:
                continue

            location_name = "".join(
                store_sel.xpath('//meta[@name="geo.placename"]/@content')
            ).strip()
            if location_name == "":
                location_name = "<MISSING>"

            street_address = "".join(
                store_sel.xpath(
                    '//meta[@property="business:contact_data:street_address"]/@content'
                )
            ).strip()
            city = "".join(
                store_sel.xpath(
                    '//meta[@property="business:contact_data:locality"]/@content'
                )
            ).strip()
            state = "".join(
                store_sel.xpath(
                    '//meta[@property="business:contact_data:region"]/@content'
                )
            ).strip()
            zip = "".join(
                store_sel.xpath(
                    '//meta[@property="business:contact_data:postal_code"]/@content'
                )
            ).strip()

            country_code = "".join(
                store_sel.xpath(
                    '//meta[@property="business:contact_data:country"]/@content'
                )
            ).strip()

            store_number = "<MISSING>"
            phone = "".join(
                store_sel.xpath(
                    '//meta[@property="business:contact_data:phone_number"]/@content'
                )
            ).strip()

            location_type = "<MISSING>"
            hours = store_sel.xpath('//meta[@property="business:hours:day"]')
            hours_of_operation = ""
            hours_list = []
            for index in range(0, len(hours)):
                day = "".join(hours[index].xpath("@content")).strip()
                start = "".join(
                    store_sel.xpath(
                        '//meta[@property="business:hours:start"][{}]/@content'.format(
                            str(index + 1)
                        )
                    )
                ).strip()
                end = "".join(
                    store_sel.xpath(
                        '//meta[@property="business:hours:end"][{}]/@content'.format(
                            str(index + 1)
                        )
                    )
                ).strip()
                hours_list.append(day + ":" + start + "-" + end)

            hours_of_operation = ";".join(hours_list).strip()

            latitude = "".join(
                store_sel.xpath('//meta[@property="place:location:latitude"]/@content')
            ).strip()
            longitude = "".join(
                store_sel.xpath('//meta[@property="place:location:longitude"]/@content')
            ).strip()

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
