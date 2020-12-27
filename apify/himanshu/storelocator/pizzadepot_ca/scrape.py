import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests

session = SgRequests()
from sgselenium import SgSelenium


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
    driver = SgSelenium().firefox("geckodriver.exe")
    driver.get("https://pizzadepot.ca/")
    cookies_list = driver.get_cookies()
    cookies_json = {}
    for cookie in cookies_list:
        cookies_json[cookie["name"]] = cookie["value"]
    cookies_string = (
        str(cookies_json)
        .replace("{", "")
        .replace("}", "")
        .replace("'", "")
        .replace(": ", "=")
        .replace(",", ";")
    )
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "cookie": cookies_string,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
    }
    base_url = "https://pizzadepot.ca/"
    for i in range(11, 44):
        page_url = "https://pizzadepot.ca/locationDetails/" + str(i)
        r = session.get(page_url, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        name = soup.find("div", {"class": "bs-glyphicon-class"})
        store_number = str(i)
        if name == "":
            continue
        lst = list(soup.find("div", {"class": "fadeInLeft"}).stripped_strings)
        try:
            if len(lst) == 11:
                location_name = lst[0]
                street_address = lst[1].split(",")[0]
                if "Springdale" in location_name:
                    city = "Springdale"
                else:
                    city = lst[1].split(",")[1].strip()
                zipp = lst[2]
                phone = lst[3]
                hours_of_operation = ", ".join(lst[6:10])
                map_url = (
                    soup.find_all("iframe")[-1]["src"]
                    .split("!2m3")[0]
                    .split("!2d")[1]
                    .split("!3d")
                )
                lat = map_url[1]
                lng = map_url[0]
            else:
                location_name = lst[0]
                street_address = "<MISSING>"
                city = "<MISSING>"
                zipp = lst[1]
                phone = lst[2]
                hours_of_operation = "Monday-Thursday " + (", ".join(lst[5:9]))
                map_url = (
                    soup.find_all("iframe")[-1]["src"]
                    .split("!2m3")[0]
                    .split("!2d")[1]
                    .split("!3d")
                )
                lat = map_url[1]
                lng = map_url[0]
        except:
            continue
        store = []
        store.append(base_url)
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append("ON")
        store.append(zipp if zipp else "<MISSING>")
        store.append("CA")
        store.append(store_number if store_number else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("Pizza Depot")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(
            hours_of_operation.replace("- - - - - - - -", "<MISSING>").replace(
                "-", " - "
            )
        )
        store.append(page_url if page_url else "<MISSING>")
        store = [
            x.encode("ascii", "ignore").decode("ascii").strip() if x else "<MISSING>"
            for x in store
        ]
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
