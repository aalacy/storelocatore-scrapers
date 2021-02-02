import csv
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup

website = "dangelos_com"
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
    data = []
    url = "https://locations.dangelos.com/index.html"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    statelist = soup.find("div", {"class": "Directory"}).findAll(
        "a", {"class": "c-directory-list-content-item-link Link--main"}
    )
    for stnow in statelist:
        stlink = "https://locations.dangelos.com/" + stnow["href"]
        r = session.get(stlink, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        citylist = soup.find("div", {"class": "Directory"}).findAll(
            "a", {"class": "c-directory-list-content-item-link Link--main"}
        )

        for citynow in citylist:
            citylink = "https://locations.dangelos.com/" + citynow["href"]
            r = session.get(citylink, headers=headers, verify=False)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                branchlist = soup.find("ul", {"class": "c-LocationGrid"}).findAll("li")
                for branch in branchlist:
                    branch = branch.find("div", {"class": "Teaser-details"}).find(
                        "a", {"class": "Link--main"}
                    )
                    branch = "https://locations.dangelos.com/" + branch["href"]
                    branch = branch.replace("../", "")
                    r = session.get(branch, headers=headers, verify=False)
                    soup = BeautifulSoup(r.text, "html.parser")
                    store = r.text.split('"id":', 1)[1].split(",", 1)[0].strip()
                    lat = r.text.split('"latitude":', 1)[1].split(",", 1)[0].strip()
                    longt = r.text.split('"longitude":', 1)[1].split(",", 1)[0].strip()
                    title = (
                        soup.find("h1", {"class": "Nap-title Heading Heading--lead"})
                        .text.replace("\n", " ")
                        .strip()
                    )
                    street = soup.find(
                        "span", {"class": "c-address-street-1"}
                    ).text.strip()
                    city = (
                        soup.find("span", {"class": "c-address-city"})
                        .text.replace(",", "")
                        .strip()
                    )
                    state = soup.find("span", {"class": "c-address-state"}).text.strip()
                    pcode = soup.find(
                        "span", {"class": "c-address-postal-code"}
                    ).text.strip()
                    phone = soup.find("span", {"id": "telephone"}).text.strip()
                    hours = soup.find(
                        "table", {"class": "c-location-hours-details"}
                    ).text.strip()
                    hours = (
                        hours.replace("Day of the WeekHours", "")
                        .replace("day", "day ")
                        .replace("PM", "PM ")
                        .strip()
                    )
                    data.append(
                        [
                            "https://dangelos.com/",
                            branch,
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
            except:
                branch = citylink
                store = r.text.split('"id":', 1)[1].split(",", 1)[0].strip()
                lat = r.text.split('"latitude":', 1)[1].split(",", 1)[0].strip()
                longt = r.text.split('"longitude":', 1)[1].split(",", 1)[0].strip()
                title = (
                    soup.find("h1", {"class": "Nap-title Heading Heading--lead"})
                    .text.replace("\n", " ")
                    .strip()
                )
                street = soup.find("span", {"class": "c-address-street-1"}).text.strip()
                city = (
                    soup.find("span", {"class": "c-address-city"})
                    .text.replace(",", "")
                    .strip()
                )
                state = soup.find("span", {"class": "c-address-state"}).text.strip()
                pcode = soup.find(
                    "span", {"class": "c-address-postal-code"}
                ).text.strip()
                phone = soup.find("span", {"id": "telephone"}).text.strip()
                hours = soup.find(
                    "table", {"class": "c-location-hours-details"}
                ).text.strip()
                hours = (
                    hours.replace("Day of the WeekHours", "")
                    .replace("day", "day ")
                    .replace("PM", "PM ")
                    .strip()
                )
                data.append(
                    [
                        "https://dangelos.com/",
                        branch,
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
    return data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


scrape()
