import csv
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    url = "https://italianvillagepizza.com/wp-admin/admin-ajax.php"

    payload = '------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="address"\r\n\r\n28602\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="formdata"\r\n\r\naddressInput=28602\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="lat"\r\n\r\n35.6703562\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="lng"\r\n\r\n-81.36194019999999\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="name"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[bubblelayout]"\r\n\r\n<div id="slp_info_bubble_[slp_location id]" class="slp_info_bubble [slp_location featured]">\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span id="slp_bubble_name"><strong>[slp_location name  suffix  br]</strong></span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span id="slp_bubble_address">[slp_location address       suffix  br]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span id="slp_bubble_address2">[slp_location address2      suffix  br]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span id="slp_bubble_city">[slp_location city          suffix  comma]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span id="slp_bubble_state">[slp_location state suffix    space]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span id="slp_bubble_zip">[slp_location zip suffix  br]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span id="slp_bubble_country"><span id="slp_bubble_country">[slp_location country       suffix  br]</span></span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span id="slp_bubble_directions">[html br ifset directions]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_option label_directions wrap directions]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span id="slp_bubble_website">[html br ifset url][slp_location web_link][html br ifset url]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span id="slp_bubble_email">[slp_location email         wrap    mailto ][slp_option label_email ifset email][html closing_anchor ifset email][html br ifset email]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span id="slp_bubble_phone">[html br ifset phone]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="location_detail_label">[slp_option   label_phone   ifset   phone]</span>[slp_location phone         suffix    br]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span id="slp_bubble_fax"><span class="location_detail_label">[slp_option   label_fax     ifset   fax  ]</span>[slp_location fax           suffix    br]<span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span id="slp_bubble_description"><span id="slp_bubble_description">[html br ifset description]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_location description raw]</span>[html br ifset description]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span id="slp_bubble_hours">[html br ifset hours]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="location_detail_label">[slp_option   label_hours   ifset   hours]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="location_detail_hours">[slp_location hours         suffix    br]</span></span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span id="slp_bubble_img">[html br ifset img]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_location image         wrap    img]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span id="slp_tags">[slp_location tags]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="</div>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[distance_unit]"\r\n\r\nmiles\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[ignore_radius]"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[immediately_show_locations]"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[initial_radius]"\r\n\r\n10000\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[initial_results_returned]"\r\n\r\n25\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[label_directions]"\r\n\r\nDirections\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[label_email]"\r\n\r\nEmail\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[label_fax]"\r\n\r\nFax\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[label_phone]"\r\n\r\nPhone\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[label_website]"\r\n\r\nWebsite\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[map_center]"\r\n\r\nPittsburgh\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[map_center_lat]"\r\n\r\n40.4406° N\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[map_center_lng]"\r\n\r\n79.9959° W\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[map_domain]"\r\n\r\nmaps.google.com\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[map_end_icon]"\r\n\r\nhttp://italianvillagepizza.com/wp-content/plugins/store-locator-le/images/icons/bulb_azure.png\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[map_home_icon]"\r\n\r\nhttp://italianvillagepizza.com/wp-content/plugins/store-locator-le/images/icons/box_yellow_home.png\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[map_type]"\r\n\r\nroadmap\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[message_no_results]"\r\n\r\nNo locations found.\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[message_no_api_key]"\r\n\r\nThis site most likely needs a Google Maps API key.\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[no_autozoom]"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[no_homeicon_at_start]"\r\n\r\n1\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[radii]"\r\n\r\n10,25,50,100,(200),500\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[radius_behavior]"\r\n\r\nalways_use\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[results_layout]"\r\n\r\n<div id="slp_results_[slp_location id]" class="results_entry location_primary [slp_location featured]">\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<div class="results_row_left_column"   id="slp_left_cell_[slp_location id]"   >"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="location_name">[slp_location name] [slp_location uml_buttons] [slp_location gfi_buttons]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="location_distance">[slp_location distance format="decimal1"] [slp_option distance_unit]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="</div>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<div class="results_row_center_column location_secondary" id="slp_center_cell_[slp_location id]" >"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="slp_result_address slp_result_street">[slp_location address]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="slp_result_address slp_result_street2">[slp_location address2]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="slp_result_address slp_result_citystatezip">[slp_location city_state_zip]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="slp_result_address slp_result_country">[slp_location country]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="slp_result_address slp_result_phone">[slp_location phone]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="slp_result_address slp_result_fax">[slp_location fax]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="</div>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<div class="results_row_right_column location_tertiary"  id="slp_right_cell_[slp_location id]"  >"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="slp_result_contact slp_result_website">[slp_location web_link raw]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="slp_result_contact slp_result_email">[slp_location email_link]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="slp_result_contact slp_result_directions"><a href="http"\r\n\r\n//[slp_option map_domain]/maps?saddr=[slp_location search_address]&amp;daddr=[slp_location location_address]" target="_blank" class="storelocatorlink">[slp_option label_directions]</a></span>\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="slp_result_contact slp_result_hours">[slp_location hours format text]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_location pro_tags raw]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_location iconarray wrap="fullspan"]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_location eventiconarray wrap="fullspan"]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_location socialiconarray wrap="fullspan"]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="</div>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="</div>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[slplus_version]"\r\n\r\n4.5.09\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[use_sensor]"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[zoom_level]"\r\n\r\n12\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[zoom_tweak]"\r\n\r\n1\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[layout]"\r\n\r\n<div id="sl_div">[slp_search][slp_map][slp_results]</div>\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[maplayout]"\r\n\r\n[slp_mapcontent][slp_maptagline]\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[resultslayout]"\r\n\r\n<div id="slp_results_[slp_location id]" class="results_entry location_primary [slp_location featured]">\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<div class="results_row_left_column"   id="slp_left_cell_[slp_location id]"   >"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_addon section=primary position=first]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="location_name">[slp_location name] [slp_location uml_buttons] [slp_location gfi_buttons]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="location_distance">[slp_location distance_1] [slp_location distance_unit]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_addon section=primary position=last]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="</div>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<div class="results_row_center_column location_secondary" id="slp_center_cell_[slp_location id]" >"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_addon section=secondary position=first]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="slp_result_address slp_result_street">[slp_location address]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="slp_result_address slp_result_street2">[slp_location address2]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="slp_result_address slp_result_citystatezip">[slp_location city_state_zip]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="slp_result_address slp_result_country">[slp_location country]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="slp_result_address slp_result_phone">[slp_location phone]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="slp_result_address slp_result_fax">[slp_location fax]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_addon section=secondary position=last]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="</div>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<div class="results_row_right_column location_tertiary"  id="slp_right_cell_[slp_location id]"  >"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_addon section=tertiary position=first]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="slp_result_contact slp_result_website">[slp_location web_link]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="slp_result_contact slp_result_email">[slp_location email_link]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="slp_result_contact slp_result_directions"><a href="http"\r\n\r\n//[slp_option map_domain]/maps?saddr=[slp_location search_address]&daddr=[slp_location location_address]" target="_blank" class="storelocatorlink">[slp_location directions_text]</a></span>\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<span class="slp_result_contact slp_result_hours">[slp_location hours]</span>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_location pro_tags]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_location iconarray wrap="fullspan"]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_location eventiconarray wrap="fullspan"]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_location socialiconarray wrap="fullspan"]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_addon section=tertiary position=last]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="</div>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="</div>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[searchlayout]"\r\n\r\n<div id="address_search">\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_search_element add_on location="very_top"]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_search_element input_with_label="name"]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_search_element input_with_label="address"]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_search_element dropdown_with_label="city"]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_search_element dropdown_with_label="state"]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_search_element dropdown_with_label="country"]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_search_element selector_with_label="tag"]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_search_element dropdown_with_label="category"]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_search_element dropdown_with_label="gfl_form_id"]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_search_element add_on location="before_radius_submit"]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="<div class="search_item">"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_search_element dropdown_with_label="radius"]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_search_element button="submit"]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="</div>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_search_element add_on location="after_radius_submit"]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="[slp_search_element add_on location="very_bottom"]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="</div>"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[theme]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[id]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[hide_search_form]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[force_load_js]"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="options[map_region]"\r\n\r\nus\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="radius"\r\n\r\n500\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="tags"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="action"\r\n\r\ncsl_ajax_search\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--'
    headers = {
        "content-type": "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        "cache-control": "no-cache",
        "postman-token": "785a755e-8055-8bdf-4413-cd9eb2870765",
    }
    page_url = "https://italianvillagepizza.com/stores/"
    json_data = session.post(url, data=payload, headers=headers).json()
    for value in json_data["response"]:

        location_name = "Pizza Shop in " + value["name"]
        street_address = (
            (value["address"].strip() + " " + value["address2"].strip())
            .strip()
            .replace("&#039;", "")
            .replace("Highway 70", "Highway 70 SE")
            .title()
            .replace("2Nd", "2nd")
            .replace("3Rd", "3rd")
            .replace(" Us ", " US ")
            .replace(" Se", " SE")
        )
        city = value["name"].replace("Downtown", "").replace("FL", "").strip()
        state = value["state"]
        zipp = value["zip"]
        country_code = "US"
        store_number = value["id"]
        location_type = "<MISSING>"
        latitude = value["lat"]
        longitude = value["lng"]

        page_url = "https://italianvillagepizza.com/" + str(
            value["name"].lower().replace(" ", "-")
        )
        soup = BeautifulSoup(session.get(page_url).content, "lxml")
        try:
            hours = " ".join(
                list(
                    soup.find(
                        lambda tag: (tag.name == "h2")
                        and "Hours of Operation" in tag.text
                    )
                    .findNext("p")
                    .stripped_strings
                )
            )

        except:
            hours = "<MISSING>"

        try:
            phone = re.findall(r"[(\d)]{5}.[\d]{3}-[\d]{4}", str(soup))[0]
        except:
            try:
                phone = re.findall(r"[\d]{3}.[\d]{3}-[\d]{4}", str(soup))[0]
            except:
                if "2522155915" in str(soup):
                    phone = "2522155915"
                else:
                    phone = "<MISSING>"

        if "page wasn't found" in str(soup):
            page_url = "<MISSING>"

        store = []
        store.append("https://italianvillagepizza.com/")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours)
        store.append(page_url)
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
