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
    url = "https://www.extremepizza.com/store-locator/"
    p = 0
    r = session.get(url, headers=headers, verify=False)
    r = r.text.split('<script type="application/ld+json">')[1].split("</script")[0]
    loclist = json.loads(r)
    loclist = loclist["subOrganization"]
    for loc in loclist:
        flag = 0
        link = loc["url"]
        title = loc["name"]
        street = loc["address"]["streetAddress"]
        city = loc["address"]["addressLocality"]
        state = loc["address"]["addressRegion"]
        pcode = loc["address"]["postalCode"]
        ccode = "US"
        phone = loc["telephone"]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        ct = soup.find("section", {"id": "intro"}).findAll("p")
        hours = ""
        for t in ct:
            if (
                (("AM " in t.text and "PM" in t.text) or ("Closed on" in t.text))
                or ("Am" in t.text and (":" in t.text or "-" in t.text))
                or "Everyday" in t.text
                or ("pm" in t.text and (":" in t.text or "-" in t.text))
            ):
                hours = hours + t.text + " "
            elif "Soon" in t.text or "Opening" in t.text:
                flag = 1
                break
        if flag == 1:
            continue
        try:
            lat = r.text.split('"latitude":', 1)[1].split(",", 1)[0]
            longt = r.text.split('"longitude":', 1)[1].split("}", 1)[0]
        except:
            lat = r.text.split('data-gmaps-lat="', 1)[1].split('"', 1)[0]
            longt = r.text.split(' data-gmaps-lng="', 1)[1].split('"', 1)[0]
        if len(hours) < 3:
            hours = "<MISSING>"
        try:
            hours = hours.split("Delivery", 1)[0]
        except:
            pass
        try:
            if len(phone) < 3:
                phone = "<MISSING>"
        except:
            phone = "<MISSING>"
        hours = hours.replace("1", " 1").replace("1 1", "11").strip()
        data.append(
            [
                "https://www.extremepizza.com/",
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
