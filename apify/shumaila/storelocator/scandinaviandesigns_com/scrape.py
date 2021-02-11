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
    url = "https://stores.scandinaviandesigns.com/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.select("a[href*=stores]")
    p = 0
    for link in linklist:
        title = link.text
        if "Find" in title or "VIEW" in title:
            continue
        link = link["href"]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("h2").text
        loc = r.text.split('<script type="application/ld+json">', 1)[1].split(
            "</script>", 1
        )[0]
        loc = json.loads(loc)
        street = loc["address"]["streetAddress"]
        city = loc["address"]["addressLocality"]
        state = loc["address"]["addressRegion"]
        pcode = loc["address"]["postalCode"]
        lat = loc["geo"]["latitude"]
        longt = loc["geo"]["longitude"]
        try:
            phone = loc["telephone"].replace("+1", "")
            phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:10]
        except:
            phone = "<MISSING>"
        try:
            hourslist = loc["openingHoursSpecification"]
            hours = ""
            for hr in hourslist:
                day = hr["dayOfWeek"]
                openstr = hr["opens"] + " AM - "
                closestr = hr["closes"]
                close = (int)(closestr.split(":")[0])
                if close > 12:
                    close = close - 12
                hours = (
                    hours
                    + day
                    + " "
                    + openstr
                    + str(close)
                    + ":"
                    + closestr.split(":")[1]
                    + " PM "
                )
        except:
            hours = "<MISSING>"
        data.append(
            [
                "https://scandinaviandesigns.com/",
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
