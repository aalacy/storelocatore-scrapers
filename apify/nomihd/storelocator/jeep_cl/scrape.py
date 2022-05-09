# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "jeep.cl"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Accept": "text/html, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://www.jeep.cl",
    "Referer": "https://www.jeep.cl/concesionarios/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

data = {
    "action": "get_chile_dealers_locations",
    "region": "",
    "dealership": "",
    "filter": "",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.jeep.cl/concesionarios/"
    api_url = "https://www.jeep.cl/wp-admin/admin-ajax.php"

    with SgRequests() as session:
        api_res = session.post(api_url, headers=headers, data=data)
        location_list = json.loads(api_res.text)["dealers"]

        data["action"] = "get_chile_dealers_list"  # update action
        api_res = session.post(api_url, headers=headers, data=data)

        api_sel = lxml.html.fromstring(api_res.text)

        stores = api_sel.xpath("//li")

        data.pop("region", None)
        data.pop("dealership", None)
        data.pop("filter", None)

        for no, store in enumerate(stores, 1):

            locator_domain = website

            page_url = search_url

            headers["Referer"] = "https://www.jeep.cl/concesionarios/"

            data["action"] = "get_chile_dealers_details"
            data["id"] = str(location_list[no - 1][3])

            store_res = session.post(api_url, headers=headers, data=data)

            store_json = json.loads(store_res.text)

            location_name = "".join(store.xpath(".//h2//text()")).strip()
            location_type = "<MISSING>"

            store_info = list(
                filter(
                    str,
                    [x.strip() for x in store.xpath(".//text()")],
                )
            )

            street_address = store_json["address"]
            city = store_json["city"]

            state = store_json["region"]
            zip = "<MISSING>"

            country_code = "CL"

            store_number = data["id"]
            phone = store_info[-2]
            if ":" in phone:
                phone = phone.split(":")[1].strip()
            
            phone = (
                phone.split("/")[0]
                .strip()
                .split("-")[0]
                .strip()
                .lower()
                .split("anexo")[0]
                .strip()
            )
            if "v" == phone:
                phone = "<MISSING>"
            hours_of_operation = "<MISSING>"

            latitude, longitude = location_list[no - 1][1], location_list[no - 1][2]

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
