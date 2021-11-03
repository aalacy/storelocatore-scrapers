# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "gocold.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.gocold.ca",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.gocold.ca/contact.html"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    maps = stores_sel.xpath('//div[@class="block"]//iframe/@src')
    temp_names = stores_sel.xpath('//div[@class="block"]//strong/text()')
    names = []
    for name in temp_names:
        if (
            "Tel:" not in name
            and "Sales" not in name
            and "General Inquiries" not in name
            and "Careers" not in name
        ):
            names.append(name)

    addresses = stores_sel.xpath('//div[@class="block"]/text()')
    add_list = []
    for add in addresses:
        if len("".join(add).strip()) > 0 and "Tel:" not in add:
            add_list.append("".join(add).strip())

    phones = stores_sel.xpath('//div[@class="block"]/a[contains(@href,"tel:")]/text()')

    if "905.595.4309" in phones:
        phones.remove("905.595.4309")

    add_index = 0
    for index in range(0, len(names)):
        page_url = search_url

        locator_domain = website

        location_name = names[index].strip()

        street_address = add_list[add_index]
        city_state_zip = add_list[add_index + 1]
        add_index = add_index + 2
        city = city_state_zip.split(",")[0].strip()
        state = city_state_zip.split(",")[-1].strip().split(" ", 1)[0].strip()
        zip = city_state_zip.split(",")[-1].strip().split(" ", 1)[-1].strip()

        country_code = "CA"

        store_number = "<MISSING>"

        phone = phones[index]

        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        map_link = maps[index]
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

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
