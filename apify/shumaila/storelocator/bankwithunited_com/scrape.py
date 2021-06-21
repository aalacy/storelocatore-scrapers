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
    data = []
    url = "https://www.bankwithunited.com/find-a-location"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    branchlist = soup.findAll("div", {"class": "location-content"})
    divlist = soup.findAll("div", {"class": "views-col"})
    geolist = soup.findAll("div", {"class": "geolocation-location"})

    p = 0

    for i in range(0, len(branchlist)):
        title = (
            branchlist[i]
            .find("div", {"class": "views-field-field-branch-name"})
            .text.strip()
        )
        street = (
            branchlist[i]
            .find("div", {"class": "views-field-field-address-address-line1"})
            .text.strip()
        )

        city = (
            branchlist[i]
            .find("span", {"class": "views-field views-field-field-address-locality"})
            .text.strip()
        )
        state = (
            branchlist[i]
            .find("span", {"class": "views-field-field-address-administrative-area"})
            .text.strip()
        )
        pcode = (
            branchlist[i]
            .find("span", {"class": "views-field-field-address-postal-code"})
            .text.strip()
        )
        phone = (
            branchlist[i]
            .find("div", {"class": "views-field-field-phone-number"})
            .text.strip()
        )
        if "ATM" in title or phone == "":
            ltype = "ATM"
            phone = "<MISSING>"
        else:
            ltype = "Branch"
        hours = "<MISSING>"
        try:
            lat = geolist[i + 1]["data-lat"]
            longt = geolist[i + 1]["data-lng"]
        except:
            lat = longt = "<MISSING>"
        for div in divlist:
            street1 = div.find(
                "div", {"class": "views-field-field-address-address-line1"}
            ).text.strip()
            if street1 == street:
                ltype = div.find(
                    "div", {"class": "views-field-field-amenities"}
                ).text.strip()
                hours = (
                    div.find(
                        "div", {"class": "views-field-field-location-service-hours"}
                    )
                    .text.replace("\n", " ")
                    .strip()
                )
                try:
                    title = (
                        div.find("div", {"class": "views-field-title"}).text.strip()
                        + " - "
                        + title
                    )
                except:
                    pass
        data.append(
            [
                "https://www.bankwithunited.com/",
                "https://www.bankwithunited.com/find-a-location",
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone,
                ltype,
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
