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
    base_url = "https://www.fuddruckers.com"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Cookie": "X-Mapping-dminehmk=7EC7D8751E8584FEFB379FCDB04A77DB; PHPSESSID=fda2c3d8271b62047bbd7667a8a08023; _ga=GA1.2.1924389010.1610013785; _gid=GA1.2.276444203.1610013785; _gcl_au=1.1.321468607.1610013786",
        "Host": "www.fuddruckers.com",
        "Referer": "https://www.fuddruckers.com/",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }
    res = session.get("https://www.fuddruckers.com/locations", headers=headers)

    store_info = json.loads(res.text.split("LOCLIST = ")[1].split(";")[0])

    store_numbers = []

    for x in store_info.keys():
        regions = store_info[x]
        for key in regions.keys():
            if key == "Mexico" or key == "Panama":
                continue

            region = regions[key]
            store_numbers += region

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Length": "53",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": "X-Mapping-dminehmk=7EC7D8751E8584FEFB379FCDB04A77DB; PHPSESSID=fda2c3d8271b62047bbd7667a8a08023; _ga=GA1.2.1924389010.1610013785; _gid=GA1.2.276444203.1610013785; _gcl_au=1.1.321468607.1610013786; _gat=1",
        "Host": "www.fuddruckers.com",
        "Origin": "https://www.fuddruckers.com",
        "Referer": "https://www.fuddruckers.com/locations",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    res = session.post(
        "https://www.fuddruckers.com/services/location/get_stores_by_numbers.php",
        data={"s": json.dumps(store_numbers)},
        headers=headers,
    )
    store_list = json.loads(res.text)["places"]["keywords"]["data"]
    data = []

    for store in store_list:
        if store["comingsoon"] or store["hours"] == "Closed":
            continue
        page_url = "https://www.fuddruckers.com" + store["link"]
        res = session.get(page_url)
        soup = bs(res.text, "lxml")

        location_name = store["storename"]
        street_address = store["address"]
        city = store["city"]
        zip = "<MISSING>" if "PA" in store["country"] else store["zip"]
        state = store["state"]
        country_code = store["country"]
        latitude = store["lat"]
        longitude = store["lng"]
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store["phone"].replace("x35063", "")
        hours_of_operation = soup.select_one(".store-hours").text.replace("\n", "")

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
