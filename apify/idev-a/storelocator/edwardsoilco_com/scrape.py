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
    base_url = "http://edwardsoilco.com"
    res = session.get("http://edwardsoilco.com/store-locations")
    store_list = res.text.split("var marker = ")[2:]
    data = []
    for store in store_list:
        detail = (
            store.split(");")[0]
            .replace("createTabbedMarker(", "")
            .replace("\t", "")
            .replace("\r\n", "")
            .split("','")
        )
        page_url = bs(detail[6], "lxml").select_one("a")["href"]
        page_url = page_url if "http" in page_url else base_url + page_url
        res = session.get(page_url, verify=False)
        soup = bs(res.text, "lxml")
        location_name = (
            soup.select_one("h2[itemprop='name']")
            .string.replace("\n", "")
            .replace("\t", "")
        )
        contents = soup.select_one("table.detailssingle td").contents
        table_data = []
        for x in contents:
            if x.string is not None and x.string != "\n":
                table_data.append(x.string)
        table_data = table_data[:-1]
        street_address = table_data[0]
        city = table_data[1].split(", ")[0]
        state = table_data[1].split(", ").pop().split(" ")[0]
        zip = table_data[1].split(", ").pop().split(" ").pop()
        try:
            phone = table_data[2].replace("Phone", "").replace(":", "").strip()
        except:
            phone = "<MISSING>"
        phone = "<MISSING>" if "Get" in phone else phone
        country_code = "US"
        store_number = detail[0][1:]
        location_type = "<MISSING>"
        geo = detail[4].split("LatLng(")[1].split(")")[0]
        latitude = geo.split(",")[0]
        longitude = geo.split(",")[1]

        hours = table_data[3:]
        hours_of_operation = ""
        for x in hours:
            hours_of_operation += (
                ""
                if x.string is None
                else x.replace("\xa0", "").replace("\n", "") + " "
            )
        hours_of_operation = hours_of_operation.strip()
        hours_of_operation = (
            "<MISSING>"
            if hours_of_operation == ""
            else hours_of_operation.replace("Store Hours:", "").strip()
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
