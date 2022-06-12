# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.simple_utils import parallelize
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list

website = "midlandsb.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Content-type": "application/x-www-form-urlencoded",
    "Accept": "*/*",
    "Origin": "https://midlandsb.locatorsearch.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}

add_list = []


def fetch_records_for(coords):
    lat = coords[0]
    lng = coords[1]
    log.info(f"pulling records for coordinates: {lat,lng}")

    search_url = " https://midlandsb.locatorsearch.com/GetItems.aspx"
    data = {
        "lat": lat,
        "lng": lng,
        "searchby": "FCSL|",
        "SearchKey": "",
        "rnd": "1589454899459",
    }

    stores = []
    try:
        stores_req = session.post(search_url, headers=headers, data=data)
        stores_sel = lxml.html.fromstring(
            stores_req.text.split("?>")[1]
            .strip()
            .replace("<![CDATA[", "")
            .replace("]]>", "")
            .replace("<br>", "\n")
        )
        stores = stores_sel.xpath("//markers//marker")

    except:
        pass

    return stores


def process_record(raw_results_from_one_coordinate):
    stores = raw_results_from_one_coordinate

    for store in stores:
        page_url = "<MISSING>"
        location_name = "".join(store.xpath("tab/title/text()")).strip()
        location_type = "".join(store.xpath("@icon")).strip()
        if "branch_" in location_type:
            location_type = "Branch"
        else:
            location_type = "ATM"

        locator_domain = website
        phone = "".join(store.xpath("tab/add2/b/text()")).strip()

        street_address = "".join(store.xpath("tab/add1/text()")).strip()
        unique_ID = f"{street_address} - {location_name}"
        if unique_ID in add_list:
            continue

        add_list.append(unique_ID)
        city_state_zip = "".join(store.xpath("tab/add2/text()")).strip()

        city = city_state_zip.strip().split(",")[0].strip()
        state = city_state_zip.strip().split(",")[1].strip().split(" ")[0].strip()
        zipp = city_state_zip.strip().split(",")[1].strip().split(" ")[-1].strip()

        hours = store.xpath("tab/contents/div/table/tr")
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath("td[1]/text()")).strip()
            time = "".join(hour.xpath("td[2]/text()")).strip()
            hours_list.append(day + time)

        hours_of_operation = "; ".join(hours_list).strip()
        country_code = "US"
        store_number = "<MISSING>"

        latitude = "".join(store.xpath("@lat")).strip()
        longitude = "".join(store.xpath("@lng")).strip()
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
        results = parallelize(
            search_space=static_coordinate_list(
                radius=200, country_code=SearchableCountries.USA
            ),
            fetch_results_for_rec=fetch_records_for,
            processing_function=process_record,
            max_threads=20,  # tweak to see what's fastest
        )
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
