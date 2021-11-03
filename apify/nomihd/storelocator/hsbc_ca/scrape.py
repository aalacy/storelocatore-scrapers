# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html

website = "hsbc.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.hsbc.ca/branch-locator/"
    home_req = session.get(search_url, headers=headers)
    home_sel = lxml.html.fromstring(home_req.text)
    data_files = "".join(
        home_sel.xpath('//div[@class="branchLocator"]/@data-dpws-tool-datafiles')
    ).strip()
    urls_list = []
    unique_list = []
    if "branches" in data_files:
        urls_list.append(json.loads(data_files)["branches"])
    if "atms" in data_files:
        urls_list.append(json.loads(data_files)["atms"])

    for url in urls_list:
        stores = []
        if "/data/branches" in url:
            stores_req = session.get(
                "https://www.hsbc.ca" + url.replace(".cdata", ".udata"),
                headers=headers,
            )
            stores = json.loads(stores_req.text)["branches"]
        elif "/data/atms" in url:
            stores_req = session.get(
                "https://www.hsbc.ca" + url.replace(".cdata", ".udata"),
                headers=headers,
            )
            stores = json.loads(stores_req.text)["atms"]

        for store in stores:
            page_url = "<MISSING>"
            locator_domain = website
            location_name = store["name"]
            street_address = ""
            if "street" in store["address"]:
                street_address = (
                    store["address"]["street"]
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", "-")
                    .strip()
                    .replace("---", "-")
                    .strip()
                )
            city = store["address"]["townOrCity"]
            state = store["address"]["stateRegionCounty"]
            zip = store["address"]["postcode"]
            country_code = "CA"
            phone = ""
            if "phoneNumber" in store:
                phone = store["phoneNumber"][list(store["phoneNumber"].keys())[0]]

            store_number = "<MISSING>"
            location_type = store["Type"]

            if street_address != "":
                unique_id = f"{street_address}+{location_type}"
                if unique_id in unique_list:
                    continue

                unique_list.append(unique_id)

            hours_list = []
            if "openingTimes" in store:
                hours = store["openingTimes"]
                for day in hours.keys():
                    if "open" in hours[day] and "close" in hours[day]:
                        time = hours[day]["open"] + "-" + hours[day]["close"]
                        if "N/A" not in time:
                            hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()
            latitude = store["coordinates"]["lat"]
            longitude = store["coordinates"]["lng"]

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
