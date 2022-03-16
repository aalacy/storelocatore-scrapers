# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
import urllib.parse
from sgscrape import sgpostal as parser

website = "academicsprek.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.academicsprek.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://www.academicsprek.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.academicsprek.com/locations/"
    search_req = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_req.text)
    json_text = urllib.parse.unquote(
        "".join(
            search_sel.xpath(
                '//div[@class="elfsight-widget-google-maps elfsight-widget"]/@data-elfsight-google-maps-options'
            )
        ).strip()
    )

    markers = json.loads(json_text)["markers"]
    coord_dict = {}
    for marker in markers:
        if len(marker["infoPhone"]) > 0:
            item_dict = {}
            item_dict["infoTitle"] = marker["infoTitle"]
            item_dict["coordinates"] = marker["coordinates"]
            item_dict["infoWorkingHours"] = marker["infoWorkingHours"]
            coord_dict[marker["infoPhone"]] = item_dict

    sections = search_sel.xpath('//ul[@class="elementor-icon-list-items"]')
    stores = []
    for index in range(0, len(sections)):
        if "LOCATIONS" == "".join(sections[index].xpath("li[1]/a/span/text()")).strip():
            stores = sections[index].xpath("li[position()>1]/a/@href")
            break

    for store_url in stores:
        page_url = store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        if "OPENING FALL" in store_req.text:
            continue
        store_sel = lxml.html.fromstring(store_req.text)
        locator_domain = website

        location_name = "<MISSING>"
        raw_address = (
            ", ".join(
                store_sel.xpath(
                    '//*[@id="content"]/div/div/div/div/section[2]/div/div/div[1]/div/div/div[3]/div/div/p[1]//text()'
                )
            )
            .strip()
            .replace(", ,", ", ")
            .strip()
        )

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode

        country_code = "CA"

        store_number = "<MISSING>"

        phone = "<MISSING>"
        try:
            phone = (
                store_req.text.split("Phone: <")[1]
                .strip()
                .split(">")[1]
                .strip()
                .split("<")[0]
                .strip()
            )
        except:
            pass

        if phone == "<MISSING>":
            try:
                phone = store_req.text.split("Phone: ")[1].strip().split("<")[0].strip()
            except:
                pass

        phone = (
            phone.split("Email")[0]
            .strip()
            .replace("(", "")
            .replace(")", "")
            .replace(" ", "-")
            .strip()
        )
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if phone in coord_dict:
            location_name = coord_dict[phone]["infoTitle"]
            hours_of_operation = coord_dict[phone]["infoWorkingHours"]
            LatLng = coord_dict[phone]["coordinates"]
            latitude = LatLng.split(",")[0].strip()
            longitude = LatLng.split(",")[1].strip()

        if hours_of_operation == "<MISSING>" or hours_of_operation == "":
            hours = store_sel.xpath(
                '//div[.//b[contains(text(),"School Hours")]]/table//tr'
            )
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath("td[1]/text()")).strip()
                time = "".join(hour.xpath("td[2]/text()")).strip()
                hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()
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
