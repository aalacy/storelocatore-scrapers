# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "hannaford.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.hannaford.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    with SgRequests() as session:
        sitemap_resp = session.get(
            "https://www.hannaford.com/sitemap/store_1.xml",
            headers=headers,
        )

        store_links = sitemap_resp.text.split("<loc>")
        for store in store_links:
            if "https://www.hannaford.comhttps://stores" in store:
                page_url = (
                    store.split("</loc>")[0]
                    .strip()
                    .replace("https://www.hannaford.comhttps:", "https:")
                )
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                if isinstance(store_req, SgRequestError):
                    continue
                store_sel = lxml.html.fromstring(store_req.text)
                locator_domain = website

                location_name = " ".join(
                    store_sel.xpath("//h1[@id='location-name']//text()")
                ).strip()

                street_address = ", ".join(
                    store_sel.xpath(
                        '//div[@class="Core-addressWrapper"]//address[@itemprop="address"]//span[contains(@class,"Address-field Address-line")]/text()'
                    )
                ).strip()
                city = "".join(
                    store_sel.xpath(
                        '//div[@class="Core-addressWrapper"]//address[@itemprop="address"]//span[@class="Address-field Address-city"]/text()'
                    )
                ).strip()
                state = "".join(
                    store_sel.xpath(
                        '//div[@class="Core-addressWrapper"]//address[@itemprop="address"]//span[@itemprop="addressRegion"]/text()'
                    )
                ).strip()
                zip = "".join(
                    store_sel.xpath(
                        '//div[@class="Core-addressWrapper"]//address[@itemprop="address"]//span[@itemprop="postalCode"]/text()'
                    )
                ).strip()

                country_code = "US"

                store_number = page_url.split("/")[-1].strip()

                section = store_sel.xpath('//div[@class="Core-storeInfoWrapper"]')
                if len(section) > 0:
                    phone = "".join(
                        section[0].xpath('.//div[@class="Core-storeContact"]/text()')
                    ).strip()
                    if len(phone) <= 0:
                        phone = "".join(
                            section[0].xpath(
                                './/div[@class="Core-pharmContact"]/text()'
                            )
                        ).strip()

                location_type = "<MISSING>"

                hours = []
                hours_section = store_sel.xpath(
                    '//div[@class="Core-storeHoursWrapper"]'
                )
                if len(hours_section) > 0:
                    hours = hours_section[0].xpath(
                        './/table[@class="c-hours-details"]//tbody/tr'
                    )
                else:
                    hours_section = store_sel.xpath(
                        '//div[@class="Core-pharmacyHoursInfo"]'
                    )
                    if len(hours_section) > 0:
                        hours = hours_section[0].xpath(
                            './/table[@class="c-hours-details"]//tbody/tr'
                        )

                hours_list = []
                for hour in hours:
                    day = "".join(
                        hour.xpath('td[@class="c-hours-details-row-day"]/text()')
                    ).strip()
                    time = "".join(
                        hour.xpath('td[@class="c-hours-details-row-intervals"]//text()')
                    ).strip()
                    hours_list.append(day + ":" + time)

                hours_of_operation = "; ".join(hours_list).strip()

                latitude = "".join(
                    store_sel.xpath(
                        '//span[@class="Address-coordinates"]/meta[@itemprop="latitude"]/@content'
                    )
                ).strip()
                longitude = "".join(
                    store_sel.xpath(
                        '//span[@class="Address-coordinates"]/meta[@itemprop="longitude"]/@content'
                    )
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
