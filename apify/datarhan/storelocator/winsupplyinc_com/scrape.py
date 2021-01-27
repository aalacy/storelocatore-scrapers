import csv
import json
import time
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []
    scraped_items = []

    DOMAIN = "winsupplyinc.com"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=200,
        max_search_results=None,
    )

    post_url = "https://www.winsupplyinc.com/rest/model/com/ws/supplier/SupplierActor/searchAdditionalSupplier?{}"
    body = '{"location":"10001","distance":"250","industryType":"","showroomOnly":false,"_dynSessConf":""}'
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    response = session.post(
        post_url.format(str(int(time.time() * 1000))), headers=headers, data=body
    )

    body = '{"location":"10001","distance":"250","industryType":"","showroomOnly":false,"_dynSessConf":"%s"}'
    response = session.get(
        "https://www.winsupplyinc.com/rest/model/atg/rest/SessionConfirmationActor/getSessionConfirmationNumber",
        headers=headers,
    )
    session_data = json.loads(response.text)
    session_no = session_data["sessionConfNo"]
    headers["Content-Type"] = "application/json"

    for code in all_codes:
        body = '{"location":"%s","distance":"250","industryType":"","showroomOnly":false,"_dynSessConf":"%s"}'
        response = session.post(
            post_url.format(str(int(time.time() * 1000))),
            headers=headers,
            data=body % (code, session_no),
        )
        data = json.loads(response.text)

        if not data.get("additionalSupplier"):
            continue

        for poi in data["additionalSupplier"]:
            store_url = "https://www.winsupplyinc.com" + poi["seoURL"]
            location_name = poi["displayName"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address1"]
            if poi["address2"]:
                street_address += ", " + poi["address2"]
            if poi["address3"]:
                street_address += ", " + poi["address3"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["city"]
            city = city if city else "<MISSING>"
            state = poi["state"]
            state = state if state else "<MISSING>"
            zip_code = poi["postalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["country"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["id"]
            store_number = store_number if store_number else "<MISSING>"
            phone = poi["phone"]
            phone = phone if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = poi["latitude"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["longitude"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = " ".join(poi["timings"])

            item = [
                DOMAIN,
                store_url,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
            if store_number not in scraped_items:
                scraped_items.append(store_number)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()


hdr = {
    "authority": "www.winsupplyinc.com",
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
    "content-type": "application/json",
    "cookie": "BIGipServerorigin_prod=303169802.20480.0000; rxVisitor=16071916149854JST89CK49VG5PBOCK7134ILNF7TFJVC; _ga=GA1.2.80294118.1607191617; __auc=c84dd6231763415e7b3c3d1188e; dtSa=-; _gid=GA1.2.1487140172.1607334507; JSESSIONID=TSE8zklXws_EJ1-s-8-S-98D4tMSnndgvYjE2XIU4BpYzOq4L27B!793648615; _gat=1; __asc=57314b9a1763cce50c75056b9da; dtCookie=v_4_srv_3_sn_C36FEEFA25E4840B524DB33205FD55E7_perc_100000_ol_0_mul_1; dtLatC=4; rxvt=1607339756231|1607336305512; dtPC=3$537927365_149h11vTNMKEAFMCQELCPNSKUMIOCTWARMDFODC-0e3",
    "origin": "https://www.winsupplyinc.com",
    "referer": "https://www.winsupplyinc.com/location-finder",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "x-dtpc": "3$537927365_149h11vTNMKEAFMCQELCPNSKUMIOCTWARMDFODC-0e3",
}
