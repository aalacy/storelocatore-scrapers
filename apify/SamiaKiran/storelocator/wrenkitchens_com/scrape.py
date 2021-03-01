import csv
import json
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "wrenkitchens_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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
        for row in data:
            writer.writerow(row)
        log.info(f"No of records being processed: {len(data)}")


def fetch_data():
    # Your scraper here
    final_data = []
    if True:
        url = "https://www.wrenkitchens.com/showrooms"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "showrooms-wrapper container"}).findAll(
            "a", {"class": "showroom-link"}
        )
        for loc in loclist:
            link = loc["href"]
            r = session.get(link, headers=headers)
            temp = r.text
            address = temp.split("var storeData = ")[1].split("};", 1)[0] + "}"
            address = address.replace("'", '"')
            phone = (
                temp.split('"telephone":')[1]
                .split("}", 1)[0]
                .replace('"', "")
                .replace("}", "")
            )
            hour_list = temp.split('"openingHoursSpecification": ')[1].split("]", 1)[
                0
            ] + "]".replace("'", '"')
            hour_list = json.loads(hour_list)
            address = json.loads(address)
            title = "Wren Kitchens" + " " + address["title"]
            lat = address["lat"]
            longt = address["lng"]
            try:
                street = (
                    address["address"]["firstLine"] + " " + ["address"]["secondLine"]
                )
            except:
                street = address["address"]["firstLine"]
            city = address["address"]["town"]
            state = address["address"]["county"]
            pcode = address["address"]["postCode"]
            hours = ""
            for hour in hour_list:
                day = hour["dayOfWeek"]
                day = day.split("/", 3)[3]
                time = hour["opens"] + "-" + hour["closes"]
                hours = hours + " " + day + " " + time
            final_data.append(
                [
                    "https://www.wrenkitchens.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "UK",
                    "<MISSING>",
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    hours,
                ]
            )
        return final_data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
