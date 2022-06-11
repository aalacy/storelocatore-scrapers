# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "thecheesecakefactory.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://locations.thecheesecakefactory.com/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        regions = search_sel.xpath('//li[@class="listing-card"]/a')

        for region in regions:

            region_url = "".join(region.xpath(".//@href")).strip()
            region_res = session.get(region_url, headers=headers)
            region_sel = lxml.html.fromstring(region_res.text)

            locator_domain = website
            cities = region_sel.xpath('//li[@class="listing-card"]/a')

            for city in cities:
                city_url = "".join(city.xpath(".//@href")).strip()
                try:
                    city_res = SgRequests.raise_on_err(
                        session.get(city_url, headers=headers)
                    )
                except SgRequestError as e:
                    if e.status_code == 404:
                        continue

                city_sel = lxml.html.fromstring(city_res.text)

                stores = city_sel.xpath('//li[@class="listing-card"]')
                for store in stores:
                    page_url = "".join(
                        store.xpath(".//a[contains(text(),'More Info')]/@href")
                    ).strip()
                    log.info(page_url)

                    store_res = session.get(page_url, headers=headers)
                    store_sel = lxml.html.fromstring(store_res.text)

                    location_name = "".join(
                        store.xpath(".//div[@class='locationInfo']/h2/text()")
                    ).strip()
                    if len(location_name) <= 0:
                        location_name = "The Cheesecake Factory"

                    street_address = "".join(
                        store.xpath('.//*[@itemprop="streetAddress"]//text()')
                    ).strip()

                    city = "".join(
                        store.xpath('.//*[@itemprop="addressLocality"]/text()')
                    ).strip()
                    state = "".join(
                        store.xpath('.//*[@itemprop="addressRegion"]//text()')
                    ).strip()
                    zip = "".join(
                        store.xpath('.//*[@itemprop="postalCode"]//text()')
                    ).strip()
                    country_code = "".join(
                        store_sel.xpath(
                            '//meta[@property="restaurant:contact_info:country_name"]/@content'
                        )
                    ).strip()

                    store_number = "<MISSING>"

                    phone = "".join(
                        store_sel.xpath('//div[@class="phone"]//text()')
                    ).strip()

                    location_type = "<MISSING>"

                    hours = store_sel.xpath('//div[@class="regular-hours"]//ul/li')
                    hours_list = []
                    for hour in hours:
                        day = "".join(hour.xpath("span[1]/text()")).strip()
                        time = "".join(hour.xpath("span[2]/text()")).strip()
                        hours_list.append(day + time)

                    hours_of_operation = "; ".join(hours_list).strip()

                    latitude, longitude = (
                        store_res.text.split('"latitude":')[1].split(",")[0].strip(),
                        store_res.text.split('"longitude":')[1].split("}")[0].strip(),
                    )
                    raw_address = "<MISSING>"

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
