# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "ram.bo"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
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
    search_urls_list = [
        "https://www.ramlatam.com/bo/concesionarios/",
        "https://www.ramlatam.com/cl/concesionarios/",
        "https://www.ramlatam.com/co/concesionarios/",
        "https://www.ramlatam.com/ec/concesionarios/",
        "https://www.ramlatam.com/pe/concesionarios/",
        "https://www.ramlatam.com/ve/concesionarios/",
    ]

    with SgRequests() as session:
        for search_url in search_urls_list:
            log.info(search_url)
            search_res = session.get(search_url, headers=headers)

            search_sel = lxml.html.fromstring(search_res.text)
            stores = search_sel.xpath(
                '//div[@class="dealers-list"]/div[@class="dealer-card"]'
            )

            for store in stores:

                locator_domain = website

                location_name = "".join(
                    store.xpath("h3[@class='dealer-name']/text()")
                ).strip()

                location_type = ", ".join(
                    store.xpath(
                        'div[@class="dealer-features"]/figure[contains(@class,"available")]/span/text()'
                    )
                ).strip()
                raw_address = (
                    "".join(
                        store.xpath(
                            'div[@class="dealer-details-text"][./span[@class="icon-adress"]]/text()'
                        )
                    )
                    .strip()
                    .replace("\r\n", "")
                    .strip()
                    .replace("\n", ", ")
                    .strip()
                )

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                if street_address is not None:
                    street_address = street_address.replace("Ste", "Suite")
                city = "".join(store.xpath("@data-region")).strip()

                state = "<MISSING>"
                zip = "<MISSING>"

                country_code = search_url.split("/")[-3]
                temp_phone = store.xpath(
                    'div[@class="dealer-details"]/div[@class="dealer-contact-options"]//p[@class="icon-phone"]/text()'
                )

                phone = "<MISSING>"
                if len(temp_phone) > 0:
                    phone = (
                        temp_phone[0]
                        .strip()
                        .encode("ascii", "replace")
                        .decode("utf-8")
                        .replace("?", "-")
                        .strip()
                        .split(" - ")[0]
                        .strip()
                        .split("/")[0]
                        .strip()
                    )
                if phone == "00000":
                    phone = "<MISSING>"

                page_url = search_url
                dealer_website = "".join(
                    store.xpath('.//a[@class="dealer-website"]/@href')
                ).strip()
                if len(dealer_website) > 0:
                    page_url = dealer_website

                temp_hours = store.xpath(
                    'div[@class="dealer-details"]/div[@class="dealer-contact-options"]//div[@class="grilla-horas"]'
                )
                hours_list = []

                if len(temp_hours) > 0:
                    hours = temp_hours[0].xpath("div")
                    for hour in hours:
                        day = "".join(hour.xpath("text()")).strip()
                        time = "".join(hour.xpath("p//text()")).strip()
                        if time == "-":
                            continue
                        hours_list.append(day + ":" + time)

                hours_of_operation = "; ".join(hours_list).strip()

                store_number = "<MISSING>"

                map_link = "".join(
                    store.xpath(".//a[@class='dealer-map']/@href")
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
                    raw_address=raw_address,
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                    SgRecord.Headers.COUNTRY_CODE,
                    SgRecord.Headers.LOCATION_NAME,
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
