import csv
import json
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
    referlinks = []
    streetlist = []
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
                        link = address[0]["href"]
                        phone = address[1].text
                        hours = temp.find("div", {"class": "hours"}).text.replace(
                            "\n", " "
                        )
                        if "tel:" not in link:
                            link = link + "?relatedposts=1"
                            r = session.get(link, headers=headers, verify=False)
                            referlist = r.text.split('"items":')[1].split("}]}", 1)[0]
                            referlist = referlist + "}]"
                            referlist = json.loads(referlist)
                            for reference in referlist:
                                referlinks.append(reference["url"])
                except:
                    address = temp.find("div", {"class": "address"}).text.replace(
                        "\n", " "
                    )
                    phone = temp.find("div", {"class": "address"}).find("a").text
                    street = address.split(phone, 1)[0]
                    hours = temp.find("div", {"class": "hours"}).text.replace("\n", " ")
                if street in streetlist:
                     continue
                streetlist.append(street.strip())
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
                    link = address[0]["href"]
                    phone = address[1].text
                    if "tel:" not in link:
                        link = link + "?relatedposts=1"
                        r = session.get(link, headers=headers, verify=False)
                        referlist = r.text.split('"items":')[1].split("}]}", 1)[0]
                        referlist = referlist + "}]"
                        referlist = json.loads(referlist)
                        for reference in referlist:
                            referlinks.append(reference["url"])
            except:
                address = temp.find("div", {"class": "address"}).text.replace("\n", " ")
                phone = temp.find("div", {"class": "address"}).find("a").text
                street = address.split(phone, 1)[0]
            hours = temp.find("div", {"class": "hours"}).text.replace("\n", " ")
            if street in streetlist:
                continue
            streetlist.append(street.strip())
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
    for refer in referlinks:
        r = session.get(refer, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        templist = soup.find("div", {"class": "wpsl-locations-details"})
        title = templist.find("strong").text
        temp = templist.find("div", {"class": "wpsl-location-address"}).findAll("span")
        if len(temp) > 5:
            street = temp[1].text
            city = temp[2].text.replace(",", "")
            state = temp[3].text
            pcode = temp[4].text
            ccode = temp[5].text
        else:
            street = temp[0].text
            city = temp[1].text.replace(",", "")
            state = temp[2].text
            pcode = temp[3].text
            ccode = temp[4].text
        phone = (
            templist.find("div", {"class": "wpsl-contact-details"}).find("span").text
        )
        hourlist = soup.find("table", {"class": "wpsl-opening-hours"}).findAll("tr")
        hours = ""
        for hour in hourlist:
            hour = hour.findAll("td")
            day = hour[0].text
            time = hour[1].find("time").text
            hours = hours + " " + day + " " + time
        if street in streetlist:
            continue
        streetlist.append(street.strip())
        data.append(
            [
                "https://www.pizzaking.com/",
                refer.strip(),
                title.strip(),
                street.strip(),
                city.strip(),
                state.strip(),
                pcode.strip(),
                ccode.strip(),
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
