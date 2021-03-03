import csv
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
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
    ids = []
    urls = [
        "https://www.lids.com/api/data/v2/stores/514599?lat=40&long=-80&num=1000&shipToStore=false",
        "https://www.lids.com/api/data/v2/stores/514599?lat=35&long=-95&num=1000&shipToStore=false",
        "https://www.lids.com/api/data/v2/stores/514599?lat=40&long=-105&num=1000&shipToStore=false",
        "https://www.lids.com/api/data/v2/stores/514599?lat=45&long=-115&num=1000&shipToStore=false",
        "https://www.lids.com/api/data/v2/stores/514599?lat=35&long=-120&num=1000&shipToStore=false",
    ]
    for url in urls:
        r = session.get(url, headers=headers)
        for item in json.loads(r.content):
            store = item["storeId"]
            name = item["name"]
            add = item["address"]["addressLine1"]
            city = item["address"]["city"]
            state = item["address"]["state"]
            country = item["address"]["country"]
            try:
                phone = item["phone"]
            except:
                phone = "<MISSING>"
            zc = item["address"]["zip"]
            lat = item["location"]["coordinate"]["latitude"]
            lng = item["location"]["coordinate"]["longitude"]
            typ = item["location"]["description"]
            hours = "Sun: " + item["sundayOpen"] + "-" + item["sundayClose"]
            hours = hours + "; Mon: " + item["mondayOpen"] + "-" + item["mondayClose"]
            hours = hours + "; Tue: " + item["tuesdayOpen"] + "-" + item["tuesdayClose"]
            hours = (
                hours + "; Wed: " + item["wednesdayOpen"] + "-" + item["wednesdayClose"]
            )
            hours = (
                hours + "; Thu: " + item["thursdayOpen"] + "-" + item["thursdayClose"]
            )
            hours = hours + "; Fri: " + item["fridayOpen"] + "-" + item["fridayClose"]
            hours = (
                hours + "; Sat: " + item["saturdayOpen"] + "-" + item["saturdayClose"]
            )
            website = "lids.com"
            if "San Jos" in city:
                city = "San Jose"
            if "170 O" in add:
                add = "170 OFarrell St"
            loc = "https://lids.com" + item["taggedUrl"]
            if country == "US":
                if phone == "":
                    phone = "<MISSING>"
                if store not in ids:
                    ids.append(store)
                    yield [
                        website,
                        loc,
                        name,
                        add,
                        city,
                        state,
                        zc,
                        country,
                        store,
                        phone,
                        typ,
                        lat,
                        lng,
                        hours,
                    ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
