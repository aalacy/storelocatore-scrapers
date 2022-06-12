# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "alexbrown.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.alexbrown.com/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[contains(@class,"col-sm-3 location-item")]/a/@href'
    )
    for store_url in stores:
        page_url = store_url.strip() + "resource.asp?page=simple_contact.htm"
        location_type = "<MISSING>"
        locator_domain = website
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        location_name = "".join(
            store_sel.xpath('//p[@class="logo_name"]/text()')
        ).strip()

        temp_address = store_sel.xpath("//address/text()")
        address = []
        for temp in temp_address:
            if len("".join(temp).strip()) > 0:
                address.append("".join(temp).strip())

        street_address = ", ".join(address[:-1]).strip()
        city_state_zip = (
            address[-1]
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", " ")
            .strip()
        )

        city = (
            city_state_zip.split(",")[0]
            .strip()
            .replace("World Financial Center", "")
            .strip()
        )
        state = (
            city_state_zip.split(",")[1]
            .strip()
            .split(" ")[0]
            .strip()
            .replace(".", "")
            .strip()
        )
        zipp = ""
        if len(city_state_zip.split(",")) == 3:
            zipp = city_state_zip.split(",")[-1].strip()
        else:
            zipp = city_state_zip.split(",")[1].strip().split(" ")[-1].strip()
        country_code = "US"
        phone = (
            "".join(store_sel.xpath('//address/strong[contains(text(),"T:")]/text()'))
            .strip()
            .replace("T:", "")
            .strip()
        )
        hours_of_operation = "<MISSING>"
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
            zip_postal=zipp,
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
