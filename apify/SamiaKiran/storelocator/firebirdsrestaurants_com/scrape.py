import csv
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "firebirdsrestaurants_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
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
        url = "https://firebirdsrestaurants.com/"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("select", {"id": "select_your_location"}).findAll("option")
        for loc in loclist:
            link = loc["value"]
            if not link:
                continue
            r = session.get(link, headers=headers, verify=False)
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.find("h1").text
            coords = (
                soup.find("a", {"class": "directions gtm_directions open_pixel"})[
                    "href"
                ]
                .split("&daddr=", 1)[1]
                .split(",")
            )
            lat = coords[0]
            longt = coords[1]
            address = soup.find("span", {"class": "addr"})
            temp = address.find("strong").text
            address = address.text.replace(temp, "")
            if "Coming Soon" in address:
                continue
            address = address.split(",")
            if len(address) > 3:
                street = address[0] + " " + address[1]
                city = address[2]
                temp = address[3].split()
                state = temp[0]
                try:
                    pcode = temp[1]
                except:
                    pcode = "<MISSING>"
            else:
                try:
                    street = address[0]
                    city = address[1]
                    temp = address[2].split()
                    state = temp[0]
                    try:
                        pcode = temp[1]
                    except:
                        pcode = "<MISSING>"
                except:
                    street = address[0]
                    try:
                        city = title.split()[1]
                    except:
                        city = title
                    temp = address[1].split()
                    state = temp[0]
                    try:
                        pcode = temp[1]
                    except:
                        pcode = "<MISSING>"
            phone = soup.find("a", {"class": "body-tel gtm_phone_click"}).text
            hourlist = soup.find("div", {"class": "hours-wrap"}).findAll("div")
            hours = ""
            for hour in hourlist:
                day = hour.find("span", {"class": "day"}).text
                time = hour.find("span", {"class": "time"}).text
                hours = hours + day + " " + time + " "
            final_data.append(
                [
                    "https://firebirdsrestaurants.com/",
                    link,
                    title.strip(),
                    street.strip(),
                    city.strip(),
                    state.strip(),
                    pcode.strip(),
                    "US",
                    "<MISSING>",
                    phone.strip(),
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
