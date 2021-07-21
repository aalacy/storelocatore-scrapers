import csv

from bs4 import BeautifulSoup

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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    base_link = "https://www.uniqlo.cn/shop/shop_list.html"
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    raw_codes = base.find(id="global-scripts").find_all("link")
    c_codes = []
    skip = ["X", "DEFAULT"]
    locator_domain = "uniqlo.com"

    for i in raw_codes:

        try:
            c_code = i["hreflang"].replace("en", "eu").split("-")[1]
            if c_code.upper() in skip:
                continue
            c_codes.append([c_code, i["hreflang"]])
        except:
            continue

    c_codes.append(["eu", "en"])

    for i in c_codes:
        c_code = i[0]
        api_link = (
            "https://store.fastretailing.com/api/"
            + c_code
            + "/uniqlo/200/getStoreList.json?r=storelocator"
        )
        stores = session.get(api_link, headers=headers).json()["result"]["stores"]

        for store in stores:
            location_name = store["store_name"]
            if len(location_name.strip()) <= 2:
                location_name = "<MISSING>"
            street_address = store["number"]
            if not street_address:
                street_address = store["address"]
                if not street_address:
                    street_address = "<MISSING>"
            city = store["municipality"]
            state = store["area1_name"]
            zip_code = store["postcode"]
            country_code = store["country_name_short"]
            store_number = store["store_id"]
            if store_number in skip:
                continue
            skip.append(store_number)
            location_type = "<MISSING>"
            phone = store["phone"]

            if "permanently closed" in store["open_hours"].lower():
                continue

            if "temporarily closed" in store["open_hours"].lower():
                hours_of_operation = store["open_hours"]
            else:
                hours_of_operation = (
                    "Mon "
                    + store["mon_open_at"]
                    + "-"
                    + store["mon_close_at"]
                    + " Tue "
                    + store["tue_open_at"]
                    + "-"
                    + store["tue_close_at"]
                    + " Wed "
                    + store["wed_open_at"]
                    + "-"
                    + store["wed_close_at"]
                    + " Thu "
                    + store["thu_open_at"]
                    + "-"
                    + store["thu_close_at"]
                    + " Fri "
                    + store["fri_open_at"]
                    + "-"
                    + store["fri_close_at"]
                    + " Sat "
                    + store["sat_open_at"]
                    + "-"
                    + store["sat_close_at"]
                    + " Sun "
                    + store["sun_open_at"]
                    + "-"
                    + store["sun_close_at"]
                ).strip()

            if hours_of_operation == "Mon - Tue - Wed - Thu - Fri - Sat - Sun -":
                try:
                    hours_of_operation = (
                        store["open_hours"].split("peration")[1].split("\n")[0].strip()
                    )
                    if "Mon" in hours_of_operation:
                        hours_of_operation = hours_of_operation[
                            hours_of_operation.find("Mon") - 1 :
                        ].strip()
                except:
                    hours_of_operation = "<MISSING>"
            hours_of_operation = hours_of_operation.replace(" -", " Closed")
            latitude = store["lat"]
            longitude = store["lon"]
            if not longitude:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            if state == "Kuala Lumpur" and latitude == "<MISSING>":
                continue
            link = (
                "https://map.uniqlo.com/"
                + country_code.lower()
                + "/"
                + i[1].split("-")[0]
                + "/detail/"
                + str(store_number)
            )
            # Store data
            store = [
                locator_domain,
                link,
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
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
