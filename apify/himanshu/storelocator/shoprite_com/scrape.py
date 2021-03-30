import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

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
    base_url = "https://shoprite.com/"
    headers = {
        "accept": "*/*",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    payload = "Region=&SearchTerm=21216&FilterOptions%5B0%5D.IsActive=false&FilterOptions%5B0%5D.Name=Online+Grocery+Delivery&FilterOptions%5B0%5D.Value=MwgService%3AShop2GroDelivery&FilterOptions%5B1%5D.IsActive=false&FilterOptions%5B1%5D.Name=Online+Grocery+Pickup&FilterOptions%5B1%5D.Value=MwgService%3AShop2GroPickup&FilterOptions%5B2%5D.IsActive=false&FilterOptions%5B2%5D.Name=Platters%2C+Cakes+%26+Catering&FilterOptions%5B2%5D.Value=MwgService%3AOrderReady&FilterOptions%5B3%5D.IsActive=false&FilterOptions%5B3%5D.Name=Pharmacy&FilterOptions%5B3%5D.Value=MwgService%3AUmaPharmacy&FilterOptions%5B4%5D.IsActive=false&FilterOptions%5B4%5D.Name=Retail+Dietitian&FilterOptions%5B4%5D.Value=ShoppingService%3ARetail+Dietitian&Radius=50000&Take=999&Redirect="

    soup = BeautifulSoup(
        session.post(
            "https://shoprite.com/StoreLocatorSearch", headers=headers, data=payload
        ).text,
        "lxml",
    )
    for dt in soup.find_all("li", {"class": "stores__store"}):
        addr = list(dt.find("div", {"class": "store__basic"}).stripped_strings)
        location_name = addr[0]
        street_address = addr[2]
        city = addr[3].split(",")[0]
        if len(addr[3].split(",")[1].strip().split(" ")) == 3:
            state = " ".join(addr[3].split(",")[1].strip().split(" ")[:2])
            zipp = addr[3].split(",")[1].strip().split(" ")[-1]
        else:
            state = addr[3].split(",")[1].strip().split(" ")[0]
            zipp = addr[3].split(",")[1].strip().split(" ")[-1]
        phone = addr[4].replace(" ", "")
        store_number = json.loads(
            dt.find("button", {"class": "store__focusResultButton"})["data-json"]
        )["storeId"]
        coord = dt.find_all("a")[1]["href"].split("=")[1].split(",")
        latitude = coord[0].replace("0000000000", "")
        longitude = coord[1].replace("0000000000", "")
        hours_of_operation = dt.find(
            "p", {"class": "hoursAndServices__schedule storeDetails__content"}
        ).text.strip()
        page_url = dt.find("a")["href"]

        store = []
        store.append(base_url)
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append("US")
        store.append(store_number if store_number else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("ShopRite")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hours_of_operation if hours_of_operation else "<MISSING>")
        store.append(page_url)
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
