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
    base_url = "https://www.hamricks.com"
    res = session.get("https://www.hamricks.com/store-locator")
    soup = bs(res.text, "lxml")
    state_list = soup.select("select#State option")
    data = []
    for state_link in state_list:
        link = state_link["data-href"]
        page_url = "https://www.hamricks.com/store-locator"
        res1 = session.get(link)
        soup1 = bs(res1.text, "lxml")
        store_list = soup1.select("div.FaqWrap")
        if len(store_list) == 0:
            store = soup1.select_one("div.DetailInfo")
            location_name = (
                store.select_one("h3").text.replace("\n", "").replace("\t", "").strip()
            )
            contents = store.select_one("div.FParagraph1.Desc").text.split("\n")
            address = []
            for x in contents:
                tmp = x.replace("\t", "").replace("\r", "").strip()
                if tmp != "":
                    address.append(tmp)
            detail = address.pop()
            city = detail.split(", ")[0]
            zip = detail.split(", ")[1].split(" ").pop()
            state = " ".join(detail.split(", ")[1].split(" ")[:-1])
            street_address = address.pop().replace("•", "•")
            phone = (
                store.select_one("div.StoreInfo")
                .text.replace("\n", "")
                .replace("\t", "")
                .strip()
            )
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            latitude = store.select_one("a")["href"].split("@")[1].split(",")[0]
            longitude = store.select_one("a")["href"].split("@")[1].split(",")[1]
            hours_of_operation = (
                store.select("div.StoreInfo")[1]
                .text.replace("\t", "")
                .replace("\n", " ")
                .replace("\r", "")
                .strip()
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
        else:
            for store in store_list:
                location_name = (
                    store.select_one("div.FaqTitle").text.replace("\n", "").strip()
                )
                contents = store.select_one("div.FParagraph1.Desc").text.split("\n")
                address_detail = []
                for x in contents:
                    tmp = x.replace("\t", "").replace("\r", "").strip()
                    if tmp != "":
                        address_detail.append(tmp)
                contact_idx = 0
                for x in address_detail:
                    contact_idx += 1
                    if len(x) == 12:
                        break
                address = address_detail[:contact_idx]
                phone = address.pop()
                detail = address.pop()
                city = detail.split(", ")[0]
                zip = detail.split(", ")[1].split(" ").pop()
                state = " ".join(detail.split(", ")[1].split(" ")[:-1])
                street_address = address.pop().replace("•", ".")
                country_code = "<MISSING>"
                store_number = "<MISSING>"
                location_type = "<MISSING>"
                latitude = store.select_one("a")["href"].split("@")[1].split(",")[0]
                longitude = store.select_one("a")["href"].split("@")[1].split(",")[1]
                hours_of_operation = (
                    store.select("div.StoreInfo")[1]
                    .text.replace("\t", "")
                    .replace("\n", " ")
                    .replace("\r", "")
                    .strip()
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
