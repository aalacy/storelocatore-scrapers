import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

base_url = "https://www.lunchboxwax.com"
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    output_list = []
    url = "https://www.lunchboxwax.com/salons/"
    request = session.get(url)
    soup = BeautifulSoup(request.text, "html.parser")
    data_list = soup.find("div", {"class", "acf-map"})
    data_list = soup.findAll("div", {"class", "marker"})

    for data in data_list:
        latitude = data["data-lat"]
        longitude = data["data-lng"]

        title = data.find("p", {"class", "locationName"}).text
        phone = data.find("p", {"class", "locPhone"}).text
        sublink = data.find("a", {"class", "btn primary-btn"}).get("href")
        subrequest = session.get(sublink)
        subsoup = BeautifulSoup(subrequest.text, "html.parser")
        hours_of_operation = (
            subsoup.find("div", {"class", "hidden-hours"})
            .text.replace("\t", " ")
            .replace("\n", " ")
            .lstrip()
            .rstrip()
            .replace("     ", ", ")
        )
        add = subsoup.find("li", {"class", "location__list-item address-list-item"})
        add = add.findAll("span")
        str_add = add[0].text
        city = add[1].text
        state = add[2].text
        postalCode = add[3].text
        output_list.append(
            [
                base_url,
                sublink,
                title,
                str_add,
                city,
                state,
                postalCode,
                "US",
                "<MISSING>",
                phone,
                "Salon",
                latitude,
                longitude,
                hours_of_operation.replace("\n", " "),
            ]
        )
    return output_list


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
