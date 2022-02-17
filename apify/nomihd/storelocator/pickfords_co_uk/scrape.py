# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "pickfords.com"
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
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    search_url = "https://www.pickfords.co.uk/sitemapxml/sitemap.xml"

    with SgRequests(
        dont_retry_status_codes=([404]),
        proxy_country="gb",
        retries_with_fresh_proxy_ip=20,
    ) as session:
        search_res = session.get(search_url, headers=headers)
        stores = search_res.text.split("<loc>")
        for index in range(1, len(stores)):
            locator_domain = website
            page_url = "".join(stores[index].split("</loc>")[0].strip()).strip()
            if "https://www.pickfords.co.uk/removals-and-storage-" not in page_url:
                continue

            log.info(page_url)
            page_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(page_res.text)
            location_name = page_url.split("/")[-1].strip().replace("-", " ").strip()
            full_address = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[@class="sfContentBlock"]/h3[contains(.//text(),"Contact your local")]/following-sibling::p[1]/span[@class="Body-Copy"]//text()'
                        )
                    ],
                )
            )
            if len(full_address) <= 0:
                full_address = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath(
                                '//div[@class="sfContentBlock"]/h3[contains(.//text(),"Contact your local")]/following-sibling::span[@class="Body-Copy"][1]//text()'
                            )
                        ],
                    )
                )
            if not full_address:
                continue

            street_address = "<MISSING>"
            city = "<MISSING>"
            state = "<MISSING>"
            zip = "<MISSING>"
            country_code = "GB"
            phone = full_address[-1]
            add_2 = ""
            if not "".join(phone).strip().replace(" ", "").strip().isdigit():
                add_2 = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath(
                                '//div[@class="sfContentBlock"]/h3[contains(.//text(),"Contact your local")]/following-sibling::p[2]/span[@class="Body-Copy"]//text()'
                            )
                        ],
                    )
                )
                if len(add_2) <= 0:
                    add_2 = list(
                        filter(
                            str,
                            [
                                x.strip()
                                for x in store_sel.xpath(
                                    '//div[@class="sfContentBlock"]/h3[contains(.//text(),"Contact your local")]/following-sibling::span[@class="Body-Copy"][2]//text()'
                                )
                            ],
                        )
                    )

            if len(add_2) > 0:
                full_address = full_address + add_2
                phone = full_address[-1]

            if len(full_address) > 1:
                street_address = (
                    ", ".join(full_address[:-4])
                    .strip()
                    .replace("Pickfords,", "")
                    .strip()
                )
                city = full_address[-4]
                state = full_address[-3]
                zip = full_address[-2]

            store_number = "<MISSING>"

            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"
            map_link = "".join(
                store_sel.xpath('//iframe[contains(@src,"maps/embed?")]/@src')
            )
            latitude, longitude = get_latlng(map_link)

            if phone:
                if not phone.replace(" ", "").strip().isdigit():
                    phone = "<MISSING>"

            if city == "Unit 2 Clifton Way":
                city = "<MISSING>"
                street_address = "Unit 2 Clifton Way"

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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
