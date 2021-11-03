import csv
import re
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "thebakedbear_com"
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
        # Body
        temp_list = []  # ignoring duplicates
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
        log.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    # Your scraper here
    final_data = []
    if True:
        url = "https://www.thebakedbear.com/locations/"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.find("div", {"class": "fusion-builder-row fusion-row"}).findAll(
            "div", {"class": "fusion-layout-column"}
        )[1:]
        for link in linklist:
            try:
                templist = link.find("ul").findAll("li")
            except:
                pass
            for temp in templist:
                link = temp.find("a")["href"]
                link = "https://www.thebakedbear.com" + link
                r = session.get(link, headers=headers, verify=False)
                if "COMING SOON" in r.text:
                    continue
                coord = r.text.split('"latitude":"')[1].split("}],", 1)[0]
                lat = coord.split(",", 1)[0].replace('"', "")
                longt = coord.split('longitude":"', 1)[1].replace('"', "")
                if ",cache:" in longt:
                    longt = longt.split(",cache:", 1)[0]
                soup = BeautifulSoup(r.text, "html.parser")
                title = soup.find("h2", {"class": "title-heading-center"}).text
                temp_address = soup.findAll("div", {"class": "fusion-li-item-content"})
                if re.match(
                    r"^(\([0-9]{3}\) |[0-9]{3}-)[0-9]{3}-[0-9]{4}$",
                    temp_address[-1].text.strip(),
                ):
                    phone = temp_address[-1].text.strip()
                else:
                    phone = "<MISSING>"
                address = temp_address[0].get_text(separator="|", strip=True).split("|")
                if len(address) > 2:
                    street = address[0] + " " + address[1]
                    temp_address = address[2].split(",")
                    city = temp_address[0]
                    temp_address = temp_address[1].split()
                    if len(temp_address) > 2:
                        state = temp_address[0] + " " + temp_address[1]
                        pcode = temp_address[2]
                    else:
                        state = temp_address[0]
                        pcode = temp_address[1]
                else:
                    street = address[0]
                    temp_address = address[1].split(",")
                    city = temp_address[0]
                    temp_address = temp_address[1].split()
                    state = temp_address[0]
                    pcode = temp_address[1]
                hourlist = soup.findAll("div", {"class": "fusion-column-wrapper"})[
                    1
                ].findAll("li")
                hours = ""
                for hour in hourlist:
                    hours = hours + hour.text + " "
                if not hours:
                    hours = "<MISSING>"
                final_data.append(
                    [
                        "https://www.thebakedbear.com/",
                        link,
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        "US",
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
