import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
import time

logger = SgLogSetup().get_logger("bluesushisakegrill_com")

session = SgRequests()


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
    addresses = []
    base_url = "https://bluesushisakegrill.com/"
    get_url = "https://bluesushisakegrill.com/locations"
    r = session.get(get_url)
    soup = BeautifulSoup(r.text, "html.parser")
    store_name = []
    store_detail = []
    return_main_object = []
    name1 = []
    main = soup.find_all("h3", {"class": "locations-item-title"})
    for i in main:
        title = i.find("a").text
        link = i.find("a")["href"]
        r1 = session.get(link)
        soup1 = BeautifulSoup(r1.text, "html.parser")
        main1 = soup1.find("div", {"class": "location_details-address"})
        data = list(main1.stripped_strings)
        address = data[2]
        street = address
        locality = data[-1]
        locality = locality.split(",")
        city = locality[0].strip()
        locality = locality[1].strip()
        locality = locality.split(" ")
        if len(locality) == 2:
            pcode = locality[1]
            state = locality[0]
        else:
            state = locality[0]
            pcode = "<MISSING>"
        phone = soup1.find("p", {"class": "location_details-phone"}).text.strip()
        hour_tmp = soup1.find("div", {"class": "location_details-hours"})
        hour = " ".join(list(hour_tmp.stripped_strings))
        cords = soup1.find(
            "a",
            {
                "class": "location_details-address-directions button button--primary button--solid"
            },
        )["href"].split("@")
        if len(cords) == 2:

            lat = (
                soup1.find(
                    "a",
                    {
                        "class": "location_details-address-directions button button--primary button--solid"
                    },
                )["href"]
                .split("@")[1]
                .split(",")[0]
            )
            lng = (
                soup1.find(
                    "a",
                    {
                        "class": "location_details-address-directions button button--primary button--solid"
                    },
                )["href"]
                .split("@")[1]
                .split(",")[1]
            )
        elif len(cords) == 1:
            lat = (
                soup1.find(
                    "a",
                    {
                        "class": "location_details-address-directions button button--primary button--solid"
                    },
                )["href"]
                .split("=")[-1]
                .split("+")[0]
            )
            lng = (
                soup1.find(
                    "a",
                    {
                        "class": "location_details-address-directions button button--primary button--solid"
                    },
                )["href"]
                .split("=")[-1]
                .split("+")[1]
            )
        if phone == "":
            phone = "<MISSING>"
        hour = hour.rstrip(":").strip()

        if (
            link
            == "https://bluesushisakegrill.com/locations/illinois/chicago/lincoln-park"
        ):
            if street == "Chicago, IL":
                street = "<MISSING>"
        store = list()
        store.append("https://bluesushisakegrill.com")
        store.append(link)
        store.append(title)
        store.append(street)
        store.append(city)
        store.append(state)
        store.append(pcode)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hour)
        yield store


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
