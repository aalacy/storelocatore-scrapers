import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("jchristophers_com")


session = SgRequests()


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
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    data = []
    base_url = "https://jchristophers.com/locations"
    r = session.get(base_url, headers=headers, timeout=5)
    soup = BeautifulSoup(r.text, "html.parser")
    data_list = soup.find("div", {"class", "et_pb_row_3"}).find_all("a")
    for loc in data_list:
        link = "https://jchristophers.com" + loc.get("href")
        response = session.get(link, headers=headers)
        s = BeautifulSoup(response.text, "html.parser")
        det = s.find("div", {"class", "et_pb_text_1"}).findAll("p")

        title = s.find("div", {"class", "et_pb_text_inner"}).find("h1").text
        street = det[0].findAll("a")[0].text
        city = det[0].findAll("a")[1].text.split(",")[0].strip()
        state = det[0].findAll("a")[1].text.split(", ")[1].split(" ")[0]
        zip = det[0].findAll("a")[1].text.split(", ")[1].split(" ")[1]
        phone = det[1].find("a").text
        hours_of_operation = det[2].text
        data.append(
            [
                "https://jchristophers.com",
                link,
                title,
                street,
                city,
                state,
                zip,
                "US",
                "<MISSING>",
                phone,
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                hours_of_operation,
            ]
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
