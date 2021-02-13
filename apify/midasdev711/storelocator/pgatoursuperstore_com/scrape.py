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
    url = "https://www.pgatoursuperstore.com/stores"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "store"})
    p = 0
    for div in divlist:
        store = str(div["id"])
        link = "https://www.pgatoursuperstore.com" + div.find("a")["href"]
        title = div.find("span", {"class": "primaryName"}).text
        street = (
            div.find("div", {"class": "address1"}).text
            + " "
            + div.find("div", {"class": "address2"}).text
        )
        city, state = div.find("div", {"class": "cityStateZip"}).text.split(", ", 1)
        state, pcode = state.lstrip().split(" ", 1)
        try:
            hours = (
                div.find("div", {"class": "hours"})
                .text.split("Hours:", 1)[1]
                .replace("\n", " ")
            )
        except:
            hours = div.find("div", {"class": "hours"}).text
        if "Coming" in hours:
            continue
        phone = div.find("div", {"class": "phone"}).text
        r = session.get(link, headers=headers, verify=False)
        lat = r.text.split('"latitude": ', 1)[1].split(",", 1)[0]
        longt = r.text.split('"longitude": ', 1)[1].split("\n", 1)[0]
        data.append(
            [
                "https://www.pgatoursuperstore.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                store,
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
