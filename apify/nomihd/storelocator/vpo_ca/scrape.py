# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape import sgpostal as parser
import json
import datetime as dt

website = "vpo.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "vpo.ca",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def split_fulladdress(address_info):
    street_address = ", ".join(address_info[0:-1]).strip(" ,.")

    city_state_zip = (
        address_info[-1].replace(",", " ").replace(".", " ").replace("  ", " ").strip()
    )

    city = " ".join(city_state_zip.split(" ")[:-2]).strip()
    state = city_state_zip.split(" ")[-2].strip()
    zip = city_state_zip.split(" ")[-1].strip()
    country_code = "US"
    return street_address, city, state, zip, country_code


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
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def add_hours(time_string, hr):
    the_time = dt.datetime.strptime(time_string, "%I:%M %p")
    new_time = the_time + dt.timedelta(hours=hr)
    return new_time.strftime("%I:%M %p")


def fetch_data():
    # Your scraper here
    base = "https://vpo.ca/"
    search_url = "https://vpo.ca/topic/storelocator"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = list(
        search_sel.xpath('//div[./div[@class="storeEmail"]/a[contains(@href,"Store")]]')
    )

    for store in store_list:

        page_url = base + "".join(store.xpath('.//a[contains(@href,"Store")]/@href'))
        locator_domain = website

        log.info(page_url)

        store_res = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_res.text)

        location_name = "".join(store_sel.xpath('//div[@class="page-title"]/h1/text()'))

        full_address = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath(
                        '//div[@class="details"]/ul/li[1]/span[2]/text()'
                    )
                ],
            )
        )

        raw_address = " ".join(full_address)

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode

        country_code = "CA"

        store_number = "".join(store_sel.xpath('//input[@id="store-id"]/@value'))

        phone = (
            " ".join(
                list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store.xpath(
                                './/div[contains(@class,"storePhone")]//text()'
                            )
                        ],
                    )
                )
            )
            .upper()
            .replace("PHONE", "")
            .strip(" :")
            .strip()
        )

        location_type = "<MISSING>"

        data = {"storeId": store_number}

        data_res = session.post(
            "https://vpo.ca/MapStore/GetTimeZoneStoreData", headers=headers, data=data
        )
        json_res = json.loads(data_res.text)

        store_info = json_res["StoreInfo"]

        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        hour_list = []
        for day in days:
            opens = store_info[f"Hours{day}Open"]
            closes = store_info[f"Hours{day}Close"]
            try:
                opens = (
                    str(float(opens.split(" ")[0].strip().replace(":", "."))).replace(
                        ".", ":"
                    )
                    + "0 "
                    + opens.split(" ")[1].strip()
                )
                opens = add_hours(opens, 6)

            except:
                pass

            try:
                closes = (
                    str(float(closes.split(" ")[0].strip().replace(":", "."))).replace(
                        ".", ":"
                    )
                    + "0 "
                    + closes.split(" ")[1].strip()
                )
                closes = add_hours(closes, 6)
            except:
                pass

            hour_list.append(f"{day}: {opens} - {closes}")

        hours_of_operation = "; ".join(hour_list)

        map_link = "".join(store_sel.xpath('//iframe[contains(@src,"maps")]/@src'))

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
