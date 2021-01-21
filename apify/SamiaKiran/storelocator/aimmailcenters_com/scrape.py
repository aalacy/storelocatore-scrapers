import csv
import json
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "aimmailcenters_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

session = SgRequests()
headers = {
    "cookie": "__cfduid=dc43abb6ee2f8533c2657e5a18f9df9321610819518; _ga=GA1.2.524291821.1610819528; _gid=GA1.2.823925842.1611037556; has_js=1; _gat_gtag_UA_32445257_1=1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
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
        url = "https://www.aimmailcenters.com/locations"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "view-content"}).findAll(
            "div", {"class": "location-name"}
        )
        for loc in loclist:
            link = loc.find("a")["href"]
            store = link.split("/", 1)[1]
            link = "https://www.aimmailcenters.com" + link
            r = session.get(link, headers=headers, verify=False)
            loc = (
                r.text.split('<script type="application/ld+json">')[1]
                .split("</script>", 1)[0]
                .replace("\n", "")
                .strip()
            )
            loc = json.loads(loc)
            street = loc["address"]["streetAddress"]
            city = loc["address"]["addressLocality"]
            state = loc["address"]["addressRegion"]
            pcode = loc["address"]["postalCode"]
            lat = loc["geo"]["latitude"]
            longt = loc["geo"]["longitude"]
            phone = loc["telephone"]
            title = "AIM" + " " + city
            soup = BeautifulSoup(r.text, "html.parser")
            hour_mf = soup.find(
                "div", {"class": "views-field views-field-field-store-hours-mf"}
            ).findAll("span")
            hour_sa = soup.find(
                "div", {"class": "views-field views-field-field-store-hours-sat"}
            ).findAll("span")
            hour_su = soup.find(
                "div", {"class": "views-field views-field-field-store-hours-sun"}
            ).findAll("span")
            hours = (
                hour_mf[0].text
                + hour_mf[1].text
                + " "
                + hour_sa[0].text
                + hour_sa[1].text
                + " "
                + hour_su[0].text
                + hour_su[1].text
            )
            final_data.append(
                [
                    "https://www.aimmailcenters.com/",
                    link,
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
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
