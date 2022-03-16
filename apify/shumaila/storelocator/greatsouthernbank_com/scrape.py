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
    url = "https://www.greatsouthernbank.com/_/api/branches/37.2075589/-93.2605231/500"
    locations = session.get(url, headers=headers, verify=False).json()["branches"]
    for loc in locations:
        title = loc["name"]
        store = "<MISSING>"
        lat = loc["lat"]
        longt = loc["long"]
        street = loc["address"]
        city = loc["city"]
        state = loc["state"]
        pcode = loc["zip"]
        phone = loc["phone"]
        detail = loc["description"]
        detail = BeautifulSoup(detail, "html.parser")
        try:
            link = detail.find("a")["href"]
            if "-84ead507913b" in link:
                street = street + " Suite 150"
            r = session.get(link, headers=headers, verify=False)
            store = r.text.split('"@id":"', 1)[1].split('"', 1)[0]
            soup = BeautifulSoup(r.text, "html.parser")
            hourd = soup.find("table", {"class": "hours"})
            hourd = hourd.findAll("tr")

            hours = ""
            for hr in hourd:
                hours = hours + hr.text + " "
            if len(hours) < 3:
                hours = "<MISSING>"
            else:
                hours = hours.replace("Day of the WeekHours", "").replace("day", "day ")
        except:

            link = "<MISSING>"
            try:
                hours = detail.find("li").text
            except:
                hours = "<MISSING>"
        if len(phone) < 3:
            phone = "<MISSING>"
        data.append(
            [
                "https://greatsouthernbank.com",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                store,
                phone,
                "Branch",
                lat,
                longt,
                hours.strip(),
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
