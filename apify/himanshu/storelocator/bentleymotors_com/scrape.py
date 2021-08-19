import csv
from sgrequests import SgRequests
import unicodedata
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("bentleymotors_com")
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses1 = []
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    r = session.get(
        "https://www.bentleymotors.com/en/apps/dealer-locator/_jcr_content.api.jsonx",
        headers=headers,
    )
    api_id = r.url.split("api.")[1].split(".json")[0]
    location_list = r.json()["dealers"]
    for location in location_list:
        if location["countryId"] not in ["US", "CA"]:
            continue
        location_request = session.get(
            "https://www.bentleymotors.com/content/brandmaster/global/bentleymotors/en/apps/dealer-locator/jcr:content.dealersinfo.api.suffix."
            + api_id
            + ".json/"
            + location["dealerId"]
            + "/dlr.json?ak=1"
        )
        store_data = location_request.json()
        addresses = store_data["addresses"]
        for address in addresses:
            store = []
            store.append("https://www.bentleymotors.com")
            store.append(store_data["dealerName"].strip())
            store.append(
                address["street"].strip() + address["secondLine"].strip()
                if "secondLine" in address
                else address["street"].strip()
            )
            if store[-1].count(",") == 2:
                store[-1] = store[-1].split(",")[0]
            store.append(address["city"].strip())
            store.append(address["county"].strip().replace("Washington", "WA"))
            store.append(address["postcode"].strip())
            store.append(store_data["countryId"].strip())
            store.append(address["id"].strip())
            phone = ""
            for department in address["departments"]:
                if phone == "" and "phone" in department:
                    if department["phone"]:
                        phone = department["phone"]
            store.append(phone.strip() if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(address["gcj02"]["lat"].strip())
            store.append(address["gcj02"]["lng"].strip())
            hours = ""
            for department in address["departments"]:
                if department["openingHours"] == []:
                    continue
                hours = hours + " " + department["name"]
                for hour in department["openingHours"]:
                    if hour["periods"] == []:
                        hours = hours + " " + hour["day"] + " "
                    else:
                        hours = (
                            hours
                            + " "
                            + hour["day"]
                            + " "
                            + hour["periods"][0]["open"]
                            + "-"
                            + hour["periods"][0]["close"]
                        )
            store.append(
                hours.strip()
                .split("pre-owned")[0]
                .replace("sales", "")
                .split("  service")[0]
                .replace("0 Sunday  ", "0 Sunday closed")
                if hours
                else "<MISSING>"
            )
            try:
                page_url = "https://www." + addresses[0]["departments"][0][
                    "website"
                ].replace("www.", "")
            except:
                try:
                    page_url = "https://www." + store_data["website"]
                except:
                    page_url = "<MISSING>"

            store.append(page_url.strip())

            for i in range(len(store)):
                if isinstance(store[i], str):
                    store[i] = "".join(
                        (
                            c
                            for c in unicodedata.normalize("NFD", store[i])
                            if unicodedata.category(c) != "Mn"
                        )
                    )
            if store[2] in addresses1:
                continue
            addresses1.append(store[2])
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
