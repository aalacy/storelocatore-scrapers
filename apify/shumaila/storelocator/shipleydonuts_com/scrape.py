from bs4 import BeautifulSoup
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
    streetlist = []
    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
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
        url = (
            "https://shipleydonuts.com/wp-admin/admin-ajax.php?action=store_search&lat="
            + str(latnow)
            + "&lng="
            + str(lngnow)
            + "&max_results=100&search_radius=500"
        )
        loclist = session.get(url, headers=headers, verify=False).json()
        if len(loclist) == 0:
            continue
        for loc in loclist:
            title = loc["store"]
            street = loc["address"] + " " + loc["address2"]
            street = street.strip()
            city = loc["city"]
            state = loc["state"]
            pcode = loc["zip"]
            phone = loc["phone"]
            lat = loc["lat"]
            longt = loc["lng"]
            link = loc["permalink"]
            try:
                hours = (
                    BeautifulSoup(loc["hours"], "html.parser")
                    .text.replace("day", "day ")
                    .replace("PM", "PM ")
                )
            except:
                hours = "<MISSING>"
            store = str(loc["id"])
            if store in streetlist:
                continue
            streetlist.append(store)

            data.append(
                [
                    "https://shipleydonuts.com/",
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
