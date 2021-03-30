import csv
import json

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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "nucara.com"
    start_url = "https://api-web.rxwiki.com/api/v2/location/search"

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "content-type": "application/json;charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    }

    all_locations = []
    states = ["Illinois", "Iowa", "Minnesota", "North Dakota", "Texas"]
    for state in states:
        formdata = '{"search_radius":10000,"query":"%s","page":0,"config_id":"0478a911-df76-40e0-a4a2-a6ee564b0a3b"}'
        response = session.post(start_url, data=formdata % state, headers=headers)
        data = json.loads(response.text)
        all_locations += data["locations"]
        if data["total_items"] > 10:
            total_pages = data["total_items"] // 10 + 2
            for page in range(1, total_pages):
                formdata = (
                    '{"search_radius":1000,"query":"%s","page":%s,"config_id":"0478a911-df76-40e0-a4a2-a6ee564b0a3b"}'
                    % (state, str(page))
                )
                response = session.post(start_url, data=formdata, headers=headers)
                data = json.loads(response.text)
                all_locations += data["locations"]

    for poi in all_locations:
        poi_url = poi["service"]["Website"]["location"]["websiteUrl"]
        poi_name = poi["custName"]
        poi_name = poi_name if poi_name else "<MISSING>"
        street = poi["addr"]["Main"]["street1"]
        if poi["addr"]["Main"]["street2"]:
            street += ", " + poi["addr"]["Main"]["street2"]
        street = street if street else "<MISSING>"
        city = poi["addr"]["Main"]["city"]
        city = city if city else "<MISSING>"
        state = poi["addr"]["Main"]["state"]
        zip_code = poi["addr"]["Main"]["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["addr"]["Main"]["country"]
        country_code = country_code if country_code else "<MISSING>"
        poi_number = "<MISSING>"
        phone = poi["phone"]
        poi_type = "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hoo = []
        days = {
            "1": "Monday",
            "2": "Tuesday",
            "3": "Wednesday",
            "4": "Thursday",
            "5": "Friday",
            "6": "Saturday",
            "7": "Sunday",
        }
        for elem in poi["hours"]:
            day = days[str(elem["day"])]
            opens = str(elem["startHH"])
            if elem["startMM"] != 0:
                opens += ":" + str(elem["startMM"])
            closes = str(elem["endHH"])
            if elem["endMM"] != 0:
                opens += ":" + str(elem["endMM"])
            hoo.append(f"{day} {opens} - {closes}")
        hoo = " ".join(hoo) if hoo else "<MISSING>"

        item = [
            DOMAIN,
            poi_url,
            poi_name,
            street,
            city,
            state,
            zip_code,
            country_code,
            poi_number,
            phone,
            poi_type,
            latitude,
            longitude,
            hoo,
        ]

        check = f"{poi_name} {street}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
