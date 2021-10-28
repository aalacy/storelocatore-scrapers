# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser
import json

website = "ihopmexico.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.ihopmexico.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.ihopmexico.com/sucursales/"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        search_res = session.get(search_url, headers=headers)
        stores_obj = json.loads(
            search_res.text.split("var wpgmaps_localize_marker_data =")[1]
            .strip()
            .split("}};")[0]
            .strip()
            + "}}"
        )
        for obj_key in stores_obj.keys():
            stores_dict = stores_obj[obj_key]
            for key in stores_dict.keys():
                store = stores_dict[key]
                page_url = store["linkd"]
                locator_domain = website
                location_name = store["title"]

                raw_address = store["desc"].replace("\n", ", ").strip()
                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                state = formatted_addr.state
                zip = formatted_addr.postcode

                country_code = "MX"

                store_number = store["marker_id"]

                phone = ""
                hours_of_operation = ""
                if page_url:
                    log.info(page_url)
                    try:
                        page_res = SgRequests.raise_on_err(
                            session.get(page_url, headers=headers)
                        )
                        page_sel = lxml.html.fromstring(page_res.text)
                        headers_text = page_sel.xpath("//h4")
                        for hd in headers_text:
                            header = (
                                "".join(hd.xpath("text()"))
                                .encode("ascii", "ignore")
                                .decode("utf-8")
                            )
                            if "Telfono" == header:
                                phone = "".join(
                                    hd.xpath("following-sibling::p[1]//text()")
                                ).strip()
                            if "Horas de operacin" == header:
                                hours = hd.xpath("following-sibling::*//text()")
                                hours_list = []
                                for index in range(1, len(hours)):
                                    if "Direccin" in "".join(
                                        hours[index]
                                    ).strip().encode("ascii", "ignore").decode("utf-8"):
                                        break
                                    else:
                                        if (
                                            "Capacidad de aforo"
                                            not in "".join(hours[index]).strip()
                                        ):
                                            hours_list.append(
                                                "".join(hours[index]).strip()
                                            )
                                hours_of_operation = "; ".join(hours_list).strip()
                    except SgRequestError as e:
                        page_url = "<MISSING>"
                        log.error(e.message)
                        pass

                location_type = "<MISSING>"

                latitude = store["lat"]
                longitude = store["lng"]

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
