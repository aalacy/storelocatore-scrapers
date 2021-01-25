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
    base_url = "https://houseofjerky.com"
    res = session.get("https://houseofjerky.com/contact-us/store-locations/")
    soup = bs(res.text, "lxml")
    store_list = soup.select("div.post-content p")[1:]
    data = []
    for store in store_list:
        if "coming soon" in store.text:
            continue
        if "House of Jerky".lower() not in store.text.lower():
            continue
        detail = store.text.split("\n")
        while True:
            try:
                detail.remove("")
            except:
                break
        location_name = detail[0].replace("’", "")
        try:
            page_url = store.select_one("a")["href"]
        except:
            page_url = "<MISSING>"
        if page_url != "<MISSING>" or location_name == "Hilton Head House of Jerky":
            detail = detail[:-1]
        address_detail = detail.pop().replace("\xa0", " ")
        if len(address_detail.split(", ")) == 1:
            address_detail = address_detail.split(" ")
            zip = address_detail.pop()
            state = address_detail.pop()
            city = " ".join(address_detail) if len(address_detail) > 0 else "<MISSING>"
            if state == "York":
                state = "New York"
                city = "NY"
        elif len(address_detail.split(", ")) == 2:
            state_zip = address_detail.split(", ").pop().split(" ")
            city = address_detail.split(", ")[0]
            zip = state_zip.pop()
            state = " ".join(state_zip)
        else:
            city = address_detail.split(", ")[0]
            state = address_detail.split(", ")[1]
            zip = address_detail.split(", ")[2]
        city = city.replace("ñ", "n")
        state = state[:-1] if state.endswith(".") else state
        street_address = " ".join(detail[1:]).replace("\n", "").replace("’", "")
        location_type = "<MISSING>"
        country_code = "US"
        phone = "<MISSING>"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"
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
