from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("timessupermarkets_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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
    url = "https://www.timessupermarkets.com/store"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    content = soup.find("div", {"class": "view-content"})
    content = soup.findAll("div", {"class": "views-row"})
    for store in content:
        links = store.find("div", {"class": "store-list-box-title"})
        link = links.find("a")["href"]
        title = links.text
        link = "https://www.timessupermarkets.com" + link
        p = session.get(link, headers=headers, verify=False)
        bs = BeautifulSoup(p.text, "html.parser")
        store_box = bs.find("div", {"class": "store-node-box"})
        address = store_box.find("div", {"class": "field-item even"}).text
        phone = store_box.find(
            "div",
            {
                "class": "field field-name-field-store-phone field-type-text field-label-above"
            },
        )
        phone = phone.find("div", {"class": "field-items"}).find("a")["href"]
        hours = store_box.find(
            "div",
            {
                "class": "field field-name-field-store-hours field-type-text field-label-above"
            },
        )
        hours = hours.find("div", {"class": "field-items"}).text.strip()
        hours = hours.replace("Everyday", "Mon-Sun:")
        hours = hours.replace("Midnight", "12 am")
        hours = hours.replace("M-Sat", "Mon-Sat:")
        hours = hours.replace("(temporary closing at 11 pm until further notice)", "")
        hours = hours.strip()
        address = address.split(" •")
        street = address[0].strip()
        city = address[1].strip()
        state = "HI"
        pcode = address[-1].strip()
        phone = phone.lstrip("tel:")

        data.append(
            [
                "https://www.timessupermarkets.com/",
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
                "<MISSING>",
                "<MISSING>",
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
