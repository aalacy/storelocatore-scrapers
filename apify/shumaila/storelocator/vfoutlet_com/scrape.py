from bs4 import BeautifulSoup
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
    p = 0
    titlelist = []
    states = [
        "Alabama",
        "Alaska",
        "Arizona",
        "Arkansas",
        "California",
        "Colorado",
        "Connecticut",
        "DC",
        "Delaware",
        "Florida",
        "Georgia",
        "Hawaii",
        "Idaho",
        "Illinois",
        "Indiana",
        "Iowa",
        "Kansas",
        "Kentucky",
        "Louisiana",
        "Maine",
        "Maryland",
        "Massachusetts",
        "Michigan",
        "Minnesota",
        "Mississippi",
        "Missouri",
        "Montana",
        "Nebraska",
        "Nevada",
        "New Hampshire",
        "New Jersey",
        "New Mexico",
        "New York",
        "North Carolina",
        "North Dakota",
        "Ohio",
        "Oklahoma",
        "Oregon",
        "Pennsylvania",
        "Rhode Island",
        "South Carolina",
        "South Dakota",
        "Tennessee",
        "Texas",
        "Utah",
        "Vermont",
        "Virginia",
        "Washington",
        "West Virginia",
        "Wisconsin",
        "Wyoming",
    ]
    for statenow in states:
        gurl = (
            "https://maps.googleapis.com/maps/api/geocode/json?address="
            + statenow
            + "&key=AIzaSyCT4uvUVAv4U6-Lgeg94CIuxUg-iM2aA4s&components=country%3AUS"
        )
        r = session.get(gurl, headers=headers, verify=False).json()
        if r["status"] == "REQUEST_DENIED":
            pass
        else:
            coord = r["results"][0]["geometry"]["location"]
            latnow = coord["lat"]
            lngnow = coord["lng"]
        myobj = {
            "radius": "2367339.1399999997",
            "latitude": latnow,
            "longitude": lngnow,
        }
        url = "https://vfoutlet.com/index.php/storelocator/index/loadstore/"
        loclist = session.post(url, headers=headers, verify=False, data=myobj).json()[
            "storesjson"
        ]
        for loc in loclist:
            store = loc["storelocator_id"]
            title = loc["store_name"]
            street = loc["address"] + " " + loc["address_2"]
            lat = loc["latitude"]
            longt = loc["longitude"]
            link = "https://vfoutlet.com/index.php/" + loc["rewrite_request_path"]
            phone = loc["phone"]
            r = session.get(link, headers=headers, verify=False)
            soup = BeautifulSoup(r.text, "html.parser")
            hours = soup.find("table", {"class": "table"}).text
            content = soup.find("div", {"class": "box-detail"}).text
            city = content.split("City:", 1)[1].split("\n", 1)[1].split("\n", 1)[0]
            state = content.split("State:", 1)[1].split("\n", 1)[1].split("\n", 1)[0]
            if link in titlelist:
                continue
            titlelist.append(link)
            data.append(
                [
                    "https://vfoutlet.com/",
                    link,
                    title,
                    street,
                    city,
                    state.replace("Washington", "WA").replace("Wisconsin", "WI"),
                    "<MISSING>",
                    "US",
                    store,
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    hours.replace("\n", " ").strip(),
                ]
            )
            p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
