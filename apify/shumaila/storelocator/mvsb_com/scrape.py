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
    p = 0
    data = []
    url = "https://www.mvsb.com/about/locations/?doing_wp_cron=1622534811.0141370296478271484375"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = str(soup.find("div", {"class": "accordion-locations"}))
    divlist = divlist.split("<h3")[1:]

    for div in divlist:
        div = "<h3" + div
        div = BeautifulSoup(div, "html.parser")
        city = div.find("h3").text
        state = "NH"
        title = div.find("strong").text
        street = div.find("p").text.split(title, 1)[1].split("(", 1)[0]
        phone = div.find("li", {"class": "phone"}).text.split(":", 1)[1].strip()
        hours = (
            div.find("div", {"class": "lobby"})
            .text.replace("Lobby Hours", "")
            .replace("\n", " ")
            .strip()
        )

        data.append(
            [
                "https://www.mvsb.com/",
                url,
                title,
                street,
                city,
                state,
                "<MISSING>",
                "US",
                "<MISSING>",
                phone,
                "Branch",
                "<MISSING>",
                "<MISSING>",
                hours,
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
