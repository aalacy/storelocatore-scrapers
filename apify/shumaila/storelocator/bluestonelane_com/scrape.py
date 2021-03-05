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
    url = "https://bluestonelane.com/cafe-and-coffee-shop-locations/?shop-sort=nearest&view-all=1&lat=&lng="
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("a", {"class": "homebox-address"})
    linklist = []
    p = 0
    for div in divlist:
        link = div["href"]
        if link in linklist:
            continue
        linklist.append(link)
        r = session.get(link, headers=headers, verify=False)
        ccode = "US"
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("h1").text.strip()
        street = soup.find("span", {"id": "yext-address"})
        try:
            store = street["data-yext-location-id"]
        except:
            store = "<MISSING>"
            continue
        url = (
            "https://knowledgetags.yextpages.net/embed?key=6Af24AhHWVK9u_N4dzlSiNnLaAoxr-dpa-xe7Zf76O9rU3Eb4m0xxX6-7A_CxoZF&account_id=6868880511088594204&location_id="
            + store
        )

        r = session.get(url, headers=headers, verify=False)
        address = r.text.split('"address":{', 1)[1].split("},", 1)[0]
        address = "{" + address + "}"
        address = json.loads(address)
        street = address["streetAddress"]
        city = address["addressLocality"]
        state = address["addressRegion"]
        pcode = address["postalCode"]
        geo = r.text.split('"geo":', 1)[1].split("},", 1)[0]
        geo = geo + "}"
        geo = json.loads(geo)
        lat = geo["latitude"]
        longt = geo["longitude"]
        try:
            hourslist = r.text.split('"openingHoursSpecification":', 1)[1].split(
                "}],", 1
            )[0]
            hourslist = hourslist + "}]"
            hourslist = json.loads(hourslist)
            hours = ""
            for hr in hourslist:
                day = hr["dayOfWeek"]
                opens = hr["opens"]
                closes = hr["closes"]
                cltime = (int)(closes.split(":", 1)[0])
                if cltime > 12:
                    cltime = cltime - 12
                hours = (
                    hours
                    + day
                    + " "
                    + opens
                    + " AM - "
                    + str(cltime)
                    + ":"
                    + closes.split(":", 1)[1]
                    + " PM "
                )
        except:
            hours = "<MISSING>"
        phone = r.text.split('"telephone":"', 1)[1].split('"', 1)[0].replace("+1", "")
        phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:10]
        ccode = "US"
        if "-" in pcode:
            continue
        if pcode.isdigit():
            pass
        else:
            ccode = "CA"
        data.append(
            [
                "https://bluestonelane.com/",
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
