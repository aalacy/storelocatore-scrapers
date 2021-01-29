from bs4 import BeautifulSoup
import csv
from sgrequests import SgRequests

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
    p = 0
    url = "https://www.fordsgarageusa.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    link_list = soup.findAll("div", {"class": "service-content"})
    p = 0
    for rep in link_list:
        title = rep.find("h4").text
        det = rep.find("div", {"class": "service-details"}).text.splitlines()
        try:
            hours = rep.find("p", {"class": "hours-row"}).text.replace("\n", " ")
        except:
            hours = rep.findAll("p")[3].text
            if hours.find("VIEW") > -1:
                hours = rep.findAll("p")[2].text
        if hours.find("Opening") > -1:
            continue
        street = det[1]
        flag = 0

        try:
            city, state = det[2].split(", ")
            state, pcode = state.lstrip().split(" ")
        except:
            flag = 1
            pass
        link = rep.find("p", {"class": "location-links"})
        link = link.find("a")
        link = "https://www.fordsgarageusa.com" + link["href"]
        r = session.get(link, headers=headers, verify=False)

        soup = BeautifulSoup(r.text, "html.parser")
        coord = soup.findAll("iframe")
        coord = str(coord[1]["src"])
        coord = coord.split("!2d", 1)[1].split("!2m")[0]
        longt, lat = coord.split("!3d")
        if flag == 1:
            addresslist = soup.findAll("p", {"class": "hours-row"})
            for adr in addresslist:
                try:
                    address = adr.select_one("a[href*=maps]").text.replace("\n", ",")
                except:
                    pass
            address = address.split(",")
            if len(address) == 4:
                street = address[0] + " " + address[1]
                city = address[2]
                state = address[3]
            elif len(address) == 3:
                street = address[0]
                city = address[1]
                state = address[2]
            state, pcode = state.lstrip().split(" ", 1)
        det = rep.find("div", {"class": "service-details"}).findAll("p")
        phone = ""
        for dt in det:
            if dt.text.find("Phone") > -1 and phone == "":
                phone = dt.text
            elif dt.text.find("Thursday") > -1 and (
                hours == "" or hours.find("Phone") > -1
            ):
                hours = dt.text
        phone = phone.replace("Phone:", "")
        phone = phone.lstrip()
        hours = hours.replace("\n", " ")
        if "OPENING SOON" in hours:
            continue
        try:
            lat = lat.split("!3m", 1)[0]
        except:
            pass
        data.append(
            [
                "https://www.fordsgarageusa.com/",
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
                lat,
                longt,
                hours,
            ]
        )

        p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
