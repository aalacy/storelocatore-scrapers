# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "dank.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "dank.ca",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "referer": "https://dank.ca/",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
}


def get_latlng(map_link):
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here

    search_url = "https://dank.ca/locations/"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)
        stores = search_sel.xpath('//a[contains(text(),"View More Details")]/@href')

        for store_url in stores:

            page_url = "https://dank.ca" + store_url
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            locator_domain = website

            location_name = store_sel.xpath(
                '//h1[@class="elementor-heading-title elementor-size-default"]/text()'
            )
            if len(location_name) > 0:
                location_name = location_name[0].strip()

            raw_address = list(
                filter(
                    str,
                    store_sel.xpath(
                        '//li[@class="elementor-icon-list-item"][.//i[@class="fas fa-map-marker-alt"] and ./a[contains(@href,"/maps/")]]//span[@class="elementor-icon-list-text"]/text()'
                    ),
                )
            )

            street_address = "".join(raw_address[0]).strip()
            city = raw_address[1].strip().split(",")[0].strip()
            state = raw_address[1].strip().split(",")[-1].strip()
            zip = raw_address[-1].strip()

            country_code = "CA"

            store_number = "<MISSING>"
            phone = "".join(
                store_sel.xpath(
                    '//div[.//h2[contains(text(),"LOCATION INFORMATION")]]/section//li[@class="elementor-icon-list-item"][.//i[@class="fas fa-phone-alt"]]//span[@class="elementor-icon-list-text"]/text()'
                )
            ).strip()

            location_type = "<MISSING>"

            hours_of_operation = (
                "; ".join(
                    store_sel.xpath(
                        '//div[@class="elementor-widget-container"]/p[contains(.//text(),"Monday")]//text()'
                    )
                )
                .strip()
                .replace("day ;", "day:")
                .strip()
            )

            map_link = "".join(
                store_sel.xpath('//iframe[contains(@src,"/maps/embed")]/@src')
            ).strip()

            latitude, longitude = get_latlng(map_link)

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
