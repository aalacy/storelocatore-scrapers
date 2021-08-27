from bs4 import BeautifulSoup
import csv
import re


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
    pattern = re.compile(r"\s\s+")
    url = "http://www.superquik.net/locations(1).html"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = (
        soup.find("div", {"class": "content"})
        .find("p", {"align": "center"})
        .findAll("a")
    )

    p = 0
    for div in divlist:

        statelink = "http://www.superquik.net/" + div["href"]
        r = session.get(statelink, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        citylist = soup.find("div", {"class": "content"}).findAll("a")
        content = soup.find("div", {"class": "content"}).text
        content = re.sub(pattern, "\n", content).strip()

        for i in range(0, len(citylist)):
            city = citylist[i]
            link = "http://www.superquik.net/" + city["href"]
            try:
                title, store = city.text.replace("\n", " ").strip().split("#")
            except:
                continue
            if i == len(citylist) - 1:
                address = content.split("#" + store, 1)[1]
            else:
                address = content.split("#" + store, 1)[1].split(
                    citylist[i + 1].text.split("#", 1)[0].replace("\n", " ").strip(), 1
                )[0]
            address = re.sub(pattern, "\n", address).strip().splitlines()
            street = address[0]
            city, state = address[1].split(", ", 1)
            state, pcode = state.strip().split(" ", 1)
            phone = address[2].strip()
            hours = "OPEN 24 HOURS"
            data.append(
                [
                    "http://www.superquik.net/",
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
