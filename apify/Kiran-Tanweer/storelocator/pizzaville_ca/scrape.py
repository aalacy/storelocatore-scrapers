from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("pizzaville_ca")

session = SgRequests()

headers = {
    "authority": "www.pizzaville.ca",
    "method": "GET",
    "path": "/stores",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "__utmc=91295899; __utmz=91295899.1612812537.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); PIZZAVILLE=crgplomrcjfmhd6bkkbhflme92; __utma=91295899.848614800.1612812537.1612812537.1613634105.2; __utmt=1; _fbp=fb.1.1613634105844.272618394; __utmb=91295899.4.9.1613634155300; AWSALB=zjysWyE51ZP1cfJeyeSd+nL/JYxvNcRoIo1sNzV1Vx9TerlzLC9t/3KZX2Rb8Wi5IQqFQFBwH6A6zIBv6pjIdWuGtFzfmfoT/e7Mgq6B0HXNh0MkA3qB9AmgUCGu; AWSALBCORS=zjysWyE51ZP1cfJeyeSd+nL/JYxvNcRoIo1sNzV1Vx9TerlzLC9t/3KZX2Rb8Wi5IQqFQFBwH6A6zIBv6pjIdWuGtFzfmfoT/e7Mgq6B0HXNh0MkA3qB9AmgUCGu",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}


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
    data = []
    url = "https://www.pizzaville.ca/stores"
    stores_req = session.get(url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    soup = str(soup)
    locations = soup.split("var locations = [")[1].split("];")[0]
    location = locations.split("],")
    location.pop(-1)
    for loc in location:
        loc = loc.strip()
        coords = loc.split("<br/>',")[1].split(",'<a")[0].strip()
        coords = coords.split(",")
        lat = coords[0]
        lng = coords[1]
        link = loc.split('<a href="')[1].split('" class')[0].strip()
        link = "https://www.pizzaville.ca" + link
        address = loc.split('"small-title">')[1].split("Tel:")[0]
        address = address.split("</span>")[1]
        address = address.rstrip("<br />")
        street = address.replace("<br />", ", ")
        street = street.replace(" , ", ", ")
        state = "<MISSING>"
        pcode = "<MISSING>"
        r = session.get(link, headers=headers)
        bs = BeautifulSoup(r.text, "html.parser")
        div_right = bs.find("div", {"class": "column right"})
        info = div_right.findAll("span")
        title = info[-3].text
        city = info[-2].text
        phone = info[-1].text
        div_left = bs.find("div", {"class": "column left"})
        hours = div_left.text.strip()
        hours = hours.replace("\n", " ")

        if hours == "":
            hours = "Store Closed"
        link = link.strip()
        title = title.strip()
        street = street.strip()
        city = city.strip()
        state = state.strip()
        pcode = pcode.strip()
        phone = phone.strip()
        lat = lat.strip()
        lng = lng.strip()
        hours = hours.strip()

        data.append(
            [
                "https://www.pizzaville.ca/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "CAN",
                "<MISSING>",
                phone,
                "<MISSING>",
                lat,
                lng,
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
