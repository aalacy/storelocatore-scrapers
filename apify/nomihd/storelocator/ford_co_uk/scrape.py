# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "ford.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://spatial.virtualearth.net/REST/v1/data/1652026ff3b247cd9d1f4cc12b9a080b/FordEuropeDealers_Transition/Dealer?$select=*,__Distance&$filter=Brand%20Eq%20%27Ford%27&$top=0&$inlinecount=allpages&$format=json&key=Al1EdZ_aW5T6XNlr-BJxCw1l4KaA0tmXFI_eTl1RITyYptWUS0qit_MprtcG7w2F&$skip={}"
    skip_index = 0
    with SgRequests() as session:
        while True:
            stores_req = session.get(search_url.format(str(skip_index)))
            stores = json.loads(stores_req.text)["d"]["results"]
            if len(stores) <= 0:
                break
            for store in stores:
                if (
                    store["HasSalesDepartmentPV"] is False
                    and store["HasSalesDepartmentCV"] is False
                ):
                    continue
                locator_domain = website
                location_type = "<MISSING>"

                page_url = "<MISSING>"

                location_name = store["DealerName"]

                street_address = (
                    store["AddressLine1"]
                    + " "
                    + store["AddressLine2"]
                    + " "
                    + store["AddressLine3"]
                )
                street_address = street_address.strip()
                city = store["Locality"]
                state = "<MISSING>"
                zip = store["PostCode"]
                country_code = store["Country"]
                if len(country_code) <= 0:
                    country_code = store["CountryCode"]

                phone = store["PrimaryPhone"]

                hours_list = []
                if "SalesMondayOpenTime" in store:
                    if len(store["SalesMondayOpenTime"]) > 0:
                        hours_list.append(
                            "Mon: "
                            + store["SalesMondayOpenTime"]
                            + "-"
                            + store["SalesMondayCloseTime"]
                        )
                    else:
                        hours_list.append("Mon: Closed")

                    if len(store["SalesTuesdayOpenTime"]) > 0:
                        hours_list.append(
                            "Tue: "
                            + store["SalesTuesdayOpenTime"]
                            + "-"
                            + store["SalesTuesdayCloseTime"]
                        )
                    else:
                        hours_list.append("Tue: Closed")

                    if len(store["SalesWednesdayOpenTime"]) > 0:
                        hours_list.append(
                            "Wed: "
                            + store["SalesWednesdayOpenTime"]
                            + "-"
                            + store["SalesWednesdayCloseTime"]
                        )
                    else:
                        hours_list.append("Wed: Closed")

                    if len(store["SalesThursdayOpenTime"]) > 0:
                        hours_list.append(
                            "Thu: "
                            + store["SalesThursdayOpenTime"]
                            + "-"
                            + store["SalesThursdayCloseTime"]
                        )
                    else:
                        hours_list.append("Thu: Closed")

                    if len(store["SalesFridayOpenTime"]) > 0:
                        hours_list.append(
                            "Fri: "
                            + store["SalesFridayOpenTime"]
                            + "-"
                            + store["SalesFridayCloseTime"]
                        )
                    else:
                        hours_list.append("Fri: Closed")

                    if len(store["SalesSaturdayOpenTime"]) > 0:
                        hours_list.append(
                            "Sat: "
                            + store["SalesSaturdayOpenTime"]
                            + "-"
                            + store["SalesSaturdayCloseTime"]
                        )
                    else:
                        hours_list.append("Sat: Closed")

                    if len(store["SalesSundayOpenTime"]) > 0:
                        hours_list.append(
                            "Sun: "
                            + store["SalesSundayOpenTime"]
                            + "-"
                            + store["SalesSundayCloseTime"]
                        )
                    else:
                        hours_list.append("Sun: Closed")

                hours_of_operation = "; ".join(hours_list).strip()
                if hours_of_operation.count("Closed") == 7:
                    hours_of_operation = "<MISSING>"
                store_number = store["DealerID"]

                latitude, longitude = store["Latitude"], store["Longitude"]

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
            log.info(f"pulling records starting from {skip_index}")
            skip_index = skip_index + 250


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
