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
    base_url = "https://formanmills.com/"
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "cache-control": "max-age=0",
        "cookie": "current_date=2021-1-18 13:53:0; _ga=GA1.2.496098882.1610959724; _gid=GA1.2.1745264377.1610959724; _fbp=fb.1.1610959729860.990200720; btpdb.1PR3l09.dGZjLjc0ODMzMDQ=U0VTU0lPTg; btpdb.1PR3l09.dGZjLjc0ODMxOTQ=U0VTU0lPTg; calltrk_referrer=direct; calltrk_landing=https%3A//formanmills.com/; calltrk_session_id=d3a45bc4-5218-48e3-b1ab-d8c1f57c5edc; __gads=ID=c90326b73e6bfce1-225c8791adc500c3:T=1610959802:RT=1610959802:S=ALNI_MbBXVkok7VDPpYeT1YkVWgv4bmcAQ; _gat_gtag_UA_11589974_2=1; __atuvc=3%7C3; __atuvs=6005d90beed699d7000",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    }
    res = session.get("https://formanmills.com/stores/", headers=headers)
    soup = bs(res.text, "lxml")
    store_list = eval(
        res.text.split("var loc =")[1]
        .split("var locations")[0]
        .replace("\n", "")
        .strip()[:-1]
    )
    data = []
    for store in store_list:
        detail = bs(store[0], "lxml")
        page_url = detail.select_one("h3 a")["href"]
        location_name = detail.select_one("h3 a").string
        location_name = (
            location_name.split(":")[0]
            if ":" in location_name
            else location_name.split("*")[0]
        )
        phone = detail.select_one("div.telephone").string
        details = detail.select("ul li")
        address = details.pop().string
        city = address.split(", ")[0]
        zip = address.split(", ")[1].split(" ")[1]
        state = address.split(", ")[1].split(" ")[0]
        street_address = ""
        for x in details:
            street_address += " " if x.string is None else x.string + " "
        street_address = street_address.strip()
        country_code = "US"
        store_number = store[3]
        location_type = "<MISSING>"
        latitude = store[1]
        longitude = store[2]
        res = session.get(page_url, headers=headers)
        soup = bs(res.text, "lxml")
        hours_of_operation = (
            soup.select_one("div.hours ul")
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
