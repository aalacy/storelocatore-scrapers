import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
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
    p = 0
    data = []
    url = "https://shop.sprouts.com/api/v2/stores"
    loclist = session.get(url, headers=headers, verify=False).json()["items"]
    for loc in loclist:
        street = loc["address"]["address1"]
        if str(loc["address"]["address2"]) != "None":
            street = street + " " + str(loc["address"]["address2"])
        city = loc["address"]["city"]
        pcode = loc["address"]["postal_code"]
        state = loc["address"]["province"]
        link = loc["external_url"]
        phone = loc["phone_number"]
        store = loc["id"]
        title = loc["name"]
        lat = loc["location"]["latitude"]
        longt = loc["location"]["longitude"]
        r = session.get(link, headers=headers, verify=False)
        hours = r.text.split('"openingHours":"', 1)[1].split('"', 1)[0]

        data.append(
            [
                "https://www.sprouts.com/",
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
