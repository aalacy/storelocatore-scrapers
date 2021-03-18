# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape import sgpostal as parser

website = "countrymax.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.countrymax.com/hours-locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[@class="page-content page-content--centered"][1]//a[contains(@href,"https://www.countrymax.com/")]/@href'
    )
    for store_url in stores:
        if "https://www.countrymax.com/countrymax-history/" in store_url:
            continue
        page_url = store_url
        location_type = "<MISSING>"
        locator_domain = website
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        location_name = "".join(
            store_sel.xpath('//h1[@class="page-heading page-heading--clear"]/text()')
        ).strip()

        sections = store_sel.xpath(
            '//div[@class="page-content page-content--centered"]//table//tr/td/p'
        )
        if len(sections) <= 0:
            sections = store_sel.xpath(
                '//div[@class="page-content page-content--centered"]//p'
            )
        address = ""
        phone = ""
        temp_hours_list = []
        for index in range(0, len(sections)):
            if "Location" in "".join(sections[index].xpath(".//strong/text()")).strip():
                address = sections[index].xpath(".//text()")
                if len(address) <= 0 or (len(address) == 1):
                    address = sections[index].xpath("span/span/text()")
                    if len(address) <= 0:
                        address = sections[index + 1].xpath(".//text()")
                        if "Phone" not in sections[index + 2].xpath(".//text()"):
                            address = address + sections[index + 2].xpath(".//text()")

                        if "Phone" not in sections[index + 3].xpath(".//text()"):
                            address = address + sections[index + 3].xpath(".//text()")

            if "Address" in "".join(sections[index].xpath("text()")).strip():
                address = sections[index + 1].xpath(".//text()")

            if "Phone:" in "".join(sections[index].xpath(".//strong/text()")).strip():
                phone = (
                    "".join(sections[index].xpath(".//text()"))
                    .strip()
                    .replace("Phone:", "")
                    .strip()
                )
                if len(phone) <= 0:
                    phone = (
                        "".join(sections[index].xpath("span/text()"))
                        .strip()
                        .replace("Phone:", "")
                        .strip()
                    )
                    if len(phone) <= 0:
                        phone = (
                            "".join(sections[index + 1].xpath(".//text()"))
                            .strip()
                            .replace("Phone:", "")
                            .strip()
                        )

            if "Ph. Number:" in "".join(sections[index].xpath(".//text()")).strip():
                phone = (
                    "".join(sections[index].xpath(".//text()"))
                    .strip()
                    .replace("Ph. Number:", "")
                    .strip()
                )

            label = "".join(sections[index].xpath(".//strong/text()")).strip()
            if (
                "Monday" in label
                or "Tuesday" in label
                or "Wednesday" in label
                or "Thursday" in label
                or "Friday" in label
                or "Saturday" in label
                or "Sunday" in label
            ):
                temp_hours_list.append(
                    "".join(sections[index].xpath(".//text()")).strip()
                )

        add_list = []
        for add in address:
            temp_text = "".join(add).strip()
            if len(temp_text) > 0 and "Location" not in temp_text:
                if "Phone" in temp_text:
                    if len(phone) <= 0:
                        try:
                            phone = temp_text.split(":")[1].strip()
                        except:
                            pass
                    break
                add_list.append("".join(add).strip())

        raw_address = " ".join(add_list).strip()
        formatted_addr = parser.parse_address_usa(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode
        country_code = formatted_addr.country

        hours = store_sel.xpath(
            '//div[@class="page-content page-content--centered"]//table//tr/td/ul/li'
        )
        hours_of_operation = ""
        hours_list = []
        for hour in hours:
            if (
                len("".join(hour.xpath(".//text()")).strip()) > 0
                and "On Route" not in "".join(hour.xpath(".//text()")).strip()
            ):
                hours_list.append("".join(hour.xpath(".//text()")).strip())

        if len(hours_list) > 0:
            hours_of_operation = "; ".join(hours_list).strip()

        if hours_of_operation == "":
            hours_list = []
            for temp in temp_hours_list:
                if len("".join(temp).strip()) > 0 and "On Route" not in temp:
                    hours_list.append("".join(temp).strip())

            hours_of_operation = "; ".join(hours_list).strip()

        store_number = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        try:
            if "maps/place" in store_req.text:
                map_link = (
                    store_req.text.split("maps/place")[1].strip().split('"')[0].strip()
                )
                if "/@" in map_link:
                    latitude = map_link.split("/@")[1].strip().split(",")[0].strip()
                    longitude = map_link.split("/@")[1].strip().split(",")[1]
            else:
                map_link = "".join(
                    store_sel.xpath('//iframe[contains(@src,"maps/embed?")]/@src')
                ).strip()
                if len(map_link) > 0:
                    latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
                    longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

        except:
            pass

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
