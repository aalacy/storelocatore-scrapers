import csv

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

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }
    base_url = "https://www.ebgames.ca/StoreLocator/GetStoresForStoreLocatorByProduct?value=&skuType=0&language=en-CA"

    phone = []
    lat = ""
    log = ""
    return_main_object = []
    k = session.get(base_url, headers=headers).json()

    for i in k:
        tem_var = []

        name = i["Name"]
        if "CLOSED -" in name.strip():
            continue

        st = i["Address"]
        lat = i["Latitude"]
        log = i["Longitude"]
        postal = i["Zip"].replace("R2C IJ2", "R2C 4J2")

        if len(postal) != 5:
            country = "CA"
        else:
            country = "US"

        state = i["Province"]
        city = i["City"]
        phone1 = i["Phones"]

        if "Please call this store for operating hours." in i["Hours"]:
            hours = "<MISSING>"
        else:
            hours = i["Hours"].replace("<br>", " ").replace("br>", " ")

        if len(phone1) == 1:
            phone = "<MISSING>"
        else:
            phone = phone1

        tem_var.append("https://www.ebgames.ca")
        tem_var.append(name.replace("\x8f", ""))
        tem_var.append(st.replace("\x8f", ""))
        tem_var.append(city.replace("\x8f", "").replace("undefined", "<MISSING>"))
        tem_var.append(state.replace("\x8f", "").replace("undefined", "<MISSING>"))
        tem_var.append(postal.replace("\x8f", "").replace("_", ""))
        tem_var.append(country)
        tem_var.append("<MISSING>")
        tem_var.append(phone.replace("\x8f", "").replace("undefined", "<MISSING>"))
        tem_var.append("<MISSING>")

        tem_var.append(lat.replace("undefined", "<MISSING>"))
        tem_var.append(log.replace("undefined", "<MISSING>"))
        tem_var.append(hours.replace("\x8f", ""))
        tem_var.append("https://www.ebgames.ca/storelocator")
        return_main_object.append(tem_var)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
