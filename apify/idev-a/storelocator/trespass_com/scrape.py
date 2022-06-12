import csv
import json
from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
    base_url = "https://www.trespass.com"
    headers = {
        "accept": "*/*",
        "content-length": "26",
        "content-type": "application/json",
        "cookie": "visid_incap_155660=ijdSwwTfRrSKi0smiRjCFJEDHWAAAAAAQUIPAAAAAAD/Tdu08l+pD+kLfCxmz+Og; PHPSESSID=g2tha85sb0hv8ufns6hebjr41o; mage-cache-storage=%7B%7D; mage-cache-storage-section-invalidation=%7B%7D; scarab.visitor=%223380A1AF4DCAF6BF%22; mage-cache-sessid=true; form_key=I55SJQUjb9KpoN7A; tp-gtm=%7B%7D; user_allowed_save_cookie=%7B%222%22%3A1%7D; _gcl_au=1.1.1681512164.1612514222; _ga=GA1.2.228596128.1612514225; _gid=GA1.2.154591611.1612514225; mage-messages=; _gaexp=GAX1.2.aFEkZ1IAS1SM_l9WBoEs_Q.18747.0; _hjTLDTest=1; _hjid=20002ad0-f8b5-41e2-b113-ec5a0d55dd0a; recently_viewed_product=%7B%7D; recently_viewed_product_previous=%7B%7D; recently_compared_product=%7B%7D; recently_compared_product_previous=%7B%7D; product_data_storage=%7B%7D; incap_ses_1203_155660=nZuQUPCT+FWgU7KQU+qxEF2uHWAAAAAAel7j/ubxAdEQnKjiPKsuQg==; incap_ses_244_155660=X5DdJkRaqSCdGfei6txiA16uHWAAAAAAmx+/Jb0U4CE5O0cd0fBOQw==; _dc_gtm_UA-10998809-1=1; _hjIncludedInSessionSample=1; _hjAbsoluteSessionInProgress=0; _uetsid=54dc2570678d11eba8ef6dc429bc8a1d; _uetvid=54dc5610678d11eb9622cd825545f9a2; section_data_ids=%7B%22customer%22%3A1612557968%2C%22cart%22%3A1612557970%7D",
        "origin": "https://www.trespass.com",
        "referer": "https://www.trespass.com/storelocator/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    data = {"existingStoreValues": ""}
    res = session.post(
        "https://www.trespass.com/rest/V1/ajax/getStoreMapMarkers",
        headers=headers,
        json=data,
    )
    store_list = json.loads(json.loads(res.text))
    data = []
    for store in store_list:
        page_url = "https://www.trespass.com/stores/" + store["url"]
        location_name = store["name"].replace("&#x20;", " ")
        phone = store["phone"].replace("&#x20;", " ").replace("&#x2B;", "+")
        city = store["city"].replace("&#x20;", " ").replace("&#x27;", "'")
        zip = store["postcode"].replace("&#x20;", " ")
        state = store["county"].replace("&#x20;", " ") or "<MISSING>"
        street_address = (
            store["address"]
            .replace("&#x20;", " ")
            .replace("&#x27;", "'")
            .replace("&#x2F;", "/")
        )
        country_code = store["country"]
        if country_code != "GB":
            continue
        store_number = store["store_id"]
        location_type = "<MISSING>"
        latitude = store["lat"]
        longitude = store["lng"]
        hours_of_operation = (
            "Monday: "
            + store["monday_open"].replace("&#x3A;", ":")
            + "-"
            + store["monday_close"].replace("&#x3A;", ":")
            + " "
        )
        hours_of_operation += (
            "Tuesday: "
            + store["tuesday_open"].replace("&#x3A;", ":")
            + "-"
            + store["tuesday_close"].replace("&#x3A;", ":")
            + " "
        )
        hours_of_operation += (
            "Wednesday: "
            + store["wednesday_open"].replace("&#x3A;", ":")
            + "-"
            + store["wednesday_close"].replace("&#x3A;", ":")
            + " "
        )
        hours_of_operation += (
            "Thursday: "
            + store["thursday_open"].replace("&#x3A;", ":")
            + "-"
            + store["thursday_close"].replace("&#x3A;", ":")
            + " "
        )
        hours_of_operation += (
            "Friday: "
            + store["friday_open"].replace("&#x3A;", ":")
            + "-"
            + store["friday_close"].replace("&#x3A;", ":")
            + " "
        )
        hours_of_operation += (
            "Saturday: "
            + store["saturday_open"].replace("&#x3A;", ":")
            + "-"
            + store["saturday_close"].replace("&#x3A;", ":")
            + " "
        )
        hours_of_operation += (
            "Sunday: "
            + store["sunday_open"].replace("&#x3A;", ":")
            + "-"
            + store["sunday_close"].replace("&#x3A;", ":")
            + " "
        )
        data.append(
            [
                base_url,
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
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
