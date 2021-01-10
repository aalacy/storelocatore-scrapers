from bs4 import BeautifulSoup
import csv
import usaddress
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
    p = 0
    data = []
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "https://wokcanorestaurant.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.find("div", {"class": "et_pb_post_content_0_tb_body"}).findAll(
        "div", {"class": "et_pb_text_inner"}
    )
    for div in divlist:
        if "Online Ordering" in div.text:
            continue
        content = re.sub(pattern, "\n", div.text).strip()
        title = content.split("\n", 1)[0]
        address = (
            content.split("Address", 1)[1].split("\n", 1)[0].replace(":", "").strip()
        )
        phone = content.split("Phone", 1)[1].split("\n", 1)[0].replace(":", "").strip()
        try:
            hours = content.split("Hours", 1)[1].split("\n", 1)[0]
        except:
            try:
                hours = content.split("Hrs", 1)[1].split("\n", 1)[1].split("\n", 1)[0]
            except:
                if "Temporarily Closed" in div.text:
                    hours = "Temporarily Closed"
        try:
            hours = hours.split(":", 1)[1]
        except:
            pass
        address = usaddress.parse(address)

        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while i < len(address):
            temp = address[i]
            if (
                temp[1].find("Address") != -1
                or temp[1].find("Street") != -1
                or temp[1].find("Occupancy") != -1
                or temp[1].find("Recipient") != -1
                or temp[1].find("BuildingName") != -1
                or temp[1].find("USPSBoxType") != -1
                or temp[1].find("USPSBoxID") != -1
            ):
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            i += 1
        street = street.lstrip().replace(",", "")
        city = city.lstrip().replace(",", "")
        state = state.lstrip().replace(",", "")
        pcode = pcode.lstrip().replace(",", "")

        data.append(
            [
                "https://wokcanorestaurant.com/",
                "https://wokcanorestaurant.com/locations/",
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone,
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                hours.replace("pm", "pm ").replace("am", "am ").strip(),
            ]
        )
        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
