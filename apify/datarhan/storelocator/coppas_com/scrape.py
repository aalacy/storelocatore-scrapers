import re
import csv

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://www.coppas.com/wp-admin/admin-ajax.php"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    frm = "address=&formdata=addressInput%3D&lat=43.653226&lng=-79.3831843&name=&options%5Bbubblelayout%5D=%3Cdiv+id%3D%22sl_info_bubble%22+class%3D%22%5Bslp_location+featured%5D%22%3E%0A%3Cspan+id%3D%22slp_bubble_name%22%3E%3Cstrong%3E%5Bslp_location+name++suffix++br%5D%3C%2Fstrong%3E%3C%2Fspan%3E%0A%3Cspan+id%3D%22slp_bubble_address%22%3E%5Bslp_location+address+++++++suffix++br%5D%3C%2Fspan%3E%0A%3Cspan+id%3D%22slp_bubble_address2%22%3E%5Bslp_location+address2++++++suffix++br%5D%3C%2Fspan%3E%0A%3Cspan+id%3D%22slp_bubble_city%22%3E%5Bslp_location+city++++++++++suffix++comma%5D%3C%2Fspan%3E%0A%3Cspan+id%3D%22slp_bubble_state%22%3E%5Bslp_location+state+suffix++++space%5D%3C%2Fspan%3E%0A%3Cspan+id%3D%22slp_bubble_zip%22%3E%5Bslp_location+zip+suffix++br%5D%3C%2Fspan%3E%0A%3Cspan+id%3D%22slp_bubble_country%22%3E%3Cspan+id%3D%22slp_bubble_country%22%3E%5Bslp_location+country+++++++suffix++br%5D%3C%2Fspan%3E%3C%2Fspan%3E%0A%3Cspan+id%3D%22slp_bubble_directions%22%3E%5Bhtml+br+ifset+directions%5D%0A%5Bslp_option+label_directions+wrap+directions%5D%3C%2Fspan%3E%0A%3Cspan+id%3D%22slp_bubble_website%22%3E%5Bhtml+br+ifset+url%5D%0A%5Bslp_location+url+++++++++++wrap++++website%5D%5Bslp_option+label_website+ifset+url%5D%5Bhtml+closing_anchor+ifset+url%5D%5Bhtml+br+ifset+url%5D%3C%2Fspan%3E%0A%3Cspan+id%3D%22slp_bubble_email%22%3E%5Bslp_location+email+++++++++wrap++++mailto+%5D%5Bslp_option+label_email+ifset+email%5D%5Bhtml+closing_anchor+ifset+email%5D%5Bhtml+br+ifset+email%5D%3C%2Fspan%3E%0A%3Cspan+id%3D%22slp_bubble_phone%22%3E%5Bhtml+br+ifset+phone%5D%0A%3Cspan+class%3D%22location_detail_label%22%3E%5Bslp_option+++label_phone+++ifset+++phone%5D%3C%2Fspan%3E%5Bslp_location+phone+++++++++suffix++++br%5D%3C%2Fspan%3E%0A%3Cspan+id%3D%22slp_bubble_fax%22%3E%3Cspan+class%3D%22location_detail_label%22%3E%5Bslp_option+++label_fax+++++ifset+++fax++%5D%3C%2Fspan%3E%5Bslp_location+fax+++++++++++suffix++++br%5D%3Cspan%3E%0A%3Cspan+id%3D%22slp_bubble_description%22%3E%3Cspan+id%3D%22slp_bubble_description%22%3E%5Bhtml+br+ifset+description%5D%0A%5Bslp_location+description+raw%5D%3C%2Fspan%3E%5Bhtml+br+ifset+description%5D%3C%2Fspan%3E%0A%3Cspan+id%3D%22slp_bubble_hours%22%3E%5Bhtml+br+ifset+hours%5D%0A%3Cspan+class%3D%22location_detail_label%22%3E%5Bslp_option+++label_hours+++ifset+++hours%5D%3C%2Fspan%3E%0A%3Cspan+class%3D%22location_detail_hours%22%3E%5Bslp_location+hours+++++++++suffix++++br%5D%3C%2Fspan%3E%3C%2Fspan%3E%0A%3Cspan+id%3D%22slp_bubble_img%22%3E%5Bhtml+br+ifset+img%5D%0A%5Bslp_location+image+++++++++wrap++++img%5D%3C%2Fspan%3E%0A%3Cspan+id%3D%22slp_tags%22%3E%5Bslp_location+tags%5D%3C%2Fspan%3E%0A%3C%2Fdiv%3E&options%5Binitial_radius%5D=500&options%5Binitial_results_returned%5D=25&options%5Blabel_directions%5D=Directions&options%5Blabel_email%5D=Email&options%5Blabel_fax%5D=Fax%3A+&options%5Blabel_hours%5D=Hours%3A+&options%5Blabel_phone%5D=Phone%3A+&options%5Blabel_website%5D=Website&options%5Bslplus_version%5D=4.1.10&options%5Btheme%5D=&radius=500&tags=&action=csl_ajax_onload"
    data = session.post(start_url, headers=hdr, data=frm).json()

    all_locations = data["response"]
    for poi in all_locations:
        store_url = "https://www.coppas.com/my-store-2/"
        location_name = poi["name"].replace("&#039;", "'")
        street_address = poi["address"]
        if poi["address2"]:
            street_address += " " + poi["address2"]
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["zip"]
        country_code = "<MISSING>"
        store_number = poi["id"]
        phone = poi["phone"]
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lng"]
        hours_of_operation = poi["hours"].replace("\r\n", " ").split("NONNA")[0].strip()

        item = [
            domain,
            store_url,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
