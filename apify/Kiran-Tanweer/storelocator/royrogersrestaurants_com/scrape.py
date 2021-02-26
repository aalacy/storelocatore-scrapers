from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("royrogersrestaurants_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
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
    url = "https://www.royrogersrestaurants.com/locations"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    locations = soup.findAll("ul", {"class": "locations"})
    for loc in locations:
        allloc = loc.findAll("li")
        for l in allloc:
            title = l.find("h4").text
            title = title.strip()
            pagelink = l.find("h4").find("a")["href"]
            pagelink = "https://www.royrogersrestaurants.com" + pagelink
            phone = l.find("p", {"class": "phone-number"}).text
            phone = phone.strip()
            street = l.find("span", {"class": "address-line1"}).text
            street2 = l.find("span", {"class": "address-line2"})
            if street2 is not None:
                street2 = street2.text
                street = street + " " + street2
            if (
                street
                == "Highspire Travel Plaza Exit 247 Eastbound, Milepost 249.7, 300 Industrial Lane, Middletown, PA 17057"
            ):
                street = "Highspire Travel Plaza Exit 247 Eastbound, Milepost 249.7, 300 Industrial Lane"
            street = street.strip()
            city = l.find("span", {"class": "locality"}).text
            city = city.strip()
            state = l.find("span", {"class": "administrative-area"}).text
            state = state.strip()
            pcode = l.find("span", {"class": "postal-code"}).text
            pcode = pcode.strip()
            country = l.find("span", {"class": "country"}).text
            if country == "United States":
                country = "US"
            p = session.get(pagelink, headers=headers, verify=False)
            soup = BeautifulSoup(p.text, "html.parser")
            content = soup.find("div", {"class": "region-content"})
            hours = content.findAll("p")
            if len(hours) == 2:
                HOO = "<MISSING>"
            if len(hours) == 3:
                HOO = hours[-1].text.strip()
            if len(hours) == 4:
                HOO = hours[-1].text.strip()
                if (
                    pagelink
                    == "https://www.royrogersrestaurants.com/locations/manchester-lakes"
                ):
                    hr1 = hours[-1].text.strip()
                    hr2 = hours[-2].text.strip()
                    HOO = hr1 + " " + hr2
            if len(hours) == 5:
                hr1 = hours[-1].text.strip()
                hr2 = hours[-2].text.strip()
                HOO = hr1 + " " + hr2
            if len(hours) == 6:
                hr1 = hours[-1].text.strip()
                hr2 = hours[-2].text.strip()
                hr3 = hours[-3].text.strip()
                HOO = hr1 + " " + hr2 + " " + hr3
            HOO = HOO.replace("\n", " ")
            HOO = HOO.replace(",", ":").strip()
            if HOO == "":
                HOO = "<MISSING>"
            coords = soup.findAll("script")
            if len(coords) == 35:
                coord = str(coords[3])
                coord = coord.split('"coordinates":[')[1].split("]}")[0]
                lng = coord.split(",")[0].strip()
                lat = coord.split(",")[1].strip()
            else:
                lat = "<MISSING>"
                lng = "<MISSING>"
            if street.find("Travel Plaza") != -1:
                street = street.split("Travel Plaza")[1].strip()
            data.append(
                [
                    "https://www.royrogersrestaurants.com/",
                    pagelink,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    country,
                    "<MISSING>",
                    phone,
                    "<MISSING>",
                    lat,
                    lng,
                    HOO,
                ]
            )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
