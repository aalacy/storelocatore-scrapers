import csv
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "littlesprouts_com"
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
    link_list = []
    if True:
        url = "https://littlesprouts.com/schools/"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.findAll("div", {"class": "x-container max width"})
        for link in linklist:
            loclist = link.findAll("div", {"class": "x-column x-sm x-1-4"})
            for loc in loclist:
                try:
                    link = loc.find(
                        "a", {"class": "x-btn purple-btn x-btn-small x-btn-block"}
                    )["href"]
                except:
                    continue
                if link in link_list:
                    temp = loc.find(
                        "h3",
                        {"class": "h-custom-headline cs-ta-center mbs mtn h4 accent"},
                    ).text
                    temp = temp.lower()
                    link = "http://littlesprouts.com/schools/" + temp + "/"
                link_list.append(link)
                r = session.get(link, headers=headers, verify=False)
                soup = BeautifulSoup(r.text, "html.parser")
                longt, lat = (
                    soup.select_one("iframe[src*=maps]")["src"]
                    .split("!2d", 1)[1]
                    .split("!2m", 1)[0]
                    .split("!3d")
                )
                if "!3m" in lat:
                    lat = lat.split("!3m", 1)[0]
                temp_address = soup.findAll("div", {"class": "x-text"})
                if len(temp_address) == 7:
                    hours = temp_address[6].text.split("\n")
                    hours = hours[0] + " " + hours[1]
                    address = temp_address[5].text.split("|", 1)[0].strip()
                    if "Infant" in address:
                        address = temp_address[4].text.split("|", 1)[0].strip()
                else:
                    hours = temp_address[5].text.split("\n")
                    hours = hours[0] + " " + hours[1]
                    address = temp_address[4].text.split("|", 1)[0].strip()
                    if "Infant" in address:
                        address = temp_address[3].text.split("|", 1)[0].strip()
                    elif "Learn About Transportation Availability" in address:
                        hours = temp_address[7].text.split("\n")
                        hours = hours[0] + " " + hours[1]
                        address = temp_address[6].text.split("|", 1)[0].strip()
                address = address.split(",")
                street = address[0]
                city = address[1]
                title = city
                temp = address[2].split()
                state = temp[0]
                try:
                    pcode = temp[1]
                except:
                    pcode = "<MISSING>"
                phone = soup.find("a", {"id": "call-btn-desktop"}).text.strip()
                final_data.append(
                    [
                        "https://littlesprouts.com/",
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
