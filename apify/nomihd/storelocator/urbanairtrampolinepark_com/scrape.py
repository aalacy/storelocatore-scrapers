# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "urbanairtrampolinepark.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.urbanair.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.urbanair.com/locations/"
    with SgRequests() as session:
        while True:
            log.info(search_url)
            stores_req = session.get(search_url, headers=headers)
            stores_sel = lxml.html.fromstring(stores_req.text)
            stores = stores_sel.xpath("//div[@data-post-id]")
            for store in stores:
                page_url = "".join(
                    store.xpath(".//h2[@class='geodir-entry-title  h5 mb-2']/a/@href")
                ).strip()
                locator_domain = website
                location_name = "".join(
                    store.xpath(".//h2[@class='geodir-entry-title  h5 mb-2']//text()")
                ).strip()
                street_address = "".join(
                    store.xpath(".//span[@itemprop='streetAddress']/text()")
                ).strip()
                city = "".join(
                    store.xpath(".//span[@itemprop='addressLocality']/text()")
                ).strip()
                state = "".join(
                    store.xpath(".//span[@itemprop='addressRegion']/text()")
                ).strip()
                zip = "".join(
                    store.xpath(".//span[@itemprop='postalCode']/text()")
                ).strip()
                phone = "".join(
                    store.xpath(".//a[contains(@href,'tel:')]/text()")
                ).strip()

                country_code = "".join(
                    store.xpath(".//span[@itemprop='addressCountry']/text()")
                ).strip()
                store_number = "".join(store.xpath("@data-post-id")).strip()

                location_type = "<MISSING>"

                map_link = "".join(
                    store.xpath('.//span[@class="bsui gd-badge-meta"]/a/@href')
                )
                latitude = map_link.split("?daddr=")[1].strip().split(",")[0].strip()
                longitude = map_link.split("?daddr=")[1].strip().split(",")[1].strip()

                hours = store.xpath(".//div[@data-day]")
                hours_list = []
                for hour in hours:
                    day = "".join(hour.xpath("div[1]/text()")).strip()
                    time = "".join(hour.xpath("div[2]//text()")).strip()
                    hours_list.append(day + ":" + time)

                hours_of_operation = "; ".join(hours_list).strip()
                if not hours_of_operation:
                    store_req = session.get(page_url, headers=headers)
                    store_sel = lxml.html.fromstring(store_req.text)
                    if "COMING SOON" in store_req.text:
                        location_type = "COMING SOON"

                    elif "TEMPORARILY CLOSED" in store_req.text:
                        location_type = "TEMPORARILY CLOSED"
                    else:
                        hours = store_sel.xpath(
                            '//div[@class="et_pb_module dsm_business_hours dsm_business_hours_0"]'
                        )
                        if len(hours) > 0:
                            hours = hours[0].xpath(
                                './/div[@class="dsm-business-hours-header"]'
                            )
                            hours_list = []
                            for hour in hours:
                                day = "".join(
                                    hour.xpath(
                                        "div[@class='dsm-business-hours-day']/text()"
                                    )
                                ).strip()
                                time = "".join(
                                    hour.xpath(
                                        "div[@class='dsm-business-hours-time']//text()"
                                    )
                                ).strip()
                                hours_list.append(day + ":" + time)

                            hours_of_operation = "; ".join(hours_list).strip()
                            if hours_of_operation.count("Closed") == 7:
                                location_type = "Closed"

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

            next_page = stores_sel.xpath('//li/a[@class="next page-link"]/@href')
            if len(next_page) > 0:
                search_url = next_page[0]
            else:
                break


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
