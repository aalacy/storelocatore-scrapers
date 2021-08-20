import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("originaljoes_ca")

session = SgRequests()

headers = {
    "authority": "spreadsheets.google.com",
    "method": "GET",
    "path": "/feeds/list/1hlS5TSu2fWJ11Am9yAPmC34HRaplWmhmr-qrpDEquQw/1/public/values?alt=json",
    "scheme": "https",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "origin": "https://www.originaljoes.ca",
    "referer": "https://www.originaljoes.ca/",
    "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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
    url = "https://spreadsheets.google.com/feeds/list/1hlS5TSu2fWJ11Am9yAPmC34HRaplWmhmr-qrpDEquQw/1/public/values?alt=json"
    stores_req = session.get(url, headers=headers).json()
    for store in stores_req["feed"]["entry"]:
        title = store["gsx$storename"]["$t"]
        streetno = store["gsx$streetnumber"]["$t"]
        streetad = store["gsx$street"]["$t"]
        street = streetno + " " + streetad
        city = store["gsx$city"]["$t"]
        state = store["gsx$province"]["$t"]
        pcode = store["gsx$postalcode"]["$t"]
        lng = store["gsx$longitude"]["$t"]
        lat = store["gsx$latitude"]["$t"]
        phone = store["gsx$phonenumber"]["$t"]
        hoo = store["gsx$hours"]["$t"]
        storeid = store["gsx$storenumber"]["$t"]
        street = street.replace("&#039;", "'")
        title = title.replace("&#039;", "'")
        link = (
            "https://www.originaljoes.ca/en/locations/"
            + storeid
            + "/"
            + streetad
            + ".html"
        )
        link = link.replace(" ", "-")
        link = link.replace("--", "-")
        hoo = hoo.strip()
        hoo = hoo.split("\n")
        if len(hoo) > 2:
            hours = hoo[0] + " " + hoo[1]
        else:
            hours = hoo[0]
        if hours == "CLOSED FOR : RENOVATIONS":
            hours = "TEMPORARILY CLOSED"

        if hours == "TEMPORARILY: CLOSED":
            hours = "TEMPORARILY CLOSED"

        if hours == "TEMPORARILY : CLOSED":
            hours = "TEMPORARILY CLOSED"

        if (
            hours
            == "MON-SUN: ., Dine-In, Takeout & Delivery:: 11AM-10PM, Delivery Only: : 10PM-11PM"
        ):
            hours = "MON-SUN: 11AM-10PM"

        hours = hours.replace("., Dine-In, Takeout & Delivery:: ", "")
        hours = hours.replace("<br>", "").strip()

        if hours.find("HAPPY HOUR") != -1:
            hours = hours.split("HAPPY HOUR")[0].strip()
        else:
            hours = hours

        if link != "https://www.originaljoes.ca/en/locations//.html":
            data.append(
                [
                    "https://originaljoes.ca/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "CAN",
                    storeid,
                    phone,
                    "<MISSING>",
                    lat,
                    lng,
                    hours,
                ]
            )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
