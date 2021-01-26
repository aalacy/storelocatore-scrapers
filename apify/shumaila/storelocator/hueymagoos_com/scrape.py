import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("hueymagoos_com")

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    }
    data = []
    base_url = "https://www.hueymagoos.com"
    p_url = "https://hueymagoos.com/locations/"
    r = session.get(p_url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    data_list = soup.findAll("div", {"class": "loc-box-new"})

    for loc in data_list:
        try:
            title = loc.find("h3").text
        except:
            continue
        if loc.find(
            "img",
            {
                "src": "https://hueymagoos.com/wp-content/uploads/coming-soon.png?b603d3&b603d3"
            },
        ):
            continue
        details = loc.find("p")
        phone = ""
        address = ""
        details = str(details).replace("<br/>", "\n")
        details = BeautifulSoup(details, "html.parser")

        if len(details.findAll("a")) > 1:
            if details.findAll("a")[0].get("href").find("tel") != -1:
                phone = details.findAll("a")[0].text
            else:
                phone = "<MISSING>"
            if details.findAll("a")[1].get("href").find("maps") != -1:
                address = details.findAll("a")[1].text
                street = address.split("\n")[0]
                city = address.split("\n")[1].split(", ")[0].strip()
                state = address.split("\n")[1].split(", ")[1].split(" ")[0].strip()
                zip = address.split("\n")[1].split(", ")[1].split(" ")[1]
            else:
                address = "<MISSING>"
            hours_of_operation = (
                details.findAll("a")[1].next_sibling.lstrip().replace("–", "-")
            )
        elif len(details.findAll("a")) == 1:
            if details.findAll("a")[0].get("href").find("tel") != -1:
                phone = details.findAll("a")[0].text
            else:
                phone = "<MISSING>"
            if details.findAll("a")[0].get("href").find("maps") != -1:
                address = details.findAll("a")[0].text
                street = address.split("\n")[0]
                city = address.split("\n")[1].split(", ")[0].strip()
                state = address.split("\n")[1].split(", ")[1].split(" ")[0].strip()
                zip = address.split("\n")[1].split(", ")[1].split(" ")[1]
            else:
                address = "<MISSING>"
            if details.findAll("a")[0].next_sibling.find("am") or details.findAll("a")[
                0
            ].next_sibling.find("pm"):
                hours_of_operation = (
                    details.findAll("a")[0]
                    .next_sibling.lstrip()
                    .replace("–", "-")
                    .replace("\n", " ")
                )
            else:
                hours_of_operation = "<MISSING>"
        else:
            if details.text:
                address = details.text
                street = address.split("\n")[0]
                city = address.split("\n")[1].split(", ")[0].strip()
                state = address.split("\n")[1].split(", ")[1].split(" ")[0].strip()
                zip = address.split("\n")[1].split(", ")[1].split(" ")[1]
            else:
                address = "<MISSING>"
            phone = "<MISSING>"
            hours_of_operation = "<MISSING>"
        data.append(
            [
                base_url,
                p_url,
                title,
                street.replace(",", "").replace("#", "No."),
                city,
                state,
                zip,
                "US",
                "<MISSING>",
                phone,
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                hours_of_operation.replace("\n", " "),
            ]
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
