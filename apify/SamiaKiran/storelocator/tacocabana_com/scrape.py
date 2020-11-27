from bs4 import BeautifulSoup
import csv
import re
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("tacocabana_com")

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
    # Your scraper here
    final_data = []
    url = "https://www.tacocabana.com/locations"
    r = session.get(url, headers=headers, verify=False)
    temp_r = r.text.split(',"list":')[1].split(',"detail"', 1)[0]
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.findAll(
        "div", {"class": "card-info styles__StyledCardInfo-s1y7dfjk-3 gCNPSz"}
    )
    cleanr = re.compile(r"<[^>]+>")
    pattern = re.compile(r"\s\s+")
    for loc in loclist:
        title = loc.find("h3")
        title = title.find("a").text
        store = title.split("#", 1)[1]
        address = loc.find("p")
        address = re.sub(cleanr, "\n", str(address))
        address = re.sub(pattern, "\n", address)
        content = address.splitlines()
        if len(content) == 7:
            street = " ".join(content[1:3])
            street = street.replace("&amp;", "&")
            city = content[3]
            state = content[4]
            pcode = content[5]
            phone = content[6]
        else:
            street = content[1]
            street = street.replace("&amp;", "&")
            city = content[2]
            state = content[3]
            pcode = content[4]
            phone = content[5]
        hours = loc.text.split(")", 1)[1]
        hours = hours.split("O", 1)[1]
        hours = "O" + hours
        temp_list = json.loads(temp_r)
        lat = "<MISSING>"
        longt = "<MISSING>"
        for temp in temp_list:
            if temp["brand_id"] == store:
                lat = temp["latitude"]
                longt = temp["longitude"]
        final_data.append(
            [
                "https://www.tacocabana.com/",
                "https://www.tacocabana.com/locations",
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
    return final_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
