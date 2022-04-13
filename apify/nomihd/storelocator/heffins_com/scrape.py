# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "heffins.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
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

    search_url = "https://www.heffins.com/about-us/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    sections = stores_sel.xpath('//div[@class="col-lg-4 col-sm-4 col-xs-12"]')
    for sec in sections:
        names = sec.xpath("h5")
        for index in range(0, len(names)):
            locator_domain = website

            location_name = "".join(names[index].xpath(".//text()")).strip()
            page_url = (
                "".join(names[index].xpath(".//@href"))
                .strip()
                .replace("../..", "")
                .strip()
            )
            latitude, longitude = "<MISSING>", "<MISSING>"

            if len(page_url) > 0:
                if "http" not in page_url:
                    page_url = "https://www.heffins.com" + page_url
                    log.info(page_url)
                    store_req = session.get(page_url, headers=headers)
                    store_sel = lxml.html.fromstring(store_req.text)
                    map_link = "".join(
                        store_sel.xpath('//iframe[contains(@src,"maps/embed")]/@src')
                    ).strip()
                    latitude, longitude = get_latlng(map_link)

            if not page_url:
                page_url = search_url

            address = names[index].xpath("following-sibling::p[1]//text()")
            street_address = ""
            city = ""
            state = ""
            zip = ""
            country_code = ""

            if location_name == "London, UK":
                street_address = address[1].strip()
                city = address[-1].strip().split(",")[0].strip()
                state = "<MISSING>"
                zip = address[-1].strip().split(",")[-1].strip()
                country_code = "GB"

            else:
                street_address = address[0].strip()
                city = address[-1].strip().split(",")[0].strip()
                state = address[-1].strip().split(",")[-1].strip().split(" ")[0].strip()
                zip = address[1].strip().split(",")[-1].strip().split(" ")[-1].strip()
                country_code = "US"

            store_number = "<MISSING>"

            phone = "".join(
                names[index].xpath(
                    'following-sibling::p[./img[@alt="phone number"]][1]//text()'
                )
            ).strip()

            if "or" in phone:
                phone = phone.split("or")[0].strip()
            location_type = "<MISSING>"

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


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
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
