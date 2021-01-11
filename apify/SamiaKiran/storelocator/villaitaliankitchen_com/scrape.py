from bs4 import BeautifulSoup
import csv
import usaddress
from sgrequests import SgRequests
from sglogging import sglog

website = "villaitaliankitchen_com"
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
    data = []
    url = "https://www.villaitaliankitchen.com/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.findAll("div")
    for loc in loclist:
        try:
            if (
                "flex" in loc["id"]
                and "flexContainer" in loc["class"]
                and loc.find("h4").text
            ):
                templist = loc.findAll("div", {"class", "row js-group-row"})

                if len(templist) > 5:
                    i = 1
                    while i < len(templist):
                        title = templist[i].text
                        title = title.split("Less", 1)[0].strip()
                        phone = templist[i + 2]
                        phone = phone.find("p", {"class": "fp-el"}).text
                        phone = phone.split("Call", 1)[1].split("for", 1)[0].strip()
                        address = templist[i + 1]
                        address = address.find("p", {"class": "fp-el"}).text.strip()
                        j = 0
                        street = ""
                        city = ""
                        state = ""
                        pcode = ""
                        address = address.replace(",", " ")
                        address = usaddress.parse(address)
                        while j < len(address):
                            temp = address[j]
                            if (
                                temp[1].find("Address") != -1
                                or temp[1].find("Street") != -1
                                or temp[1].find("Recipient") != -1
                                or temp[1].find("Occupancy") != -1
                                or temp[1].find("BuildingName") != -1
                                or temp[1].find("USPSBoxType") != -1
                                or temp[1].find("USPSBoxID") != -1
                            ):
                                street = street + " " + temp[0]
                            if temp[1].find("PlaceName") != -1:
                                city = city + " " + temp[0]
                            if temp[1].find("StateName") != -1:
                                state = state + " " + temp[0]
                            if temp[1].find("ZipCode") != -1:
                                pcode = pcode + " " + temp[0]
                            j += 1
                        city = city.strip()
                        state = state.strip()
                        data.append(
                            [
                                "https://www.villaitaliankitchen.com/",
                                "<MISSING>",
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
                                "<MISSING>",
                            ]
                        )
                        i += 3
                else:
                    title = templist[1].text
                    title = title.split("Less", 1)[0]
                    address = templist[2]
                    address = address.find("p", {"class": "fp-el"}).text.strip()
                    phone = templist[3]
                    try:
                        phone = phone.find("p", {"class": "fp-el"}).text
                        phone = phone.split("Call", 1)[1].split("for", 1)[0].strip()
                    except:
                        phone = "<MISSING>"
                    i = 0
                    street = ""
                    city = ""
                    state = ""
                    pcode = ""
                    address = address.replace(",", " ")
                    address = usaddress.parse(address)
                    while i < len(address):
                        temp = address[i]
                        if (
                            temp[1].find("Address") != -1
                            or temp[1].find("Street") != -1
                            or temp[1].find("Recipient") != -1
                            or temp[1].find("Occupancy") != -1
                            or temp[1].find("BuildingName") != -1
                            or temp[1].find("USPSBoxType") != -1
                            or temp[1].find("USPSBoxID") != -1
                        ):
                            street = street + " " + temp[0]
                        if temp[1].find("PlaceName") != -1:
                            city = city + " " + temp[0]
                        if temp[1].find("StateName") != -1:
                            state = state + " " + temp[0]
                        if temp[1].find("ZipCode") != -1:
                            pcode = pcode + " " + temp[0]
                        i += 1
                    city = city.strip()
                    state = state.strip()
                    data.append(
                        [
                            "https://www.villaitaliankitchen.com/",
                            "<MISSING>",
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
                            "<MISSING>",
                        ]
                    )
        except:
            pass
    return data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


scrape()
