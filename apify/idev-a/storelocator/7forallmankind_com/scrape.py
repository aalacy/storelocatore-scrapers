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
    base_url = "https://www.7forallmankind.com/"

    res = session.get(
        "https://www.7forallmankind.com/storelocator/index/ajax/?_=1611046887442"
    )
    store_list = json.loads(res.text)
    data = []
    for store in store_list:
        page_url = store["store_url"]
        location_name = store["storename"]
        street_address = ", ".join(store["address"])
        state = "<MISSING>" if store["region"] is None else store["region"]
        city = store["city"]
        country_code = store["country_id"]
        store_number = store["storelocator_id"]
        location_type = "<MISSING>"
        latitude = store["latitude"]
        longitude = store["longitude"]
        zip = store["zipcode"]
        phone = store["telephone"]
        try:
            hours = json.loads(store["storetime"])
        except:
            tmp = store["storetime"].split('"')[1::2]
            hours = []
            hour = {}
            idx = 0
            while idx < len(tmp):
                if idx % 14 == 0 and idx > 0:
                    hours.append(hour)
                    hour = {}
                hour[tmp[idx]] = tmp[idx + 1]
                idx += 2
            hours.append(hour)
        hours_of_operation = ""
        for hour in hours:
            hours_of_operation += (
                hour["days"]
                + ": "
                + hour["open_hour"]
                + ":"
                + hour["open_minute"]
                + "-"
                + hour["close_hour"]
                + ":"
                + hour["close_minute"]
                + ""
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
                '="' + phone + '"',
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
