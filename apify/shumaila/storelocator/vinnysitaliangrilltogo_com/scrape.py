from bs4 import BeautifulSoup
import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("vinnysitaliangrilltogo_com")


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
    url = "https://vinnysitaliangrilltogo.com"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = (
        soup.find("footer", {"id": "footer"})
        .find("div", {"class": "footer-top"})
        .findAll("div", {"class": "col-lg-6 col-md-6 footer-links"})
    )
    for div in divlist:
        content = div.text.lstrip().rstrip().splitlines()
        title = content[0]
        street, city, state = content[3].lstrip().split(", ", 2)
        state, pcode = state.lstrip().split(" ", 1)
        pcode = pcode.lstrip().split(",")[0]
        phone = content[4]
        hours = " ".join(content[5:])
        data.append(
            [
                "https://vinnysitaliangrilltogo.com",
                "https://vinnysitaliangrilltogo.com",
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone.replace("Phone: ", ""),
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                hours,
            ]
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
