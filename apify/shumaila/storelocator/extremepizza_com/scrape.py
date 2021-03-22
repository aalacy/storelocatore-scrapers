from bs4 import BeautifulSoup
import csv
import json
import re
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
    url = "https://www.extremepizza.com/store-locator/"
    p = 0
    cleanr = re.compile(r"<[^>]+>")
    r = session.get(url, headers=headers, verify=False)
    loclist = r.text.split('{"@type": "FoodEstablishment", ')
    loclist = r.text.split('"hours"')[1:]
    for loc in loclist:
        try:
            link = loc.split('"url": "', 1)[1].split(",", 1)[0]
        except:
            break
        link = "https://www.extremepizza.com" + link.replace('"', "")
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        address = r.text.split('"location": ', 1)[1].split("}", 1)[0]
        address = soup.find("section", {"id": "intro"}).findAll("a")[0].text.strip()
        try:
            phone = soup.find("section", {"id": "intro"}).findAll("a")[1].text
        except:
            if (
                "Coming Soon!" in soup.find("section", {"id": "intro"}).text
                or "soon!" in soup.find("section", {"id": "intro"}).text
            ):
                continue
            else:
                phone = "<MISSING>"
        hourlist = soup.find("section", {"id": "intro"}).findAll("p")
        hours = ""
        for hr in hourlist:
            if (
                "AM" in hr.text
                or "day" in hr.text
                or "am -" in hr.text
                or "pm -" in hr.text
            ):
                hrnow = re.sub(cleanr, " ", str(hr)).strip()
                hours = hours + hrnow + " "
        address = address.split(", ")
        state = address[-1]
        city = address[-2]
        street = " ".join(address[0:-2])
        state, pcode = state.strip().split(" ", 1)
        title = soup.find("title").text.split(" |", 1)[0]
        lat = r.text.split('data-gmaps-lat="', 1)[1].split('"', 1)[0]
        longt = r.text.split('data-gmaps-lng="', 1)[1].split('"', 1)[0]
        if len(hours) < 3:
            hours = "<MISSING>"
        else:
            hours = hours.replace("&amp;", "&").replace(".", "")
        try:
            hours = hours.split("Try", 1)[0]
        except:
            pass
        try:
            hours = hours.split("Thirst", 1)[0]
        except:
            pass
        try:
            hours = hours.split("We", 1)[0]
        except:
            pass
        if "Order Online" in phone:
            phone = "<MISSING>"
        data.append(
            [
                "https://www.extremepizza.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone,
                "<MISSING>",
                lat,
                longt.replace("\n", "").strip(),
                hours.strip(),
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
