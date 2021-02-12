import csv
import json
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
    base_url = "https://www.originalmattress.com/"

    res1 = session.get("https://www.originalmattress.com/find-a-store")
    store_list = json.loads(
        res1.text.split('type="hidden" data-mapmarkers="')[1]
        .split('" />')[0]
        .replace("&quot;", '"')
    )
    data = []
    for store in store_list:
        page_url = base_url + store["UrlSlug"]
        store_number = store["Id"]
        location_name = store["Name"].replace("&amp;", "&")
        location_type = (
            "Factory & Store" if "Factory & Store" in location_name else "Store"
        )
        latitude = store["Latitude"]
        longitude = store["Longitude"]
        contents = (
            store["ShortDescription"]
            .replace("&gt;", ">")
            .replace("&lt;", "<")
            .replace("NOW OPEN:", "")
            .replace("Next to Trader Joe’s", "")
        )
        if "Phone:" in bs(contents, "lxml").text:
            phone = (
                bs(contents, "lxml")
                .text.split("Phone:")[1]
                .split("\n")[0]
                .replace("\xa0", "")
            )
        else:
            phone = (
                bs(contents, "lxml")
                .text.split("Phone number:")[1]
                .split("\n")[0]
                .replace("\xa0", "")
            )

        try:
            hours = (
                bs(contents, "lxml")
                .text.lower()
                .split("store hours:")[1]
                .split("\nhigh")
            )
            hours[:] = [x for x in hours if x]
            hours_of_operation = hours[0].replace("\n", "").split("phone")[0]
        except:
            hours_of_operation = (
                bs(contents, "lxml").text.lower().split("8\n")[1].split("\n")[0]
            )
        hours_of_operation = hours_of_operation.replace("\xa0", "")

        contents = contents.split(">")
        contents_data = []
        for x in contents:
            content = x.split("<")
            contents_data.append(
                content[0]
                .replace("\r\n", "")
                .replace(",", " ")
                .replace("&#160;", "")
                .strip()
            )
        contents_data[:] = [x for x in contents_data if x]
        contents_data = (
            "/".join(contents_data)
            .split("Store hours:")[0]
            .split("Phone")[0]
            .split("/")[:-1]
        )

        tmp = "/ ".join(contents_data).split(" ")
        tmp[:] = [x for x in tmp if x]
        zip = tmp.pop()
        if len(zip) == 7:
            state = zip[:2]
            zip = zip[2:]
        else:
            state = tmp.pop().replace("/", "")
        contents_data = " ".join(tmp).strip().split("/")
        contents_data[:] = [x for x in contents_data if x]

        city = contents_data.pop()
        street_address = " ".join(contents_data).replace("&#39;", "'")

        country_code = "US"

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
