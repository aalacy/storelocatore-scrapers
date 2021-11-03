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
    url = "https://www.zinburgeraz.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.select('a:contains("View Details")')
    p = 0
    for div in divlist:
        link = div["href"]
        r = session.get(link, headers=headers, verify=False)
        content = r.text.split('<script type="application/ld+json">', 1)[1].split(
            "</script", 1
        )[0]
        content = json.loads(content)
        lat = content["geo"]["latitude"]
        longt = content["geo"]["longitude"]
        try:
            phone = content["telephone"]
        except:
            phone = "<MISSING>"
        state = content["address"]["addressRegion"]
        pcode = content["address"]["postalCode"]
        ccode = content["address"]["addressCountry"]
        street = content["address"]["streetAddress"]
        city = content["address"]["addressLocality"]
        title = "ZINBURGER IN " + city.upper()
        try:
            hourlist = content["openingHoursSpecification"]
            hours = ""
            for hr in hourlist:
                day = hr["dayOfWeek"].split("/")[-1]
                openstr = (
                    hr["opens"].split(":")[0] + ":" + hr["opens"].split(":")[1] + " AM "
                )
                closestr = (int)(hr["closes"].split(":")[0])
                if closestr > 12:
                    closestr = closestr - 12
                hours = (
                    hours
                    + day
                    + " "
                    + openstr
                    + " - "
                    + str(closestr)
                    + ":"
                    + hr["closes"].split(":")[1]
                    + " PM "
                )
        except:
            hours = "<MISSING>"
        data.append(
            [
                "https://www.zinburgeraz.com",
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
