import time
import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from bs4 import BeautifulSoup
from sgscrape import sgpostal as parser


logger = SgLogSetup().get_logger("breauxmart_com")


session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        temp_list = []
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)
        logger.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    data = []
    url = "https://api.freshop.com/1/stores?app_key=breaux_mart&distance=10&fields=id%2Cname&has_address=true&q=LA&token=b9d5ebe8311a1e8691c9e16d0740383e"
    stores = session.get(url, headers=headers, verify=False).json()
    for loc in stores["items"]:
        storeid = loc["id"]
        title = loc["name"]
        title2 = title.replace(" - ", "-")
        title2 = title2.replace(" ", "-")
        link = "https://www.breauxmart.com/stores/" + title2
        req = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(req.text, "html.parser")
        address = soup.find("div", {"class": "fp-store-address"}).text
        address = address.lstrip(title)
        information = soup.find(
            "div", {"class": "stores-landing-left col-md-6"}
        ).findAll("div")
        if len(information) == 19:
            hours = information[12].find("p").text
            phone = information[14].find("p").text
        else:
            hours = information[9].find("p").text
            phone = information[11].find("p").text
        phone = phone.split("Fax")[0].strip()
        phone = phone.strip()
        hours = hours.strip()
        lat = soup.find("meta", {"property": "place:location:latitude"})["content"]
        lng = soup.find("meta", {"property": "place:location:longitude"})["content"]
        parsed = parser.parse_address_usa(address)
        street1 = parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
        street = (
            (street1 + ", " + parsed.street_address_2)
            if parsed.street_address_2
            else street1
        )
        city = parsed.city if parsed.city else "<MISSING>"
        state = parsed.state if parsed.state else "<MISSING>"
        pcode = parsed.postcode if parsed.postcode else "<MISSING>"

        data.append(
            [
                "https://www.breauxmart.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                storeid,
                phone,
                "<MISSING>",
                lat,
                lng,
                hours,
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
