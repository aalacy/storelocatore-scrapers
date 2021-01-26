import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("festfoods_com")

session = SgRequests()

headers = {
    "authority": "www.festfoods.com",
    "method": "GET",
    "path": "/api/stores/locations",
    "scheme": "https",
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cookie": "_ga=GA1.2.1390384036.1611617749; _gid=GA1.2.271015495.1611617749; __insp_wid=104378033; __insp_nv=true; __insp_targlpu=aHR0cHM6Ly93d3cuZmVzdGZvb2RzLmNvbS8%3D; __insp_targlpt=RmVzdGl2YWwgRm9vZHM%3D; __insp_sid=976196949; __insp_uid=3517566280; _fbp=fb.1.1611617752439.1822224673; fp-session=%7B%22token%22%3A%22a6fba605c51796af7103be22dada784e%22%7D; fp-pref=%7B%7D; __insp_msld=true; fp-history=%7B%220%22%3A%7B%22name%22%3A%22%22%7D%2C%221%22%3A%7B%22name%22%3A%22store-locator%22%7D%7D; __insp_pad=3; __insp_slim=1611617957984",
    "if-none-match": 'W/"6ebe-RjO1+liiqq8d53WkcHDW9jH1QFA"',
    "referer": "https://www.festfoods.com/my-store/store-locator",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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

        temp_list = []
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
    url = "https://www.festfoods.com/api/freshop/1/stores?sort=name&name_sort=asc&app_key=festival_foods_envano"
    r = session.get(url, headers=headers, verify=False).json()
    r = r["items"]
    for loc in r:
        ids = loc["id"].strip()
        if ids != "2240" and ids != "3322" and ids != "1955" and ids != "100":
            title = loc["name"]
            street = loc["address_1"]
            city = loc["city"]
            state = loc["state"]
            pcode = loc["postal_code"]
            lat = loc["latitude"]
            lng = loc["longitude"]
            phone = loc["phone"]
            storeid = loc["store_number"]
            link = loc["url"]

            data.append(
                [
                    "https://www.festfoods.com/",
                    link,
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
                    "<INACCESSIBLE>",
                ]
            )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
