import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}


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
    data = []
    url = "https://www.gcrtires.com/content/bcs-sites/gcr/en/locations/_jcr_content.storelist.json"
    p = 0
    loclist = session.get(url, headers=headers, verify=False).json()["storeList"]
    for loc in loclist:
        pcode = loc["zip"]
        street = loc["address"]
        phone = loc["phone"]
        store = loc["storenumber"]
        title = "GCR Tires & Service #" + str(store)
        city = loc["location"]
        state = loc["state"]
        lat = loc["latitude"]
        longt = loc["longitude"]
        hours = (
            "Sunday "
            + loc["sundayhours"]
            + " Saturday "
            + loc["saturdayhours"]
            + " Weekdays "
            + loc["weekdayhours"]
            + " "
        )
        link = "https://www.gcrtires.com/locations/" + str(store)
        data.append(
            [
                "https://www.gcrtires.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                store,
                phone,
                "<MISSING>",
                lat,
                longt,
                hours,
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
