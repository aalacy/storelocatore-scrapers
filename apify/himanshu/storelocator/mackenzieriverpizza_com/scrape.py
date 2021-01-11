import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

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
    addressess = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    base_url = "https://www.mackenzieriverpizza.com/locations/"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for link in soup.find_all("div", {"class": "et_pb_text_inner"}):
        page_url = link.find("h3").find("a")["href"]
        r1 = session.get(page_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        addr = list(
            soup1.find_all("div", {"class": "et_pb_text_inner"})[1].stripped_strings
        )
        if addr == []:
            if (
                page_url == "https://www.mackenzieriverpizza.com/rapid-city/"
                or page_url == "https://www.mackenzieriverpizza.com/fairfield/"
            ):
                if page_url == "https://www.mackenzieriverpizza.com/rapid-city/":
                    location_name = "Rapid City,SD"
                else:
                    location_name = soup1.find(
                        "h2", {"class": "et_pb_slide_title"}
                    ).text
                addr1 = list(
                    soup1.find_all("div", {"class": "et_pb_text_inner"})[
                        0
                    ].stripped_strings
                )
                street_address = addr1[1]
                city = addr1[2].split(",")[0]
                state = addr1[2].split(",")[1].strip().split(" ")[0]
                zipp = addr1[2].split(",")[1].strip().split(" ")[1]
                phone = addr1[3]
                hours_of_operation = ", ".join(addr1[5:])
            else:
                location_name = soup1.find("h2", {"class": "et_pb_slide_title"}).text
                addr1 = list(
                    soup1.find_all("div", {"class": "et_pb_text_inner"})[
                        0
                    ].stripped_strings
                )
                street_address = addr1[2]
                city = addr1[3].split(",")[0]
                state = addr1[3].split(",")[1].strip().split(" ")[0]
                try:
                    zipp = addr1[3].split(",")[1].strip().split(" ")[1]
                except:
                    zipp = "<MISSING>"
                phone = addr1[1]
                hours_of_operation = ", ".join(addr1[5:])
        elif addr[0] == "EAT":
            location_name = soup1.find("h2", {"class": "et_pb_slide_title"}).text
            addr1 = list(
                soup1.find_all("div", {"class": "et_pb_text_inner"})[0].stripped_strings
            )
            street_address = addr1[2]
            city = addr1[3].split(",")[0]
            state = addr1[3].split(",")[1].strip().split(" ")[0]
            zipp = addr1[3].split(",")[1].strip().split(" ")[1]
            phone = addr1[1]
            hours_of_operation = ", ".join(addr1[5:])
        elif addr[0] == "HOURS":
            location_name = soup1.find("h2", {"class": "et_pb_slide_title"}).text
            addr1 = list(
                soup1.find_all("div", {"class": "et_pb_text_inner"})[0].stripped_strings
            )
            hoo = list(
                soup1.find_all("div", {"class": "et_pb_text_inner"})[1].stripped_strings
            )
            street_address = addr1[2]
            city = addr1[3].split(",")[0]
            state = addr1[3].split(",")[1].strip().split(" ")[0]
            try:
                zipp = addr1[3].split(",")[1].strip().split(" ")[1]
            except:
                zipp = addr1[4]
            phone = addr1[1]
            hours_of_operation = ", ".join(hoo[1:])
        else:
            location_name = (
                soup1.find("h1", {"style": "text-align: center;"}).find("span").text
            )
            addr1 = addr
            street_address = addr1[2]
            city = addr1[3].split(",")[0]
            state = addr1[3].split(",")[1].strip().split(" ")[0]
            zipp = addr1[3].split(",")[1].strip().split(" ")[1]
            phone = addr1[1]
            hours_of_operation = ", ".join(addr1[5:])

        map_url = (
            soup1.find("iframe")["src"].split("!2m3")[0].split("!2d")[1].split("!3d")
        )
        lat = map_url[1]
        lng = map_url[0]

        store = []
        store.append("https://www.mackenzieriverpizza.com/")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("MacKenzie River Pizza")
        store.append(lat)
        store.append(lng)
        store.append(hours_of_operation)
        store.append(page_url)
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
