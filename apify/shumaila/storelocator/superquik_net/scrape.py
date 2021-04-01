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
        citylist = soup.findAll("p", {"class": "style9"})
        if len(citylist) == 0:
            citylist = soup.find("span", {"class": "style9"})
        for city in citylist:
            try:
                link = "http://www.superquik.net/" + city.find("a")["href"]
            except:
                try:
                    link = "http://www.superquik.net/" + city["href"]
                except:
                    break
            content = city.text.strip().splitlines()
            title = content[0] + " " + content[1].lstrip()
            title = title.strip()
            store = content[1].split("#", 1)[1]
            try:
                street = content[2].lstrip()
                city, state = content[3].lstrip().split(", ", 1)
                state, pcode = state.lstrip().split(" ", 1)
                phone = content[4].lstrip()
            except:
                content = (
                    soup.findAll("span", {"class": "style9"})[1]
                    .text.strip()
                    .splitlines()
                )
                street = content[0].lstrip()
                city, state = content[1].lstrip().split(", ", 1)
                state, pcode = state.lstrip().split(" ", 1)
                phone = content[2].lstrip()
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
