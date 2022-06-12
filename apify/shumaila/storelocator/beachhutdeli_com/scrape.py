from bs4 import BeautifulSoup
from sgrequests import SgRequests
import csv

session = SgRequests()
headers = {
    "authority": "beachhutdeli.com",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():

    # Site URL
    site_url = "https://beachhutdeli.com/"
    location_url = "https://beachhutdeli.com/locations/"

    stores_req = session.get(location_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    data_list = soup.findAll("div", {"class", "row"})
    for d in data_list:
        if d.find("div", {"class", "site-content"}):
            state_list = (
                d.find("div", {"class", "site-content"})
                .find("div")
                .find("label")
                .findAll("option")
            )
    store_data = []
    for state_item in state_list:
        state = state_item["value"]
        if state != "0":
            href_url = location_url + "results/?state=" + state
            content_store = session.get(href_url, headers=headers)
            content_store = content_store.json()
            for item_content in content_store:
                location = item_content["location"]
                location_name = item_content["post_title"]
                store_number = item_content["info"]["store_number"]
                page_url = item_content["href"]
                if item_content["info"]["phone"] == "":
                    phone = "<MISSING>"
                else:
                    phone = item_content["info"]["phone"]
                store_type = "<MISSING>"
                zip = location["zip"]
                city = location["city"]
                state = location["state"]
                street_address = location["address"]
                country_code = "US"
                longitude = str(location["longitude"]).split(",")[0]
                latitude = location["latitude"]
                if item_content["info"]["hours"] == "":
                    ul_for_hours = "<MISSING>"
                else:
                    ul_for_hours = str(item_content["info"]["hours"]).replace(
                        "<br />", ""
                    )
                store_data.append(
                    [
                        site_url,
                        page_url,
                        location_name,
                        street_address,
                        city,
                        state,
                        zip,
                        country_code,
                        store_number,
                        phone,
                        store_type,
                        latitude,
                        longitude,
                        ul_for_hours,
                    ]
                )
    return store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
