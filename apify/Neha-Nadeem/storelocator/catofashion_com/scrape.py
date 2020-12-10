from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("catofashion_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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


def fetch_data():
    data = []

    url = "https://www.catofashions.com/catostores.cfm"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")

    selectlist = soup.find("select", {"name": "locSt"})
    statelist = selectlist.find_all("option")
    statecode = [o.get("value") for o in statelist]

    if statecode[0] == "DEFAULT":
        statecode.pop(0)
    for st in statecode:
        url = (
            "https://www.catofashions.com/catostores.cfm?locRad=10%20mi&locZip=&locSt="
            + st
        )
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        link = url
        content = soup.findAll("div", {"class": "mapAddress"})

        count = 1

        for con in content:
            store = "store" + str(count)
            count = count + 1

            try:
                temp = con.find("h5").text
                title = con.find("h4").text
                title = temp + " " + title
            except:
                title = con.find("h4").text
            temp = con.find("h4").text
            city = temp.split(", ", 1)[0]
            state = temp.split(", ", 1)[1]
            if (len(state)) > 3:
                state = state[:3]
            street = con.find("p").text
            phone = con.find("a").text

            pcode = con.find("a", {"href": "javascript: void(false)"})["onclick"]
            pcode = pcode[-7:]
            pcode = pcode[:-2]

            latlong = con.find("h4")["onclick"].split("(")[1].split(")")[0]
            lat = latlong.split(",", 2)[1]
            long = latlong.split(",")[-1]

            data.append(
                [
                    "https://www.catofashions.com/",
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
                    long,
                    "<MISSING>",  # hours,
                ]
            )
    return data


def scrape():

    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
