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
    url = "https://blackfinnameripub.com/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.select('a:contains("Vist Location")')
    for div in divlist:
        divlink = div["href"]
        if "blackfinndc.com" in divlink:
            divlink = divlink + "/locations"
        r = session.get(divlink, headers=headers, verify=False)
        try:
            loclist = r.text.split("locations:", 1)[1].split("apiKey")[0]
            loclist = loclist.replace("\n", "").replace("}}],", "}}]")
            loclist = json.loads(loclist)
            for loc in loclist:
                title = loc["name"]
                link = "https://blackfinndc.com" + loc["url"]
                phone = loc["phone_number"]
                lat = loc["lat"]
                longt = loc["lng"]
                street = loc["street"]
                city = loc["city"]
                state = loc["state"]
                pcode = loc["postal_code"]
                hours = loc["hours"]
                hours = (
                    BeautifulSoup(str(hours), "html.parser")
                    .text.replace("pm", "pm ")
                    .replace("day", "day ")
                    .strip()
                )
                data.append(
                    [
                        "https://blackfinnameripub.com/",
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
                        hours.replace("am", " am ").replace("pm", " pm ").strip(),
                    ]
                )

                p += 1
        except:
            loc = r.text.split('<script type="application/ld+json">', 1)[1].split(
                "</script>", 1
            )[0]
            loc = json.loads(loc)
            title = loc["name"]
            street = loc["subOrganization"]["address"]["streetAddress"]
            city = loc["subOrganization"]["address"]["addressLocality"]
            state = loc["subOrganization"]["address"]["addressRegion"]
            pcode = loc["subOrganization"]["address"]["postalCode"]
            phone = loc["subOrganization"]["telephone"]
            link = loc["subOrganization"]["hasMap"]
            lat = longt = hours = "<MISSING>"
            data.append(
                [
                    "https://blackfinnameripub.com/",
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
                    "<MISSING>",
                    "<MISSING>",
                    "<MISSING>",
                ]
            )

            p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
