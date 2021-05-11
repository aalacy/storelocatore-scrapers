# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "tedscafe.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
}


def split_fulladdress(address_info):
    street_address = " ".join(address_info[0:-1]).strip()

    city = address_info[-1].split(",")[0].strip()

    state = "".join(address_info[-1].split(",")[1:]).strip().split(" ")[0].strip(" ,")
    zip = "".join(address_info[-1].split(",")[1:]).strip().split(" ")[1].strip(" ,")

    country_code = "US"

    return street_address, city, state, zip, country_code


def get_latlng(lat_lng_href):
    if "z/data" in lat_lng_href:
        lat_lng = lat_lng_href.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in lat_lng_href:
        lat_lng = lat_lng_href.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here

    search_url = "https://tedscafe.com/locations/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    cities = search_sel.xpath(
        '//section[ ./div[contains(@class,"background-overlay")] and .//section]'
    )

    for city in cities:

        hours_info = city.xpath('.//section//*[ ./*[contains(@class,"business-day")]]')
        hour_list = []
        for hour in hours_info:
            info = hour.xpath(".//text()")
            info = list(filter(str, [x.strip() for x in info]))
            hour_list.append(f"{info[0]}: {info[1]}")

        columns = city.xpath('.//section[2]//div[contains(@class,"populated")]')

        for col in columns:
            store_list = col.xpath(".//h3")

            detail_list = col.xpath('.//div[contains(@data-widget_type,"text-editor")]')

            for idx, store in enumerate(store_list, 0):

                page_url = search_url
                locator_domain = website

                location_name = "".join(store.xpath(".//text()")).strip()

                address_info = list(
                    filter(
                        str,
                        detail_list[idx].xpath(".//h4//text()"),
                    )
                )

                address_info = list(filter(str, ([x.strip() for x in address_info])))
                street_address, city, state, zip, country_code = split_fulladdress(
                    address_info
                )

                store_number = "<MISSING>"

                phone = "".join(
                    detail_list[idx].xpath(".//a[@href and @data-location]//text()")
                ).strip()

                location_type = "<MISSING>"

                hours_of_operation = "; ".join(hour_list)

                lat_lng_href = "".join(
                    detail_list[idx].xpath('.//a[contains(@href,"maps")]/@href')
                )

                latitude, longitude = get_latlng(lat_lng_href)

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
