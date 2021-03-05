import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests

session = SgRequests()


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
    base_url = "https://www.selfridges.com"
    res = session.get("https://www.selfridges.com/US/en/features/info/stores/london/")
    soup = bs(res.text, "lxml")
    page_links = soup.select("ul.navigation-root a")
    links = []
    for x in page_links:
        links.append(base_url + x["href"])

    data = []
    for link in links:
        res = session.get(link)
        soup = bs(res.text, "lxml")
        store_info = soup.select(
            "div.richText.component.section.default-style.col-xs-12.col-sm-6"
        )
        page_url = link
        try:
            address_contents = (
                store_info[1].select_one("div.richText-content p").contents
            )
        except:
            store_info = soup.select(
                "div.richText.component.section.default-style.col-xs-12.col-sm-3"
            )
            address_contents = (
                store_info[1].select_one("div.richText-content p").contents
            )
        address = []
        for item in address_contents:
            if item.string is None:
                continue
            address.append(item.string)
        zip = address.pop()
        state = "<MISSING>"
        country_code = "<MISSING>"
        city = address.pop()
        street_address = ", ".join(address[1:])
        location_name = address[0]
        geo = soup.select_one(
            ".richText.component.section.col-xs-12.richtext.default-style .richText-content a.cta"
        )["href"]
        latitude = geo.split("=")[1].split(",")[0]
        longitude = geo.split("=")[1].split(",")[1]
        location_type = "<MISSING>"
        store_number = "<MISSING>"
        phone = "<MISSING>"
        hours_of_operation = ", ".join(
            store_info[0]
            .select_one("div.richText-content")
            .text.replace("\xa0", " ")
            .split("\n")[2:9]
        )
        data.append(
            [
                base_url,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zip,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
