# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "becu.org"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.becu.org",
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
    elif "staticmap?" in map_link:
        latitude = map_link.split("C")[-1].split(",")[0].strip()
        longitude = map_link.split("C")[-1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    base = "https://www.becu.org"
    search_url = "https://www.becu.org/locations/all-locations"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = list(
        search_sel.xpath(
            '//div[contains(@class,"row") and .//*[contains(@name,"all-locations")]]//div[contains(@class,"row")]//p[./a[not(contains(@href,"#"))] or not(./a)]'
        )
    )

    for store in store_list:

        url = store.xpath("./a/@href")
        if url:
            page_url = base + url[0]
            log.info(page_url)
            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)
        else:
            page_url = "<MISSING>"

        locator_domain = website
        data = list(filter(str, [x.strip() for x in store.xpath(".//text()")]))

        if (data[1] == "nd" or data[1] == "th" or data[1] == "rd") and data[2][
            0
        ] == "&":
            location_name = " ".join(data[:3])
            location_name = (
                location_name.replace(" nd ", "nd ")
                .replace(" th ", "th ")
                .replace(" rd ", "rd ")
                .strip()
            )
            full_address = data[3:]
        elif data[1] == "nd" or data[1] == "th" or data[1] == "rd":
            location_name = " ".join(data[:2])
            location_name = (
                location_name.replace(" nd ", "nd ")
                .replace(" th ", "th ")
                .replace(" rd ", "rd ")
                .strip()
            )
            full_address = data[2:]
        else:

            location_name = data[0].strip()
            full_address = data[1:]

        street_address, city, state, zip, country_code = split_fulladdress(full_address)

        street_address = (
            street_address.replace(" nd ", "nd ")
            .replace(" th ", "th ")
            .replace(" rd ", "rd ")
            .strip()
        )

        store_number = "<MISSING>"

        if url:
            phone = (
                " ".join(store_sel.xpath('//a[contains(@href,"tel") or @hred]//text()'))
                .split(" ")[0]
                .strip()
            )
            if not phone:
                phone = (
                    " ".join(
                        store_sel.xpath(
                            '//*[contains(text(),"Contact Us")]/../following-sibling::p[contains(text(),"-") or contains(text(),".")]/text()'
                        )
                    )
                    .split(" ")[0]
                    .strip()
                )
            if not phone:
                phone = (
                    " ".join(
                        store_sel.xpath(
                            '//*[contains(text(),"Contact Us")]/following-sibling::p[contains(text(),"-") or contains(text(),".")]/text()'
                        )
                    )
                    .split(" ")[0]
                    .strip()
                )
        else:
            phone = "<MISSING>"

        location_type = "<MISSING>"

        if url:
            hours_of_operation = "".join(
                list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath(
                                '//div[@class="location-hours"]//text()'
                            )
                        ],
                    )
                )
            )
            hours_of_operation = (
                hours_of_operation.replace("[By Appointment Only]", "")
                .strip()
                .replace("M-F,", "M-F")
                .strip()
            )
        else:
            hours_of_operation = "<MISSING>"

        if page_url == "https://www.becu.org/locations/Spokane":
            name = location_name.split(" ")[1]
            hours = " ".join(
                store_sel.xpath(f'//strong[contains(text(),"{name}")]/text()')
            ).strip()
            hours_of_operation = hours.split("NFC:")[1].strip()

        if url:

            map_link = "".join(store_sel.xpath('//div[@class="static-map"]/img/@src'))
            if not map_link:
                map_link = "".join(
                    store_sel.xpath(
                        '//div[@itemprop="address"]//a[contains(@href,"maps")]/@href'
                    )
                )
        else:
            map_link = "<>"

        try:
            hours_of_operation = hours_of_operation.split("; Drive-thru")[0].strip()
        except:
            pass

        try:
            hours_of_operation = hours_of_operation.split(", Drive-thru")[0].strip()
        except:
            pass

        latitude, longitude = get_latlng(map_link)

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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
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
