from bs4 import BeautifulSoup
import csv
import json
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
    url = "https://fitnesstogether.com/personal-trainers-near-me"
    p = 0
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("li", {"class": "list-title"})
    for div in divlist:
        search = div.text
        gurl = (
            "https://maps.googleapis.com/maps/api/geocode/json?address="
            + search
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
            "https://fitnesstogether.com/locator?q="
            + search
            + "%2C%20United%20States&lat="
            + str(latnow)
            + "&lng="
            + str(lngnow)
        )

        if "Columbia" in search:
            url = "https://fitnesstogether.com/locator?q=District%20of%20Columbia%2C%20United%20States&lat=38.895&lng=-77.03667&limit=5"
        loclist = session.get(url, headers=headers, verify=False).json()["locations"]

        for loc in loclist:

            if loc["status"] == "soon":
                continue
            title = loc["name"]
            store = loc["id"]
            link = "https://fitnesstogether.com/" + loc["slug"]
            street = loc["address"] + " " + loc["address_2"]
            city = loc["city"]
            state = loc["state"]
            pcode = loc["zip_code"]
            phone = loc["phone_number"]
            if len(phone) < 3:
                phone = "<MISSING>"
            lat = loc["latitude"]
            longt = loc["longitude"]
            hourslist = json.loads(loc["business_hours"])
            hours = ""
            for hr in hourslist:
                day = hr
                hr = hourslist[day]
                start = ":".join(hr["start"].split(":")[0:2])
                end = hr["end"].split(":")[0:2]
                endtime = (int)(end[0])
                if endtime > 12:
                    endtime = endtime - 12
                hours = (
                    hours
                    + day
                    + " "
                    + start
                    + " AM - "
                    + str(endtime)
                    + ":"
                    + end[1]
                    + " PM "
                )
            data.append(
                [
                    "https://fitnesstogether.com/",
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
