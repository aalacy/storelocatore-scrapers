# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html
from bs4 import BeautifulSoup as BS

website = "tgifridays.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Referer": "https://www.tgifridays.co.uk/locations/braehead/",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
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
    elif "q=" in map_link:
        latitude = map_link.split("q=")[1].strip().split(",")[0].strip()
        longitude = (
            map_link.split("q=")[1]
            .strip()
            .split(",")[1]
            .strip()
            .split("+(")[0]
            .strip()
            .replace("+", "")
            .strip()
        )
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here

    stores_req = session.get(
        "https://www.tgifridays.co.uk/fridays-locations/", headers=headers
    )
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[@class="row align-items-top"]//a[contains(@href,"/locations/")]/@href'
    )
    for store_url in stores:
        page_url = "https://www.tgifridays.co.uk" + store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        location_name = "".join(
            store_sel.xpath('//div[@class="title-body"]//h1/text()')
        ).strip()
        location_type = "<MISSING>"
        locator_domain = website

        raw_address = store_sel.xpath("//address/text()")
        if "This restaurant is temporarily closed" in store_req.text:
            location_type = "temporarily closed"
            street_address = "<MISSING>"
            city = "<MISSING>"
            state = "<MISSING>"
            zip = "<MISSING>"
        elif "permanently closed" in store_req.text:
            continue
        else:
            street_address = raw_address[0].strip()
            city = raw_address[1].strip()
            state = "<MISSING>"
            zip = raw_address[-1].strip()

        country_code = "GB"

        phone = "".join(
            store_sel.xpath('//p[@class="h4 phone-number"]//text()')
        ).strip()
        store_number = "<MISSING>"

        hours_of_operation = ""
        try:
            hours_of_operation = (
                store_req.text.split("opening hours are:<br /><br />")[1]
                .strip()
                .split("</p>")[0]
                .strip()
                .replace("<br />", "; ")
                .strip()
            )
        except:
            try:
                hours_of_operation = (
                    store_req.text.split("opening hours are:</span><br /><br />")[1]
                    .strip()
                    .split("</p>")[0]
                    .strip()
                    .replace("<br />", "; ")
                    .strip()
                )
            except:
                try:
                    hours_of_operation = (
                        store_req.text.split("opening hours are:</span></p>")[1]
                        .strip()
                        .split("</span></p>")[0]
                        .strip()
                        .replace("<br />", "; ")
                        .strip()
                    )
                except:
                    try:
                        hours_of_operation = (
                            store_req.text.split(
                                "opening hours are:</span><br /><span></span></p>"
                            )[1]
                            .strip()
                            .split("</span></p>")[0]
                            .strip()
                            .replace("<br />", "; ")
                            .strip()
                        )
                    except:
                        try:
                            hours_of_operation = (
                                store_req.text.split(
                                    "opening hours will be:<br /><br />"
                                )[1]
                                .strip()
                                .split("</p>")[0]
                                .strip()
                                .replace("<br />", "; ")
                                .strip()
                            )
                        except:
                            try:
                                hours_of_operation = (
                                    store_req.text.split(
                                        "opening hours are: </span><br /><br /><span>"
                                    )[1]
                                    .strip()
                                    .split("</p>")[0]
                                    .strip()
                                    .replace("<br />", "; ")
                                    .strip()
                                )
                            except:
                                pass

        try:
            hours_of_operation = (
                BS(hours_of_operation, "html.parser")
                .get_text()
                .split("For our COVID-19 safety measures")[0]
                .strip()
                .replace("; ;", ";")
                .strip()
            )
        except:
            pass

        if len(hours_of_operation) <= 0:
            try:
                hours_of_operation = (
                    store_req.text.split("hours are:")[1]
                    .strip()
                    .split("<h4")[0]
                    .strip()
                )
            except:
                pass

        if len(hours_of_operation) <= 0:
            try:
                hours_of_operation = (
                    store_req.text.split(
                        "<p>Check out our dine-in opening times below:</p>"
                    )[1]
                    .strip()
                    .split("<span></span></p>")[0]
                    .strip()
                )
            except:
                pass

        try:
            hours_of_operation = (
                BS(hours_of_operation, "html.parser")
                .get_text()
                .split("For our COVID-19 safety measures")[0]
                .strip()
                .replace("; ;", ";")
                .strip()
                .replace("pmSunday:", "pm; Sunday:")
                .strip()
                .replace("\n", ";")
                .strip()
            )
        except:
            pass
        if hours_of_operation:
            if ";" == hours_of_operation[-1]:
                hours_of_operation = "".join(hours_of_operation[:-1]).strip()

        map_link = "".join(
            store_sel.xpath('//a[contains(text(),"View map")]/@href')
        ).strip()

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
            hours_of_operation=hours_of_operation.split(";Learn more")[0].strip(),
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
