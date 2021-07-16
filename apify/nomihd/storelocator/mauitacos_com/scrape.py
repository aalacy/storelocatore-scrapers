# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html


website = "mauitacos.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "mauitacos.com",
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
    search_url = "https://mauitacos.com/locations"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    area_list = search_sel.xpath(
        '//div[./h2[text()]]//div[@class="wpb_wrapper" and (./h2  or ./h3)]'
    )

    for area in area_list:
        store_names = list(
            filter(
                str,
                [x.strip() for x in area.xpath("./*[self::h2 or self::h3]//text()")],
            )
        )
        for pos, store_name in enumerate(store_names, 1):  # pos is position

            page_url = search_url
            locator_domain = website
            location_name = store_name

            store_number = "<MISSING>"
            location_type = "<MISSING>"

            addresses = area.xpath(
                f'./p[(count(preceding-sibling::h2)={pos} or count(preceding-sibling::h3)={pos}) and not(contains(.//a//text(),"Menu"))]'
            )

            street_address = (
                " ".join(
                    list(
                        filter(
                            str, [x.strip() for x in addresses[0].xpath(".//text()")]
                        )
                    )
                )
                .replace("Address:", " ")
                .replace("  ", " ")
                .strip()
            )
            temp_street = street_address
            for index in range(0, len(temp_street)):
                if temp_street[index].isdigit() or temp_street[index].isalpha():
                    street_address = "".join(temp_street[index:]).strip()
                    break
            city_state_zip = " ".join(
                list(filter(str, [x.strip() for x in addresses[1].xpath(".//text()")]))
            ).strip()
            city_state_zip = (
                city_state_zip.replace(",", " ")
                .replace(".", " ")
                .replace("  ", " ")
                .strip()
            )

            city = " ".join(city_state_zip.split(" ")[:-2]).strip()
            temp_city = city
            for index in range(0, len(temp_city)):
                if temp_city[index].isdigit() or temp_city[index].isalpha():
                    city = "".join(temp_city[index:]).strip()
                    break

            state = city_state_zip.split(" ")[-2].strip()
            zip = city_state_zip.split(" ")[-1].strip()
            country_code = "US"

            phone = (
                " ".join(
                    list(
                        filter(
                            str, [x.strip() for x in addresses[2].xpath(".//text()")]
                        )
                    )
                )
                .replace("Phone:", " ")
                .replace("  ", " ")
            )
            temp_phone = phone
            for index in range(0, len(temp_phone)):
                if (
                    temp_phone[index].isdigit()
                    or temp_phone[index].isalpha()
                    or temp_phone[index] == "("
                ):
                    phone = "".join(temp_phone[index:]).strip()
                    break

            hours_of_operation = "<MISSING>"

            lat_lng_href = addresses[3].xpath(".//a/@href")[0]

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
