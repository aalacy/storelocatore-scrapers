# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape import sgpostal as parser

website = "gongchausa.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.gongchausa.com/location"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="all_locations"]//tr[position()>1]')

    for store in stores:
        if "Coming Soon" in "".join(store.xpath("td[1]//text()")).strip():
            continue

        location_type = "<MISSING>"
        store_number = "<MISSING>"
        locator_domain = website
        phone = "".join(store.xpath("td[3]/div/text()")).strip()
        page_url = "".join(
            store.xpath(
                'td[4]/div[@class="table_address"]/a[contains(text(),"Directions")]/@href'
            )
        ).strip()
        location_name = "".join(store.xpath("td[1]/div/text()")).strip()
        address = "".join(store.xpath("td[2]/div/text()")).strip()

        if len(page_url) <= 0:
            continue

        street_address = ""
        city = ""
        state = ""
        zip = ""
        country_code = ""

        if "#" in page_url:
            page_url = "<MISSING>"
            formatted_addr = parser.parse_address_usa(address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode
            country_code = formatted_addr.country

            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = "<MISSING>"
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

        else:
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            json_list = store_sel.xpath('//script[@type="application/ld+json"]/text()')

            is_json_available = False
            for js in json_list:
                if "streetAddress" in js:
                    is_json_available = True
                    json_data = json.loads(
                        js.split('"Bubble tea"}')[0].strip() + '"Bubble tea"}'
                    )

                    location_name = json_data["name"]

                    street_address = json_data["address"]["streetAddress"]
                    city = json_data["address"]["addressLocality"]
                    state = json_data["address"]["addressRegion"]
                    zip = json_data["address"]["postalCode"]
                    country_code = json_data["address"]["addressCountry"]
                    latitude = json_data["geo"]["latitude"]
                    longitude = json_data["geo"]["longitude"]

            if is_json_available is False:
                formatted_addr = parser.parse_address_usa(address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                state = formatted_addr.state
                zip = formatted_addr.postcode
                country_code = formatted_addr.country
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                map_link = "".join(
                    store_sel.xpath('//iframe[contains(@src,"maps/embed?")]/@src')
                ).strip()
                latitude = ""
                longitude = ""
                if len(map_link) > 0:
                    latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
                    longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

            temp_list = []
            raw_text = store_sel.xpath('//div[@class="col-sm-6"][1]/p//text()')
            for raw in raw_text:
                if len("".join(raw).strip()) > 0:
                    temp_list.append("".join(raw).strip())

            hours_list = []
            for index in range(0, len(temp_list)):
                if (
                    "Mon" == "".join(temp_list[index]).strip()
                    or "Tue" == "".join(temp_list[index]).strip()
                    or "Wed" == "".join(temp_list[index]).strip()
                    or "Thu" == "".join(temp_list[index]).strip()
                    or "Fri" == "".join(temp_list[index]).strip()
                    or "Sat" == "".join(temp_list[index]).strip()
                    or "Sun" == "".join(temp_list[index]).strip()
                ):
                    day = "".join(temp_list[index]).strip()
                    time = "".join(temp_list[index + 1]).strip()
                    hours_list.append(day + ":" + time)

                elif (
                    "Mon" in "".join(temp_list[index]).strip()
                    or "Tue" in "".join(temp_list[index]).strip()
                    or "Wed" in "".join(temp_list[index]).strip()
                    or "Thu" in "".join(temp_list[index]).strip()
                    or "Fri" in "".join(temp_list[index]).strip()
                    or "Sat" in "".join(temp_list[index]).strip()
                    or "Sun" in "".join(temp_list[index]).strip()
                ):
                    hours_list.append("".join(temp_list[index]).strip())

            hours_of_operation = (
                (
                    "; ".join(hours_list)
                    .strip()
                    .replace("19050 Gulf Fwy, Friendswood, TX 77546; ", "")
                    .strip()
                    .replace("343 Bloomfield Ave Suite Montclair, NJ 07042; ", "")
                    .strip()
                )
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
            )

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

        # break


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
