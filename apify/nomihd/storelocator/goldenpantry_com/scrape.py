# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import us

website = "goldenpantry.com"
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

    search_url = "https://www.goldenpantry.com/wp-admin/admin-ajax.php"
    data = {
        "address": "",
        "formdata": "addressInput=&cat=0",
        "lat": "",
        "lng": "",
        "name": "",
        "options[bubblelayout]": '<div id="sl_info_bubble" class="[slp_location featured]">\n<span id="slp_bubble_name"><strong>[slp_location name  suffix  br]</strong></span>\n<span id="slp_bubble_address">[slp_location address       suffix  br]</span>\n<span id="slp_bubble_address2">[slp_location address2      suffix  br]</span>\n<span id="slp_bubble_city">[slp_location city          suffix  comma]</span>\n<span id="slp_bubble_state">[slp_location state suffix    space]</span>\n<span id="slp_bubble_zip">[slp_location zip suffix  br]</span>\n<span id="slp_bubble_country"><span id="slp_bubble_country">[slp_location country       suffix  br]</span></span>\n<span id="slp_bubble_directions">[html br ifset directions]\n[slp_option label_directions wrap directions]</span>\n<span id="slp_bubble_website">[html br ifset url]\n[slp_location url           wrap    website][slp_option label_website ifset url][html closing_anchor ifset url][html br ifset url]</span>\n<span id="slp_bubble_email">[slp_location email         wrap    mailto ][slp_option label_email ifset email][html closing_anchor ifset email][html br ifset email]</span>\n<span id="slp_bubble_phone">[html br ifset phone]\n<span class="location_detail_label">[slp_option   label_phone   ifset   phone]</span>[slp_location phone         suffix    br]</span>\n<span id="slp_bubble_fax"><span class="location_detail_label">[slp_option   label_fax     ifset   fax  ]</span>[slp_location fax           suffix    br]<span>\n<span id="slp_bubble_description"><span id="slp_bubble_description">[html br ifset description]\n[slp_location description raw]</span>[html br ifset description]</span>\n<span id="slp_bubble_hours">[html br ifset hours]\n<span class="location_detail_label">[slp_option   label_hours   ifset   hours]</span>\n<span class="location_detail_hours">[slp_location hours         suffix    br]</span></span>\n<span id="slp_bubble_img">[html br ifset img]\n[slp_location image         wrap    img]</span>\n<span id="slp_tags">[slp_location tags]</span>\n</div>',
        "options[distance_unit]": "miles",
        "options[immediately_show_locations]": "0",
        "options[initial_radius]": "10000",
        "options[initial_results_returned]": "10000",
        "options[label_directions]": "Directions",
        "options[label_email]": "Email",
        "options[label_fax]": "Fax: ",
        "options[label_hours]": "Hours: ",
        "options[label_phone]": "Phone: ",
        "options[label_website]": "Website",
        "options[map_domain]": "maps.google.com",
        "options[slplus_version]": "4.2.08",
        "options[ignore_radius]": "1",
        "options[theme]": "",
        "options[id]": "",
        "options[hide_search_form]": "",
        "options[only_with_category]": "",
        "options[endicon]": "",
        "options[homeicon]": "",
        "options[only_with_tag]": "",
        "options[tags_for_pulldown]": "",
        "options[tags_for_dropdown]": "",
        "options[hide_results]": "0",
        "options[order_by]": "sl_distance ASC",
        "options[use_sensor]": "false",
        "options[add_tel_to_phone]": "0",
        "options[extended_data_version]": "4.2.06",
        "options[installed_version]": "4.2.06",
        "options[orderby]": "sl_distance ASC",
        "options[resultslayout]": '<div id="slp_results_[slp_location id]" class="results_entry  [slp_location featured]">\r\n    <div class="results_row_left_column"   id="slp_left_cell_[slp_location id]"   >\r\n        <span class="location_name">[slp_location name]</span>\r\n        <span class="location_distance">[slp_location distance_1] [slp_location distance_unit]</span>\r\n    </div>\r\n    <div class="results_row_center_column" id="slp_center_cell_[slp_location id]" >\r\n        <span class="slp_result_address slp_result_street">[slp_location address]</span>\r\n        <span class="slp_result_address slp_result_street2">[slp_location address2]</span>\r\n        <span class="slp_result_address slp_result_citystatezip">[slp_location city_state_zip]</span>\r\n        <span class="slp_result_address slp_result_country">[slp_location country]</span>\r\n        <span class="slp_result_address slp_result_phone">[slp_location phone]</span>\r\n        <span class="slp_result_address slp_result_fax">[slp_location fax]</span>\r\n    </div>\r\n    <div class="results_row_right_column"  id="slp_right_cell_[slp_location id]"  >\r\n         <span class="slp_result_contact slp_result_website">[slp_location web_link]</span>\r\n        <span class="slp_result_contact slp_result_email">[slp_location email_link]</span>\r\n        <span class="slp_result_contact slp_result_directions"><a href="http://[slp_location map_domain]/maps?saddr=[slp_location search_address]&daddr=[slp_location location_address]" target="_blank" class="storelocatorlink">[slp_location directions_text]</a></span>\r\n        <span class="slp_result_contact slp_result_hours">[slp_location hours]</span>\r\n<span class="slp_location_description">[slp_location <description>]</span>\r\n        [slp_location iconarray wrap="fullspan"]\r\n        [slp_location socialiconarray wrap="fullspan"]\r\n        </div>\r\n</div>',
        "options[show_country]": "1",
        "options[show_hours]": "1",
        "options[featured_location_display_type]": "show_within_radius",
        "options[email_link_format]": "label_link",
        "options[popup_email_title]": "Send An Email",
        "options[popup_email_from_placeholder]": "Your email address.",
        "options[popup_email_subject_placeholder]": "Email subject line.",
        "options[popup_email_message_placeholder]": "What do you want to say?",
        "radius": "50000",
        "tags": "",
        "action": "csl_ajax_search",
    }

    stores_req = session.post(search_url, data=data, headers=headers)
    stores = json.loads(stores_req.text)["response"]

    for store in stores:
        page_url = "<MISSING>"

        locator_domain = website
        location_name = "Golden Pantry"
        if location_name == "":
            location_name = "<MISSING>"

        street_address = store["address"]
        if store["address2"] is not None:
            if len(store["address2"]) > 0:
                street_address = street_address + ", " + store["address2"]

        city = store["city"]
        state = store["state"]
        zip = store["zip"]

        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        if street_address == "" or street_address is None:
            street_address = "<MISSING>"

        if city == "" or city is None:
            city = "<MISSING>"

        if state == "" or state is None:
            state = "<MISSING>"

        if zip == "" or zip is None:
            zip = "<MISSING>"

        store_number = str(store["id"])
        phone = store["phone"]

        location_type = "<MISSING>"
        latitude = store["lat"]
        longitude = store["lng"]

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        hours_of_operation = store["hours"]
        try:
            hours_of_operation = (
                hours_of_operation.split("&")[0].strip().replace("Store:", "").strip()
            )
        except:
            pass

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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
