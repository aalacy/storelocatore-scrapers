import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}
headers = {
    "Request-Id": "|HTTDs.jfJ5R",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
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
            "https://locations.alliedcash.com/service/location/getlocationsnear?latitude="
            + str(latnow)
            + "&longitude="
            + str(lngnow)
            + "&radius=1000&brandFilter=Allied%20Cash"
        )
        loclist = session.get(url, headers=headers, verify=False).json()
        for loc in loclist:
            title = loc["ColloquialName"]
            street = loc["Address1"] + " " + str(loc["Address2"])
            city = loc["City"]
            state = loc["StateCode"]
            pcode = loc["ZipCode"]
            phone = loc["FormattedPhone"]
            lat = loc["Latitude"]
            longt = loc["Longitude"]
            store = loc["StoreNum"]
            if street in streetlist:
                continue
            streetlist.append(street)
            link = "https://locations.alliedcash.com/locations" + loc["Url"]
            hours = (
                "Monday "
                + str(loc["MondayOpen"])
                + "-"
                + str(loc["MondayClose"])
                + " Tuesday "
                + str(loc["TuesdayOpen"])
                + "-"
                + str(loc["TuesdayClose"])
                + " Wednesday "
                + str(loc["WednesdayOpen"])
                + "-"
                + str(loc["WednesdayClose"])
                + " Thursday "
                + str(loc["ThursdayOpen"])
                + "-"
                + str(loc["ThursdayClose"])
                + " Friday "
                + str(loc["FridayOpen"])
                + "-"
                + str(loc["FridayClose"])
            )
            data.append(
                [
                    "https://www.alliedcash.com/",
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
