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
    base_url = "https://www.hamleys.com"
    res = session.get("https://www.hamleys.com/find-a-store")
    soup = bs(res.text, "lxml")
    page_links = soup.select("div.find-store ul a")
    store_ids = []
    for x in page_links:
        store_ids.append(x["href"])

    data = []
    for store_id in store_ids:
        headers = {
            "accept": "*/*",
            "content-length": "22",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "cookie": 'PHPSESSID=cfd91cbd4919579ecbc54d020ca5fa66; form_key=3vGnmitjNYaPDoHn; mage-banners-cache-storage=%7B%7D; mage-cache-storage=%7B%7D; mage-cache-storage-section-invalidation=%7B%7D; mage-cache-sessid=true; mage-messages=; recently_viewed_product=%7B%7D; recently_viewed_product_previous=%7B%7D; recently_compared_product=%7B%7D; recently_compared_product_previous=%7B%7D; product_data_storage=%7B%7D; PHPSESSID=cfd91cbd4919579ecbc54d020ca5fa66; form_key=3vGnmitjNYaPDoHn; _ga=GA1.2.792531740.1610704921; _gid=GA1.2.45376347.1610704921; _fbp=fb.1.1610704924086.422481675; _hjTLDTest=1; _hjid=c3a50b1e-7c57-43ba-86ab-6cb1c8f8639a; _hjFirstSeen=1; _hjAbsoluteSessionInProgress=1; _sp_ses.fe1b=*; smc_uid=1610704935159409; smc_tag=eyJpZCI6MTk1NSwibmFtZSI6ImhhbWxleXMuY29tIn0=; smc_refresh=13184; smc_sesn=1; smc_not=default; private_content_version=c90fd986e5db7a9065440a499265516f; _uetsid=b62ee020571811eb8e6df30fa29e85fa; _uetvid=b62ef3b0571811ebb7a047247ac08a75; smc_spv=4; smc_tpv=4; smct_last_ov=[{"id":40665,"loaded":1610706257235,"open":null,"eng":null,"closed":null}]; smc_v4_40665={"timer":0,"start":1610704941651,"last":1610704941651,"disp":null,"close":null,"reset":null,"engaged":null,"active":1610706258730,"cancel":null,"fm":null}; section_data_ids=%7B%7D; _sp_id.fe1b=762307b8-9a5b-4ec2-88bb-a90e6fcef14c.1610704928.1.1610706794.1610704928.135d30fa-3546-44c7-8f07-475d257e9913; smct_session={"s":1610704936174,"l":1610706829522,"lt":1610706829523,"t":1621,"p":734}',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }
        payload = {"id": "store." + store_id}
        res = session.post(
            "https://www.hamleys.com/ajaxcms", data=payload, headers=headers
        )
        soup = bs(
            res.text.replace("\\/", "/").replace('\\"', '"').replace("\\r\\n", ""),
            "lxml",
        )
        page_url = "https://www.hamleys.com/find-a-store"
        try:
            store = json.loads(soup.select_one("div.find-store-map")["data-locations"])[
                0
            ]
            location_name = store["location_name"]
            latitude = store["position"]["latitude"]
            longitude = store["position"]["longitude"]
            zip = store["zipcode"]
            state = "<MISSING>" if store["state"] == "" else store["state"]
            country_code = store["country"]
            city = store["city"]
            street_address = store["address"]
            phone = "<MISSING>" if store["phone"] == "" else store["phone"]
            hours = soup.select("div.pagebuilder-column table tbody tr")[1:]
            hours_of_operation = ""
            for hour in hours:
                day_hours = hour.contents
                for day in day_hours:
                    hours_of_operation += day.string.strip() + " "
        except:
            location_name = "<MISSING>"
            location_name = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            zip = "<MISSING>"
            state = "<MISSING>"
            country_code = "<MISSING>"
            city = "<MISSING>"
            street_address = "<MISSING>"
            phone = "<MISSING>"
            hours_of_operation = "<MISSING>"

        location_type = "<MISSING>"
        store_number = "<MISSING>"

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
