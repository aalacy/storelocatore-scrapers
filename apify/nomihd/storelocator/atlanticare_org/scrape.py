# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "atlanticare.org"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        temp_list = []  # ignoring duplicates
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)

        log.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    # Your scraper here
    loc_list = []

    search_url = "https://www.atlanticare.org/find-a-location/?page=1&count=10000"
    stores_req = session.get(search_url, headers=headers)
    json_text = (
        stores_req.text.split("var moduleInstanceData_IH_PublicDetailView")[-1]
        .strip()
        .split("=", 1)[1]
        .strip()
        .split("};")[0]
        .strip()
        + "}"
    )
    json_data = json.loads(json_text)
    stores = json.loads(json_data["SettingsData"].encode("utf-8"))["MapItems"]
    for store in stores:
        page_url = "https://www.atlanticare.org" + store["DirectUrl"]

        locator_domain = website
        location_name = store["Title"].split(",")[0].strip()
        if location_name == "":
            location_name = "<MISSING>"

        address = store["LocationAddress"]
        street_address = "".join(address.split(",")[:-2]).strip()
        city = address.split(",")[-2].strip()
        state = address.split(",")[-1].strip().rsplit(" ", 1)[0].strip()
        zip = address.split(",")[-1].strip().rsplit(" ", 1)[1].strip()

        is_digit = True
        for z in zip:
            if z.isalpha():
                is_digit = False
                break

        if is_digit is False:
            state = state + " " + zip
            zip = "<MISSING>"

        zip = zip.encode("ascii", "replace").decode("utf-8").replace("?", "").strip()
        country_code = "<MISSING>"

        if street_address == "" or street_address is None:
            street_address = "<MISSING>"

        if city == "" or city is None:
            city = "<MISSING>"

        if state == "" or state is None:
            state = "<MISSING>"

        if zip == "" or zip is None:
            zip = "<MISSING>"

        store_number = "<MISSING>"
        phone = store["LocationPhoneNum"]

        latitude = ""
        longitude = ""
        if "Latitude" in store:
            latitude = store["Latitude"]

        if "Longitude" in store:
            longitude = store["Longitude"]

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        location_type = ""
        hours_of_operation = ""

        store_req = session.get(page_url, headers=headers)
        store_json_text = (
            store_req.text.split("var moduleInstanceData_IH_PublicDetailView")[-1]
            .strip()
            .split("=", 1)[1]
            .strip()
            .split("};")[0]
            .strip()
            + "}"
        )
        store_json_data = json.loads(store_json_text)
        store_json = json.loads(store_json_data["SettingsData"].encode("utf-8"))

        temp_fields = store_json["StaticPageZones"][0]["Value"]["FieldColumns"]
        loc_type_list = []
        for field in temp_fields:
            sub_fields = field["Fields"]
            for s in sub_fields:
                if "Services" == s["FieldName"]:
                    FieldColumns = s["FieldColumns"]
                    for col in FieldColumns:
                        fields = col["Fields"]
                        for f in fields:
                            if "ServiceName" == f["FieldName"]:
                                loc_type_list.append(f["Value"])

                if "LocationHours" == s["FieldName"]:
                    hours_of_operation = ";".join(s["Values"]).strip()

        location_type = ";".join(loc_type_list).strip()

        if location_type == "":
            location_type = "<MISSING>"

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"

        if phone == "" or phone is None:
            phone = "<MISSING>"

        curr_list = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            zip,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]

        loc_list.append(curr_list)

        # break
    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
