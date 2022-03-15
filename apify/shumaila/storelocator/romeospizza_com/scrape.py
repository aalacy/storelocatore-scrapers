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
    url = "https://www.romeospizza.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.findAll("div", {"class": "col-6"})
    for link in linklist:
        try:
            link = link.select_one('a:contains("More Info")')["href"]
            r = session.get(link, headers=headers, verify=False)
            soup = BeautifulSoup(r.text, "html.parser")
            loc = r.text.split('<script type="application/ld+json">', 1)[1].split(
                "</script>", 1
            )[0]
            loc = json.loads(loc)
            phone = loc["telephone"]
            phone = phone.replace("+1", "")
            phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:10]
            city = loc["address"]["addressLocality"]
            street = loc["address"]["streetAddress"]
            state = loc["address"]["addressRegion"]
            pcode = loc["address"]["postalCode"]
            lat = loc["geo"]["latitude"]
            longt = loc["geo"]["longitude"]
            hours = soup.find("table", {"class": "hours"}).text
            title = city
        except:
            continue
        data.append(
            [
                "https://romeospizza.com",
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
