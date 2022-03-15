import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("raymondjames_com")
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://www.raymondjames.com/"
    addresses = []
    headers = {
        "Accept": "* / *",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }

    params = {"radius": 99999, "location": 96734}

    result = session.get(
        "https://www.raymondjames.com/dotcom/api/searchbranches",
        params=params,
        headers=headers,
    ).json()

    page = result["page"]
    total_pages = result["totalPages"]

    while page <= total_pages:
        logger.info(f"{page}/{total_pages}")
        params["page"] = page

        result = session.get(
            "https://www.raymondjames.com/dotcom/api/searchbranches",
            params=params,
            headers=headers,
        ).json()

        page += 1
        json_data = result["results"]

        for result in json_data:
            location_name = result["header"]
            if result["subHeaders"] is None:
                location_name = result["header"]
            else:
                location_name1 = result["header"]
                location_name2 = "".join(result["subHeaders"])
                ln = location_name1, location_name2
                location_name = " ".join(ln)
            if (
                result["address"]["line2"] is None
                and result["address"]["line3"] is None
            ):
                street_address = result["address"]["line1"]

            if (
                result["address"]["line2"] is not None
                and result["address"]["line3"] is None
            ):
                street1 = result["address"]["line1"]
                street2 = "".join(result["address"]["line2"])
                street12 = street1, street2
                street_address = " ".join(street12)

            if (
                result["address"]["line1"] is not None
                and result["address"]["line2"] is not None
                and result["address"]["line3"]
            ):
                street1 = result["address"]["line1"]
                street2 = result["address"]["line2"]
                street3 = result["address"]["line3"]
                street123 = street1, street2, street3
                street_address = " ".join(street123)

            if result["address"]["city"] is None:
                city = "<MISSING>"
            else:
                city = result["address"]["city"]
            if result["address"]["state"] is None:
                state = "<MISSING>"
            else:
                state = result["address"]["state"]

            if result["address"]["zip"] is None:
                zipp = "<MISSING>"
            else:
                zipp = result["address"]["zip"]

            if result["address"]["latitude"] is None:
                latitude = "<MISSING>"
            else:
                latitude = result["address"]["latitude"]
            if result["address"]["longitude"] is None:
                longitude = "<MISSING>"
            else:
                longitude = result["address"]["longitude"]
            if result["phone"] is None:
                phone = "<MISSING>"
            else:
                phone = result["phone"]

            hours_of_operation = "<MISSING>"
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("Raymond James Financial Services")
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append("<MISSING>")
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
