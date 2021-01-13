from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("petfoodexpress_com")

session = SgRequests()
headers = {
    "authority": "api.petfood.express",
    "method": "GET",
    "path": "/store/pickup",
    "scheme": "https",
    "accept": "text/plain, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "text/html",
    "if-modified-since": "Mon, 11 Jan 2021 18:03:11 GMT",
    "origin": "https://www.petfood.express",
    "referer": "https://www.petfood.express/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "x-api-key": '{"key":"ZmQ5OWU4NGMtYTY5YS00MWExLTg1NzktNGMzYWVlMDMzYjRk","fibonacciKey":"931295","jwt":null}',
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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
        temp_list = []  # ignoring duplicates
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
    url = "https://api.petfood.express/store/map/"
    response = session.get(url, headers=headers, verify=False).json()
    for r in response:
        lat = r["latitude"]
        lng = r["longitude"]
        phone = r["storePhone"]
        title = r["storeName"]
        storeid = r["storeNumber"]
        street = r["storeAddress"]
        city = r["storeCity"]
        state = "CA"
        pcode = r["storeZip"]
        url2 = "https://api.petfood.express/store/details/" + storeid
        p = session.post(url2, headers=headers, verify=False)
        soup = BeautifulSoup(p.text, "html.parser")
        timelist = soup.findAll("p")
        HOO = timelist[1].text.strip()

        data.append(
            [
                "https://www.petfood.express/",
                url2,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                storeid,
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
