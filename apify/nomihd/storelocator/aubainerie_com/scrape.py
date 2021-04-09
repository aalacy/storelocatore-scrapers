# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "aubainerie.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "scu2ms436gx80018015-rs.su.retail.dynamics.com",
    "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    "odata-version": "4.0",
    "prefer": "return=representation",
    "accept-language": "en-AU",
    "sec-ch-ua-mobile": "?0",
    "requestid": "c123180810bb3244843872df16d7942d/1",
    "from-keystone": "true",
    "content-type": "application/json;charset=UTF-8",
    "accept": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    "contenttype": "application/json",
    "request-id": "|rB9GU.uCQCE",
    "odata-maxversion": "4.0",
    "oun": "M100",
    "origin": "https://www.aubainerie.com",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.aubainerie.com/",
}


def format_time(time):
    if ".5" in time:
        time = time.replace(".5", "") + ":30"
    elif ".0" in time:
        time = time.replace(".0", "") + ":00"

    return time


def fetch_data():
    # Your scraper here
    search_url = "https://scu2ms436gx80018015-rs.su.retail.dynamics.com/Commerce/OrgUnits/GetOrgUnitLocationsByArea?$top=1000&api-version=7.3"

    data = '{"searchArea":{"Latitude":45.5017,"Longitude":73.5673,"Radius":100000,"DistanceUnitValue":1}}'

    stores_req = session.post(search_url, data=data, headers=headers)
    stores = json.loads(stores_req.text)["value"]
    for store in stores:
        page_url = "https://www.aubainerie.com/en/" + store["OrgUnitNumber"]
        locator_domain = website
        location_name = store["OrgUnitName"]
        street_address = store["Street"]
        city = store["City"]
        location_name = city
        state = store["State"]
        zip = store["Zip"]

        country_code = store["Country"]
        if country_code == "CAN":
            country_code = "CA"

        store_number = store["OrgUnitNumber"]
        location_type = "<MISSING>"

        phone = store["Contacts"][0]["Locator"]
        log.info(store_number)
        hours_url = "https://scu2ms436gx80018015-rs.su.retail.dynamics.com/Commerce/OrgUnits/GetStoreHours(storeNumber='{}')?api-version=7.3"
        hours_req = session.get(hours_url.format(store_number), headers=headers)
        hours_of_operation = ""
        hours_list = []
        if "RegularStoreHours" in hours_req.text:
            hours = json.loads(hours_req.text)["RegularStoreHours"]
            if hours is not None:
                if hours["IsClosedOnMonday"] is False:
                    open_time = format_time(str(hours["MondayOpenTime"] / 3600))
                    close_time = format_time(str(hours["MondayCloseTime"] / 3600))
                    hours_list.append("Monday:" + open_time + "-" + close_time)
                else:
                    hours_list.append("Monday:Closed")

                if hours["IsClosedOnTuesday"] is False:
                    open_time = format_time(str(hours["TuesdayOpenTime"] / 3600))
                    close_time = format_time(str(hours["TuesdayCloseTime"] / 3600))
                    hours_list.append("Tuesday:" + open_time + "-" + close_time)
                else:
                    hours_list.append("Tuesday:Closed")

                if hours["IsClosedOnWednesday"] is False:
                    open_time = format_time(str(hours["WednesdayOpenTime"] / 3600))
                    close_time = format_time(str(hours["WednesdayCloseTime"] / 3600))
                    hours_list.append("Wednesday:" + open_time + "-" + close_time)
                else:
                    hours_list.append("Wednesday:Closed")

                if hours["IsClosedOnThursday"] is False:
                    open_time = format_time(str(hours["ThursdayOpenTime"] / 3600))
                    close_time = format_time(str(hours["ThursdayCloseTime"] / 3600))
                    hours_list.append("Thursday:" + open_time + "-" + close_time)
                else:
                    hours_list.append("Thursday:Closed")

                if hours["IsClosedOnFriday"] is False:
                    open_time = format_time(str(hours["FridayOpenTime"] / 3600))
                    close_time = format_time(str(hours["FridayCloseTime"] / 3600))
                    hours_list.append("Friday:" + open_time + "-" + close_time)
                else:
                    hours_list.append("Friday:Closed")

                if hours["IsClosedOnSaturday"] is False:
                    open_time = format_time(str(hours["SaturdayOpenTime"] / 3600))
                    close_time = format_time(str(hours["SaturdayCloseTime"] / 3600))
                    hours_list.append("Saturday:" + open_time + "-" + close_time)
                else:
                    hours_list.append("Saturday:Closed")

                if hours["IsClosedOnSunday"] is False:
                    open_time = format_time(str(hours["SundayOpenTime"] / 3600))
                    close_time = format_time(str(hours["SundayCloseTime"] / 3600))
                    hours_list.append("Sunday:" + open_time + "-" + close_time)
                else:
                    hours_list.append("Sunday:Closed")

                hours_of_operation = "; ".join(hours_list).strip()
            else:
                hours_of_operation = "<MISSING>"
        else:
            hours_of_operation = "<MISSING>"

        latitude = store["Latitude"]
        longitude = store["Longitude"]

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
