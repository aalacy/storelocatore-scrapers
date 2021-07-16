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

    data = []
    url = "https://api.storerocket.io/api/user/3MZpoQ2JDN/locations?radius=250&units=miles"
    p = 0
    loclist = session.get(url, headers=headers, verify=False).json()["results"][
        "locations"
    ]
    for loc in loclist:
        title = loc["name"]
        store = loc["id"]
        lat = loc["lat"]
        longt = loc["lng"]
        street = loc["address_line_1"]
        city = loc["city"]
        state = loc["state"]
        pcode = loc["postcode"]
        ccode = "US"
        if str(street) == "None":
            street, city, state, pcode = loc["address"].split(", ")
        phone = (
            loc["phone"]
            .replace("(", "")
            .replace(")", "")
            .replace("-", "")
            .replace(" ", "")
        )
        phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:10]
        if "Indiana" in state:
            state = "IN"
        elif "Illinois" in state:
            state = "IL"
        data.append(
            [
                "https://theoriginalpizzaking.com/",
                "https://theoriginalpizzaking.com/additional-pizza-king-locations/?location=Y287W2qN8A",
                title,
                street,
                city,
                state,
                pcode,
                ccode,
                store,
                phone,
                "<MISSING>",
                lat,
                longt,
                "<MISSING>",
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
