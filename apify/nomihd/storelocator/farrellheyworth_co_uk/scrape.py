# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "farrellheyworth.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
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
    elif "&daddr=" in map_link:
        latitude = map_link.split("&daddr")[1].split(",")[0].strip()
        longitude = map_link.split("&daddr")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here

    search_url = "https://www.farrellheyworth.co.uk/about-us/branches/"

    with SgRequests(dont_retry_status_codes=([404])) as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath('//div[@class="post"]')

        for _, store in enumerate(stores):

            page_url = "".join(store.xpath(".//h2/a/@href"))
            log.info(page_url)
            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            locator_domain = website

            location_name = "".join(
                store_sel.xpath('//div[@class="contact-now"]/h2//text()')
            ).strip()

            raw_address = "<MISSING>"
            street_address = " ".join(
                store_sel.xpath('//div[@itemprop="streetAddress"]//text()')
            ).strip()

            city = "".join(
                store_sel.xpath('//div[@itemprop="addressLocality"]//text()')
            ).strip()
            state = "<MISSING>"
            zip = "".join(
                store_sel.xpath('//div[@itemprop="postalCode"]//text()')
            ).strip()

            country_code = "".join(
                store_sel.xpath('//div[@itemprop="addressRegion"]//text()')
            ).strip()

            store_number = "<MISSING>"

            phone = "".join(store_sel.xpath('//div[@class="tel"]/a/text()'))

            location_type = "<MISSING>"
            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//table[@class="OpeningHoursTable"]//text()'
                        )
                    ],
                )
            )[1:]
            hours_of_operation = "; ".join(hours).replace(":;", ":").strip()
            map_link = "".join(store_sel.xpath('//div[@class="adr"]/a/@href'))
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
