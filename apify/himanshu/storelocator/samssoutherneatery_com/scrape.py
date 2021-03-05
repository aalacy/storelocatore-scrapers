import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    phoness = []
    addressess = []
    base_url = "http://samssoutherneatery.com"
    r = session.get(
        "https://www.ordersamssoutherneatery.com/locations", headers=headers
    )
    soup = BeautifulSoup(r.text, "lxml")
    for link in soup.find_all(
        lambda tag: (tag.name == "a") and "Order Now" in tag.text
    ):
        page_url = link["href"]
        if "/locations-list" not in page_url:
            r_loc = session.get(page_url, headers=headers)
            soup_loc = BeautifulSoup(r_loc.text, "lxml")
            locator_domain = base_url
            jd = str(soup_loc).split("<script>")[1].split("</script>")[0]
            location_name = jd.split('var _locationName = "')[1].split('";')[0]
            addr = jd.split('var _locationAddress = "')[1].split('";')[0].split(",")
            if len(addr) == 4:
                street_address = " ".join(addr[:2]).replace(" Springhill", "").strip()
                city = addr[2].strip()
                state = addr[3].strip().split(" ")[0]
                zipp = addr[3].strip().split(" ")[1]
            else:
                street_address = addr[0].lower().strip()
                city = addr[1].lower().strip()
                state = addr[2].strip().split(" ")[0]
                zipp = addr[2].strip().split(" ")[1]
            phone = soup_loc.find(
                lambda tag: (tag.name == "a") and "(" in tag.text
            ).text
            latitude = jd.split("var _locationLat = ")[1].split(";")[0]
            longitude = jd.split("var _locationLng = ")[1].split(";")[0]
            hour_page = page_url + "/Website/Hours"
            hour_r = session.get(hour_page, headers=headers)
            hour_soup = BeautifulSoup(hour_r.text, "lxml")
            hours_of_operation = (
                " ".join(list(hour_soup.stripped_strings)[1:])
                .replace("Business Hours", "Business Hours :")
                .replace("Carryout Hours", ",Carryout Hours :")
            )
            store = []
            store.append(locator_domain if locator_domain else "<MISSING>")
            store.append(location_name if location_name else "<MISSING>")
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append("US")
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("Sam's Southern Eatery")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours_of_operation if hours_of_operation else "<MISSING>")
            store.append(page_url)
            store = [x.replace("–", "-") if type(x) == str else x for x in store]
            store = [x.strip() if type(x) == str else x for x in store]
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            if store[8] in phoness:
                continue
            phoness.append(store[8])
            yield store
    rm_link = [
        "https://www.samssouthernpinebluff.com",
        "https://www.samssouthernwhitehall.com",
        "https://www.samssouthernnatchitoches.com",
        "https://www.samssouthernmarlow.com",
        "https://www.samssoutherntahlequah.com",
        "https://www.samssouthernbethany.com",
        "https://www.samssouthernlawton.com",
        "https://www.samssouthernchickasha.com",
        "https://www.samssouthernmay.com/",
    ]
    r1 = session.get("https://samssoutherneatery.com/locations-list", headers=headers)
    soup1 = BeautifulSoup(r1.text, "lxml")
    for link in soup1.find_all(
        lambda tag: (tag.name == "a") and "Order Now" in tag.text
    ):
        page_url = link["href"].replace("/#/", "")
        if "/locations-list" not in page_url:
            if page_url in rm_link:
                continue
            r_loc = session.get(page_url, headers=headers)
            soup_loc = BeautifulSoup(r_loc.text, "lxml")
            locator_domain = base_url
            jd = str(soup_loc).split("<script>")[1].split("</script>")[0]
            location_name = jd.split('var _locationName = "')[1].split('";')[0]
            addr = jd.split('var _locationAddress = "')[1].split('";')[0].split(",")
            if len(addr) == 4:
                street_address = " ".join(addr[:2]).replace(" Springhill", "").strip()
                city = addr[2].strip()
                state = addr[3].strip().split(" ")[0]
                zipp = addr[3].strip().split(" ")[1]
            else:
                street_address = addr[0].lower().strip()
                city = addr[1].lower().strip()
                state = addr[2].strip().split(" ")[0]
                zipp = addr[2].strip().split(" ")[1]
            phone = soup_loc.find(
                lambda tag: (tag.name == "a") and "(" in tag.text
            ).text
            latitude = jd.split("var _locationLat = ")[1].split(";")[0]
            longitude = jd.split("var _locationLng = ")[1].split(";")[0]
            hour_page = page_url + "/Website/Hours"
            hour_r = session.get(hour_page, headers=headers)
            hour_soup = BeautifulSoup(hour_r.text, "lxml")
            hours_of_operation = (
                " ".join(list(hour_soup.stripped_strings)[1:])
                .replace("Business Hours", "Business Hours :")
                .replace("Carryout Hours", ",Carryout Hours :")
            )
            if page_url == "https://www.samssoutherntoledo.com":
                location_name = "Sam's Southern Eatery Toledo"
                hours_of_operation = "Business Hours Mon - Sat:	9:00 AM - 9:00 PM Sun: 11:00 AM - 9:00 PM, Carryout Hours Mon - Sat: 9:00 AM - 8:45 PM Sun:	11:00 AM - 8:45 PM".strip()
            store = []
            store.append(locator_domain if locator_domain else "<MISSING>")
            store.append(location_name if location_name else "<MISSING>")
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append("US")
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("Sam's Southern Eatery")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours_of_operation if hours_of_operation else "<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            store = [x.replace("–", "-") if type(x) == str else x for x in store]
            store = [x.strip() if type(x) == str else x for x in store]
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            if store[8] in phoness:
                continue
            phoness.append(store[8])
            yield store
    r2 = session.get("https://samssoutherneatery.com/locations-list", headers=headers)
    soup2 = BeautifulSoup(r2.text, "lxml")
    for link2 in soup2.find_all("div", {"class": "sqs-block-content"})[2:]:
        try:
            if "http" not in link2.find("a")["href"]:
                page_url = "https://samssoutherneatery.com" + link2.find("a")["href"]
        except:
            continue
        page_r = session.get(page_url, headers=headers)
        page_soup = BeautifulSoup(page_r.text, "lxml")
        if "https://samssoutherneatery.com/vivian-la" in page_url:
            continue
        if "https://samssoutherneatery.com/mississippi" in page_url:
            addr = list(
                page_soup.find_all("div", {"class": "sqs-block-content"})[
                    1
                ].stripped_strings
            )
            location_name = addr[1]
            street_address = addr[2]
            city = addr[3].split(",")[0]
            state = addr[3].split(",")[1].strip().split(" ")[0]
            zipp = addr[3].split(",")[1].strip().split(" ")[1]
            phone = addr[4]
        else:
            addr = list(
                page_soup.find("div", {"class": "sqs-block-content"}).stripped_strings
            )
            location_name = addr[0]
            street_address = addr[1]
            city = addr[2].split(",")[0]
            state = addr[2].split(",")[1].strip().split(" ")[0]
            try:
                zipp = (
                    addr[2]
                    .split(",")[1]
                    .strip()
                    .split(" ")[1]
                    .replace("7129", "71291")
                    .replace("7680", "76801")
                )
            except:
                zipp = "<MISSING>"
            if "Laplace" in city:
                zipp = "70068"
            try:
                phone = addr[3].replace("Online Ordering Coming Soon!", "<MISSING>")
            except:
                phone = "<MISSING>"
        if "OPENING SOON!" in phone:
            continue
        store = []
        store.append(base_url if base_url else "<MISSING>")
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("Sam's Southern Eatery")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(page_url)
        store = [x.strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        if store[8] in phoness:
            continue
        phoness.append(store[8])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
