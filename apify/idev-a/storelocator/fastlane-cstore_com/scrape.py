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
    base_url = "http://fastlane-cstore.com"
    page_url = "http://fastlane-cstore.com/locations.html"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    }
    res = session.get(page_url, headers=headers)
    soup = bs(res.text, "lxml")
    store_list = soup.select("table[width='530'] tr")[4:]
    data = []
    idx = 0
    location_type = "Convenience Stores"
    while True:
        if idx == len(store_list):
            break
        if location_type == "Hotels":
            break
        if store_list[idx].text.replace("\n", "").replace("\xa0", "").strip() == "":
            idx += 1
            continue
        try:
            location_name = store_list[idx].select_one("b").string
        except:
            try:
                location_name = (
                    store_list[idx].select_one("strong").string.replace("’", "'")
                )
            except:
                location_type = (
                    store_list[idx]
                    .select_one("font")
                    .string.replace("\n", " ")
                    .replace("                ", " ")
                )
                idx += 1
                continue
        if "Phone:" in store_list[idx + 1].text:
            detail = store_list[idx + 1].text.split("Phone:")
        else:
            detail = store_list[idx + 1].text.split("Phone/")
        address = detail[0].split("\n")
        while True:
            try:
                address.remove("")
            except:
                break
        address_detail = address.pop().strip()
        city = address_detail.split(", ")[0]
        state = address_detail.split(", ")[1].split(" ")[0]
        state = state[:-1] if state.endswith(".") else state
        zip = address_detail.split(", ")[1].split(" ")[1]
        street_address = ""
        for x in address:
            street_address += x.strip() + " "
        street_address = street_address.replace("Address: ", "")
        country_code = "US"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"
        phone = detail[1].split("\n")[2][0:14].replace("\xa0", "")
        phone = "<MISSING>" if phone == "" else phone
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

        idx += 2
    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
