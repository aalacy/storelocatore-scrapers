import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("luckysupermarkets_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-csrf-token": "pUPBnuvR1AwYgZDIAoStxvE22I0b9UAJZBJfSbssh5c",
    "cookie": "__cfduid=dbe0dd2d9d2a5e7ab828da58496e7df921605194864; has_js=1; _ga=GA1.2.1455690690.1605194885; _gid=GA1.2.1225523054.1605194885; _fbp=fb.1.1605194886804.831749390; SSESS2ae72b531fe45e3e644af8b82a2a8a0a=LnUFAAap0U426lC2sJn2qpvhQdb_q7tgN1ZJHgdshoc; Srn-Auth-Token=7d130072b0e0089900b0fc8ac0bde2fc296cb7398fba59ab0bdfb4e17cc25ba0; XSRF-TOKEN=pUPBnuvR1AwYgZDIAoStxvE22I0b9UAJZBJfSbssh5c; __zlcmid=118ja2CvTKtGghG; session=1605199629727.xgi41b7; _gat_UA-104489120-1=1; _gat_UA-102256819-2=1",
}


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
    # Your scraper here
    data = []
    url = "https://www.luckysupermarkets.com/api/m_store_location?store_type_ids=1,2,3"
    loclist = session.get(url, headers=headers, verify=False).json()["stores"]
    daylist = {
        0: "Sunday",
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
    }
    for loc in loclist:
        title = loc["storeName"]
        store = loc["store_number"]
        street = loc["address"]
        city = loc["city"]
        state = loc["state"]
        pcode = loc["zip"]
        ccode = loc["country"]
        lat = loc["latitude"]
        longt = loc["longitude"]
        phone = loc["phone"]
        hour_list = loc["store_hours"]
        hours = ""
        for hr in hour_list:
            day = daylist[hr["day"]]
            start = hr["open"]
            close = hr["close"]
            hours = hours + day + " " + start + " - " + close + " "
        data.append(
            [
                "https://www.luckysupermarkets.com/",
                "https://www.luckysupermarkets.com/stores/",
                title,
                street,
                city,
                state,
                pcode,
                ccode,
                store,
                phone,
                "<MISSING>",
                lat,
                longt,
                hours,
            ]
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
