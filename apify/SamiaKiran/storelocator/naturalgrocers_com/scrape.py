import csv
import re
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "naturalgrocers_com"
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
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
                row[8],
                row[10],
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)
        log.info(f"No of records being processed: {len(temp_list)}")


def get_store_data(loc):
    pattern = re.compile(r"\s\s+")
    title = loc.find("div", {"class", "card-text"}).find("h3").text.replace("–", "")
    link = loc.find("div", {"class", "author-name text-center"}).find("a")["href"]
    if link in unique_locations:
        return None
    unique_locations.append(link)

    link = "https://www.naturalgrocers.com" + link
    storenum_text = "<MISSING>"
    r = session.get(link, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    log.info(link)
    if soup.find("div", {"class": "field--name-field-google-maps-link"}):
        storenum_text = (
            soup.find("div", {"class": "field--name-field-google-maps-link"})
            .find("a")
            .text.replace("GET DIRECTIONS TO OUR STORE ", "")
            .replace("Review us on Google", "")
            .strip()
        )
    else:
        storenum_text = "<MISSING>"
    if storenum_text == "":
        storenum_text = "<MISSING>"
    street = loc.find("span", {"class", "address-line1"}).text
    city = loc.find("span", {"class", "locality"}).text
    state = loc.find("span", {"class", "administrative-area"}).text
    lat = loc.find("div", {"class", "geolocation"})["data-lat"]
    longt = loc.find("div", {"class", "geolocation"})["data-lng"]
    if "Coming Soon!" in title:
        title = title.split("- Coming Soon!")[0].replace("\n", "").strip()
        title = title + " " + "- Coming Soon!"
        title = re.sub(pattern, "\n", title)
        phone = "<MISSING>"
        pcode = "<MISSING>"
        hours = "<MISSING>"
    else:
        try:
            phone = loc.find("div", {"class", "store_telephone_number"}).find("a").text
        except:
            phone = loc.find("div", {"class", "store_telephone_number"}).text
        pcode = loc.find("span", {"class", "postal-code"}).text
        hours = ""
        if loc.find("div", {"class", "office-hours"}):
            hourlist = loc.find("div", {"class", "office-hours"}).findAll(
                "div", {"class", "office-hours__item"}
            )

            for hour in hourlist:
                day = hour.find("span", {"class", "office-hours__item-label"}).text
                time = hour.find("span", {"class", "office-hours__item-slots"}).text
                hours = hours + day + " " + time + " "
        else:
            hours = "<MISSING>"
    data = [
        "https://www.naturalgrocers.com/",
        link,
        title.strip(),
        street.strip(),
        city.strip(),
        state.strip(),
        pcode.strip(),
        "US",
        storenum_text,
        phone.strip(),
        "<MISSING>",
        lat.strip(),
        longt.strip(),
        hours.strip(),
    ]

    return data


def fetch_data():
    # Your scraper here
    final_data = []
    global unique_locations
    unique_locations = []

    if True:
        url = "https://www.naturalgrocers.com/store-directory"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        statelist = soup.find("div", {"class": "select-wrapper"}).findAll("option")[1:]
        for state in statelist:
            state = state["value"]
            stateurl = (
                "https://www.naturalgrocers.com/store-directory?field_store_address_administrative_area="
                + state
            )
            r = session.get(stateurl, headers=headers, verify=False)
            soup = BeautifulSoup(r.text, "html.parser")
            storecount = soup.find("span", {"class": "store-count"}).text
            if int(storecount) > 12:
                pagecount = soup.find("nav", {"class": "pager"}).findAll(
                    "li", {"class": "pager__item"}
                )[:-2]
                for page in pagecount:
                    pageurl = page.find("a")["href"]
                    pageurl = "https://www.naturalgrocers.com/store-directory" + pageurl
                    r = session.get(pageurl, headers=headers, verify=False)
                    soup = BeautifulSoup(r.text, "html.parser")
                    loclist = soup.findAll("div", {"class": "views-row"})
                    for loc in loclist:
                        store_list = get_store_data(loc)
                        if store_list is None:
                            continue
                        final_data.append(store_list)
            else:
                loclist = soup.findAll("div", {"class": "views-row"})
                for loc in loclist:
                    store_list = get_store_data(loc)
                    if store_list is None:
                        continue
                    if store_list not in final_data:
                        final_data.append(store_list)
        return final_data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
