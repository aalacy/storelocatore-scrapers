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
    url = "https://oilchangers.ca/wp-admin/admin-ajax.php?action=locations_request&tire-rotations=false&tire-change=false"
    p = 0
    loclist = session.get(url, headers=headers, verify=False).json()
    week = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    for loc in loclist:
        title = loc["title"]
        store = loc["post_id"]
        lat = loc["location_latitude"][0]
        longt = loc["location_longitude"][0]
        street = loc["street_address"][0]
        city = loc["location_city"][0]
        state = loc["location_province"][0]
        pcode = loc["location_postal_code"][0]
        link = "https://oilchangers.ca" + loc["permalink"]
        ccode = "CA"
        phone = loc["phone_number"][0]
        hours = ""
        for day in week:
            try:
                openstr = "hours_of_operation_" + day.lower() + "_opening_hour"
                opens = loc[openstr][0].split(":")[0]
                closestr = "hours_of_operation_" + day.lower() + "_closing_hour"
                closes = (int)(loc[closestr][0].split(":")[0])
                if closes > 12:
                    closes = closes - 12
                hours = (
                    hours
                    + day
                    + " "
                    + opens
                    + ":"
                    + loc[openstr][0].split(":")[1]
                    + " AM - "
                    + str(closes)
                    + ":"
                    + loc[closestr][0].split(":")[1]
                    + " PM "
                )
            except:
                hours = hours + day + " Closed "
        if title.find("Coming Soon") == -1:
            data.append(
                [
                    "https://oilchangers.ca/",
                    link,
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
                    hours,
                ]
            )

            p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
