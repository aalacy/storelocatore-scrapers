# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "postalconnections.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.postalconnections.com/store-locator/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//ul[@class="locations"]/li/a')
    lat_lng_list = (
        stores_req.text.split("var stores = [")[1]
        .strip()
        .split("];")[0]
        .strip()
        .split("['")
    )
    lat_lng_dict = {}
    for index in range(1, len(lat_lng_list)):
        temp_text = lat_lng_list[index].split("],")[0].strip()
        lat_lng_dict[temp_text.split("',")[0].strip()] = temp_text.split(",")[1:3]

    for index in range(0, len(stores)):
        if "Coming soon" in "".join(stores[index].xpath("span/text()")).strip():
            continue
        page_url = "".join(stores[index].xpath("@href")).strip()
        if "http" not in page_url:
            page_url = "https://www.postalconnections.com" + page_url

        location_name = "".join(stores[index].xpath("text()")).strip()

        location_type = "<MISSING>"
        locator_domain = website
        log.info(page_url)
        try:
            store_req = SgRequests.raise_on_err(session.get(page_url, headers=headers))
        except SgRequestError as e:
            log.error(e.status_code)
            continue

        store_sel = lxml.html.fromstring(store_req.text)

        address = store_sel.xpath('//a[@class="c-header__location"]/text()')
        add_list = []
        street_address = ""
        city = ""
        state = ""
        zip = ""
        phone = ""
        if len(address) > 0:
            for add in address:
                if len("".join(add).strip()) > 0:
                    add_list.append("".join(add).strip())

            if location_name != "Modesto #2":
                street_address = add_list[0].strip()
                city_state_zip = add_list[1].strip()
                city = city_state_zip.split(",")[0].strip()
                state = city_state_zip.split(",")[1].strip().split(" ")[0].strip()
                zip = city_state_zip.split(",")[1].strip().split(" ")[-1].strip()
            else:
                street_address = add_list[2].strip()
                city_state_zip = add_list[-1].strip()
                city = city_state_zip.split(",")[0].strip()
                state = city_state_zip.split(",")[1].strip().split(" ")[0].strip()
                zip = city_state_zip.split(",")[1].strip().split(" ")[-1].strip()
                phone = store_sel.xpath('//a[@class="c-header__phone"]/text()')[-1]

        else:
            sections = store_sel.xpath('//div[@class="store-detail"]')
            for sec in sections:
                if "Address" in "".join(sec.xpath("h3/text()")).strip():
                    address = "".join(sec.xpath("p/a/text()")).strip()
                    city_state = "".join(
                        store_sel.xpath(
                            '//section[@class="section hero store"]//div[@class="l-col"]/h2/text()'
                        )
                    ).strip()
                    city = city_state.split(",")[0].strip()
                    if "," in address:
                        street_address = address.split(",")[0].strip()
                    elif "\n" in address:
                        street_address = address.split("\n")[0].strip()

                    street_address = street_address.replace(city, "").strip()
                    state = city_state.split(",")[-1].strip()
                    zip = address.split(" ")[-1].strip()

        if len(phone) <= 0:
            phone = store_sel.xpath('//a[@class="c-header__phone"]/text()')
            if len(phone) <= 0:
                phone = "".join(
                    store_sel.xpath(
                        '//section[@class="section hero store"]//a[contains(@href,"tel:")]/text()'
                    )
                ).strip()
            else:
                phone = phone[0].strip()

        country_code = "US"

        hours_of_operation = "; ".join(
            store_sel.xpath('//span[@class="c-header__hours"]/text()')
        ).strip()

        if len(hours_of_operation) <= 0:
            try:
                hours_of_operation = (
                    store_req.text.split("<h3>Hours</h3>")[1]
                    .strip()
                    .split("</p>")[0]
                    .strip()
                    .replace("<p>", "")
                    .replace("<br />", "; ")
                    .strip()
                )
                try:
                    hours_of_operation = hours_of_operation.split(
                        "<h3>Regular Hours:</h3>"
                    )[1].strip()
                except:
                    pass

                try:
                    hours_of_operation = hours_of_operation.split("</b>")[0].strip()
                except:
                    pass

                try:
                    hours_of_operation = hours_of_operation.split("<br>")[0].strip()
                except:
                    pass
                hours_of_operation = "".join(hours_of_operation.split("\n")).strip()

            except:
                pass

        else:
            if len(hours_of_operation.split("; Mon")) > 0:
                if location_name == "Modesto":
                    hours_of_operation = hours_of_operation.split("; Mon")[0].strip()
                elif location_name == "Modesto #2":
                    hours_of_operation = (
                        "Mon" + hours_of_operation.split("; Mon")[1].strip()
                    )

        store_number = "<MISSING>"

        modified_loc_name = (
            location_name.replace("(Manhattan)", "")
            .strip()
            .replace("(", "")
            .replace(")", "")
            .strip()
            .replace("Hockessin", "Hockessein")
        )
        if modified_loc_name in lat_lng_dict:
            latitude = lat_lng_dict[modified_loc_name][0]
            longitude = lat_lng_dict[modified_loc_name][1]

        if street_address == "":
            hours_of_operation = "<INACCESSIBLE>"
            location_type = "<INACCESSIBLE>"
            store_number = "<INACCESSIBLE>"
            street_address = "<INACCESSIBLE>"
            city = "<INACCESSIBLE>"
            state = "<INACCESSIBLE>"
            zip = "<INACCESSIBLE>"
            phone = "<INACCESSIBLE>"

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
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
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
