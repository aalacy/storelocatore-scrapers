import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import sglog

website = "pizzaking_com"
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
        for row in data:
            writer.writerow(row)
        log.info(f"No of records being processed: {len(data)}")


def fetch_data():
    data = []
    url = "https://www.pizzaking.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    loclist = r.text.split('<section class="entry-content cf">', 1)[1].split(
        "</section>", 1
    )[0]
    loclist = loclist.split("<h3>")[1:]
    for loc in loclist:
        if len(loc) < 7:
            continue
        title = loc
        title = title.split("</h3>", 1)[0]
        templist = loc
        multiple_loc = templist.count('<div class="store">')
        if multiple_loc > 1:
            templist = (
                templist.split("</h3>", 1)[1]
                .rsplit('<div class="citygroup dontsplit">', 1)[0]
                .strip()
            )
            soup = BeautifulSoup(templist, "html.parser")
            templist = soup.findAll("div", {"class": "store"})
            for temp in templist:
                if len(temp.text) < 3:
                    continue
                try:
                    address = temp.findAll("div", {"class": "address"})
                    if len(address) > 1:
                        street = address[0].text
                        phone = address[1].find("a").text
                    else:
                        address = temp.find("div", {"class": "address"}).findAll("a")
                        street = address[0].text
                        phone = address[1].text
                        hours = temp.find("div", {"class": "hours"}).text.replace(
                            "\n", " "
                        )
                except:
                    address = temp.find("div", {"class": "address"}).text.replace(
                        "\n", " "
                    )
                    phone = temp.find("div", {"class": "address"}).find("a").text
                    street = address.split(phone, 1)[0]
                    hours = temp.find("div", {"class": "hours"}).text.replace("\n", " ")
                data.append(
                    [
                        "https://www.pizzaking.com/",
                        "https://www.pizzaking.com/locations/",
                        title.strip(),
                        street.strip(),
                        title.strip(),
                        "<MISSING>",
                        "<MISSING>",
                        "US",
                        "<MISSING>",
                        phone.strip(),
                        "<MISSING>",
                        "<MISSING>",
                        "<MISSING>",
                        hours.strip(),
                    ]
                )
        else:
            if not title:
                continue
            templist = (
                templist.split("</h3>", 1)[1]
                .rsplit('<div class="citygroup dontsplit">', 1)[0]
                .strip()
            )
            soup = BeautifulSoup(templist, "html.parser")
            temp = soup.find("div", {"class": "store"})
            if len(temp.text) < 3:
                continue
            try:
                address = temp.findAll("div", {"class": "address"})
                if len(address) > 1:
                    street = address[0].text
                    phone = address[1].find("a").text
                else:
                    address = temp.find("div", {"class": "address"}).findAll("a")
                    street = address[0].text
                    phone = address[1].text
            except:
                address = temp.find("div", {"class": "address"}).text.replace("\n", " ")
                phone = temp.find("div", {"class": "address"}).find("a").text
                street = address.split(phone, 1)[0]
            hours = temp.find("div", {"class": "hours"}).text.replace("\n", " ")
            data.append(
                [
                    "https://www.pizzaking.com/",
                    "https://www.pizzaking.com/locations/",
                    title.strip(),
                    street.strip(),
                    title.strip(),
                    "<MISSING>",
                    "<MISSING>",
                    "US",
                    "<MISSING>",
                    phone.strip(),
                    "<MISSING>",
                    "<MISSING>",
                    "<MISSING>",
                    hours.strip(),
                ]
            )
    return data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


scrape()
