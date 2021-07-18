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
    p = 0
    url = "https://www.landmarkcinemas.com/showtimes/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.select("a[href*=showtimes]")
    for link in linklist:

        title = link.text
        link = link["href"]
        if link == "/showtimes/":
            continue
        link = "https://www.landmarkcinemas.com" + link
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            hours = (
                soup.find("div", {"class": "cinenote"}).find("p").text.split(".", 1)[0]
            )
        except:
            hours = "<MISSING>"
        if "permanently CLOSED" in hours:
            continue
        if "In compliance" in hours or len(hours) < 3:
            hours = "<MISSING>"
        streetlist = soup.findAll("span", {"itemprop": "streetAddress"})
        street = ""
        for st in streetlist:
            if st.text in street:
                continue
            street = street + st.text + " "
        city = soup.find("span", {"itemprop": "addressLocality"}).text
        state = soup.find("span", {"itemprop": "addressRegion"}).text
        pcode = soup.find("span", {"itemprop": "postalCode"}).text
        phone = soup.find("span", {"itemprop": "telephone"}).text
        ccode = "CA"
        lat = r.text.split('"lat":', 1)[1].split(",", 1)[0]
        longt = r.text.split('"lng":', 1)[1].split(",", 1)[0]
        data.append(
            [
                "https://www.landmarkcinemas.com/",
                link,
                title,
                street.strip(),
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
