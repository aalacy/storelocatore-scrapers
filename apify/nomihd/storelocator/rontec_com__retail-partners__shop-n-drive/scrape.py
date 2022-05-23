# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ast
import lxml.html
from sgpostal import sgpostal as parser

website = "rontec.com/retail-partners/shop-n-drive"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Referer": "http://rontec-servicestations.co.uk/",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "http://rontec-servicestations.co.uk/cluster2.cfm"

    with SgRequests(verify_ssl=False) as session:
        search_res = session.get(search_url, headers=headers)

        markers = ast.literal_eval(
            search_res.text.split("var markers = ")[1].strip().split("];")[0].strip()
            + "]"
        )

        temp_html = (
            (
                search_res.text.split("var infoWindowContent = [")[1]
                .strip()
                .split("];")[0]
                .strip()
                + "]"
            )
            .replace("'", "")
            .replace("+", "")
            .strip()
            .replace("[", "['")
            .replace("]", "']")
            .replace("],']", "],]")
        )
        temp_html = (
            "[" + temp_html.replace("\r\n", "").strip().replace("\n", "").strip()
        )
        info_list = ast.literal_eval(temp_html)
        for index in range(0, len(markers)):
            locator_domain = website
            info_sel = lxml.html.fromstring(info_list[index][0])
            page_url = (
                "http://rontec-servicestations.co.uk/"
                + "".join(info_sel.xpath("//a/@href")).strip()
            )
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            location_name = markers[index][0].split(",")[0].strip()
            location_type = (
                markers[index][3]
                .split(".png")[0]
                .strip()
                .split("/")[-1]
                .strip()
                .replace("_marker", "")
                .strip()
            )

            raw_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[@class="panel-body"]//div[@class="col-md-6"]//text()'
                        )
                    ],
                )
            )
            hours_of_operation = "<MISSING>"
            phone = "<MISSING>"
            raw_address = "<MISSING>"
            for index, raw in enumerate(raw_info, 0):
                if "Opening Hours:" in raw:
                    hours_of_operation = raw_info[index + 1]
                if "Tel:" in raw:
                    phone = raw_info[index + 1]
                if "Address:" in raw:
                    raw_address = (
                        ", ".join(raw_info[index + 1 :])
                        .strip()
                        .split(", Tel:")[0]
                        .strip()
                    )
                    temp_raw = raw_address.split(",", 1)
                    if temp_raw[0].isdigit():
                        raw_address = temp_raw[0] + temp_raw[1]

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address:
                street_address = (
                    street_address.replace("Nn10 6Bq", "")
                    .replace("Sr5 3Nx", "")
                    .replace("Pe8 6Lb", "")
                    .replace("Ll14 6Yy", "")
                    .replace("Ig11 0At", "")
                    .strip()
                )
            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode
            if not zip:
                zip = raw_address.split(",")[-1].strip()

            if zip:
                zip = zip.replace("CLWYD LL14 1PA", "LL14 1PA").strip()
            country_code = "GB"

            store_number = page_url.split("?id=")[1].strip()
            latitude, longitude = markers[index][1], markers[index][2]
            shop_n_drive_logo = "".join(
                store_sel.xpath(
                    '//div[@class="panel-body"]//div[@class="col-md-8"]/img[@src="images/shondrive.jpg"]/@src'
                )
            ).strip()
            if shop_n_drive_logo:
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
