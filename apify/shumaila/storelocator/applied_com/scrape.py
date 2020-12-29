from bs4 import BeautifulSoup
import csv
import re
import json

from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}
headerss = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": "_hjid=af658011-d907-43c0-9120-aa8730bd428b; CookieConsent={stamp:%27yNDrfc8QZwUwKbwjE4cYxwrNU5rtLi7p2VfewAmpccyGEobEd8IYsQ==%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cver:3%2Cutc:1607876507873%2Cregion:%27us%27}; hubspotutk=1409c31ac03a43bc48d2b78fbd121db1; __utmz=254702680.1607876516.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _fbp=fb.1.1607876538822.1694875894; accountSummaryViewMode=list; _cer.v=d6b9ab8349bd65a5e75f5ed1076fe3ee46f48be2.qlajkz.d; _hjIncludedInPageviewSample=1; _hjTLDTest=1; _CEFT=EgNwlgpg7hAmBcBzACgWgGoEMCCBNXAKugBwDQATgMYD6ArrgBoBGmAVgB64BAYsACBADSAJggB5MLgCeTAMKUAzACUADioCKQA%3D; __hssrc=1; __utmc=254702680; messagesUtk=15c2c13275b94e07990e6ea76e9db466; _ce.s=v11.rlc~1609240385918~v~d6b9ab8349bd65a5e75f5ed1076fe3ee46f48be2~vv~14~ir~1~v11nv~1; _hjAbsoluteSessionInProgress=0; __hstc=195597939.1409c31ac03a43bc48d2b78fbd121db1.1607876513713.1609239827392.1609246242634.8; __utma=254702680.562927595.1607876516.1609239829.1609246245.8; JSESSIONID=1C509014C66BCD20D373112F755E3DD8; __hssc=195597939.3.1609246242634; __utmt=1; __utmb=254702680.2.10.1609246245",
    "Host": "www.applied.com",
    "Origin": "https://www.applied.com",
    "Referer": "https://www.applied.com/store-finder/position",
    "Sec-Fetch-Dest": "document",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
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
        "Alberta",
        "British Columbia",
        "Manitoba",
        "New Brunswick",
        "Newfoundland",
        "Labrador",
        "Nova Scotia",
        "Ontario",
        "Prince Edward Island",
        "Quebec",
        "Saskatchewan",
    ]

    data = []
    streetlist = []
    pattern = re.compile(r"\s\s+")
    ccode = "US"
    for st in states:

        if st == "Alberta":
            ccode = "CA"
        gurl = (
            "https://maps.googleapis.com/maps/api/geocode/json?address="
            + st
            + "&key=AIzaSyCT4uvUVAv4U6-Lgeg94CIuxUg-iM2aA4s&components=country%3A"
            + ccode
        )
        r = session.get(gurl, headers=headers, verify=False).json()
        if r["status"] == "REQUEST_DENIED":
            pass
        else:
            coord = r["results"][0]["geometry"]["location"]
            latnow = coord["lat"]
            lngnow = coord["lng"]
        myobj = {
            "latitude": latnow,
            "longitude": lngnow,
            "CSRFToken": "921f28f7-3e9b-40a2-bd63-12adcc260799",
        }
        url = "https://www.applied.com/store-finder/position"
        r = session.post(url, headers=headerss, data=myobj, verify=False)

        soup = BeautifulSoup(r.text, "html.parser")

        try:
            storelist = soup.find("div", {"class": "store-result-list"}).findAll(
                "tr", {"class": "item"}
            )
        except:

            continue
        coordlist = r.text.split("data-stores= '{", 1)[1].split("}'", 1)[0].split("{")

        for div in storelist:
            tdlist = div.findAll("td")
            col1 = re.sub(pattern, "\n", tdlist[0].text).lstrip().splitlines()
            title = col1[0]
            store = col1[1].replace("(", "").replace(")", "").strip()
            phone = col1[2]
            address = re.sub(pattern, "\n", tdlist[2].text).lstrip().splitlines()
            link = "https://www.applied.com" + tdlist[0].find("a")["href"]
            street = address[0]
            try:
                city, state = address[1].split(", ", 1)
            except:
                if address[1].split(",", 1)[0] in link:
                    state = link.split(address[1].split(",", 1)[0] + ", ")[1].split(
                        " ", 1
                    )[0]
                    city = address[1].split(",", 1)[0]
            pcode = address[2]
            if title in streetlist:
                continue
            streetlist.append(title)
            lat = link.split("lat=", 1)[1].split("&", 1)[0]
            longt = link.split("long=", 1)[1]
            if "View Map" in phone:
                phone = "<MISSING>"
            lat = "<MISSING>"
            longt = "<MISSING>"
            for coord in coordlist:
                coord = coord.replace("\n", "").lstrip()
                try:
                    coord = "{" + coord.split("}", 1)[0] + "}"
                    coord = json.loads(coord)

                    if title.strip() == coord["name"]:
                        lat = coord["latitude"]
                        longt = coord["longitude"]
                        break
                except:
                    pass
            data.append(
                [
                    "https://www.applied.com/",
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
                    "<MISSING>",
                ]
            )

            p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
