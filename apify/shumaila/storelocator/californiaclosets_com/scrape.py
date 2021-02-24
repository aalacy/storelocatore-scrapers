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
    p = 0
    data = []
    url = "https://www.californiaclosets.com/showrooms/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.select('a:contains("Showroom details")')
    titlelist = []
    for link in linklist:
        link = link["href"]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            content = r.text.split('<script type="application/ld+json">')[1].split(
                "</script>"
            )[0]
            content = json.loads(content)
            street = content["address"]["streetAddress"]
            pcode = content["address"]["postalCode"]
            state = content["address"]["addressRegion"]
            city = content["address"]["addressLocality"]
            phone = content["telephone"]
            try:
                lat = content["geo"]["latitude"]
                longt = content["geo"]["longitude"]
            except:
                try:
                    lat, longt = (
                        r.text.split('"https://www.google.com/maps/place/', 1)[1]
                        .split('"')[0]
                        .split(",")
                    )
                except:
                    lat = longt = "<MISSING>"
            title = content["name"]
            try:
                ccode = content["address"]["addressCountry"]
            except:
                if pcode.strip().isdigit:
                    ccode = "US"
                else:
                    ccode = "CA"
            try:
                hourslist = content["openingHoursSpecification"]
                hours = ""
                for hr in hourslist:
                    day = hr["dayOfWeek"]
                    try:
                        opens = hr["opens"] + " AM - "

                        close = hr["closes"]
                        cttime = (int)(close.split(":", 1)[0])
                        if cttime > 12:
                            cttime = cttime - 12
                        hours = (
                            hours
                            + day
                            + " "
                            + opens
                            + str(cttime)
                            + ":"
                            + close.split(":", 1)[1]
                            + " PM "
                        )
                    except:
                        hours = hours + day + " Closed "
            except:
                hours = "<MISSING>"
        except:
            try:
                address = (
                    soup.find("div", {"class": "address-nav"})
                    .text.lstrip()
                    .splitlines()
                )
            except:
                continue
            street = address[1]
            city, state = address[2].split(", ")
            pcode = address[3]
            phone = address[5]
            hours = (
                soup.findAll("div", {"class": "address-nav"})[1]
                .text.split("Make", 1)[0]
                .replace("Working Hours", "")
                .replace("\n", " ")
                .strip()
            )
            ccode = "CA"

            title = soup.find("title").text.split("-")[0]
            try:
                lat, longt = (
                    r.text.split('"https://www.google.com/maps/place/', 1)[1]
                    .split('"')[0]
                    .split(",")
                )
            except:

                continue
        if hours.find("call") > -1:
            hours = "<MISSING>"
        if len(pcode) < 2:
            pcode = "<MISSING>"
        if state == "Washington":
            state = "WA"
        if state == "Wisconsin":
            state = "WI"
        if state == "Boise" and city == "Idaho":
            state = "ID"
            city = "Boise"
        if len(state) > 3 or street in titlelist:
            continue
        titlelist.append(street)
        data.append(
            [
                "https://www.californiaclosets.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                ccode,
                "<MISSING>",
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
