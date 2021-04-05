import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()


def write_output(data):
    with open("data.csv", newline="", mode="w", encoding="utf-8") as output_file:
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
    addresses = []
    headers = {
        "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    }

    base_url = "https://unitedtkdcenters.com"
    location_url = "https://www.unitedtkdcenters.com/locations"

    r = session.get(location_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    div = soup.find_all("div", {"data-ux": "ContentCard"})[0:30]
    for i in div:
        name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        phone = ""
        latitude = ""
        longitude = ""
        hours_of_operation = ""
        link = ""

        try:
            if "/locations" in i.find("a", {"data-ux": "ContentCardButton"})["href"]:
                name = i.find("h4", {"data-ux": "ContentCardHeading"}).text
                addr = i.find_all("span")[0].text.split(",")
                street_address = addr[0].strip()
                city = addr[1].strip()
                state = "<MISSING>"
                zipp = "<MISSING>"
                phone = i.find_all("span")[1].text.strip()
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                hours_of_operation = "<MISSING>"
                link = "<MISSING>"
            else:

                link = base_url + i.find("a", {"data-ux": "ContentCardButton"})["href"]
                if link == "https://unitedtkdcenters.com/jackson-heights-roosevelt":
                    name = "Jackson Heights (Roosevelt)"
                    street_address = "85-15 Roosevelt Ave"
                    city = "Flushing"
                    phone = "718-457-3400"
                    state = "<MISSING>"
                    zipp = "<MISSING>"
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                    hours_of_operation = "<MISSING>"
                    link = "<MISSING>"
                else:
                    r1 = session.get(link, headers=headers)
                    soup1 = BeautifulSoup(r1.text, "lxml")
                    try:
                        name = soup1.find("h2", {"data-ux": "SectionSplitHeading"}).text
                    except:
                        name = soup1.find("h1", {"data-ux": "SectionSplitHeading"}).text

                    addr2 = soup1.find("p", {"data-ux": "ContentText"}).text.split(",")
                    phone = soup1.find(
                        "a", {"data-aid": "CONTACT_INFO_PHONE_REND"}
                    ).text.strip()
                    if len(addr2) == 2:
                        street_address = addr2[0]
                        city = addr2[1].strip()
                        state = "<MISSING>"
                        zipp = "<MISSING>"
                    elif len(addr2) == 3:
                        street_address = addr2[0]
                        city = addr2[1].strip()
                        temp_state_zip = addr2[2].split(" ")
                        state = temp_state_zip[-2]
                        zipp = temp_state_zip[-1]
                    elif len(addr2) == 4:
                        street_address = addr2[0]
                        city = addr2[1].strip()
                        temp_state_zip = addr2[2].split(" ")
                        state = (
                            " ".join(temp_state_zip[0:3]).replace(" 07423", "").strip()
                        )
                        zipp = temp_state_zip[-1].strip()
                    elif len(addr2) == 5:
                        street_address = addr2[0]
                        city = addr2[1].strip()
                        temp_state_zip = addr2[3].split(" ")
                        state = (
                            " ".join(temp_state_zip[0:3]).replace(" 07423", "").strip()
                        )
                        zipp = temp_state_zip[-1].strip()

                    for i in soup1.find_all(
                        "script",
                        {
                            "src": re.compile(
                                "//img1.wsimg.com/blobby/go/1730034b-f59e-4632-8435-ec0a3958a5d9/gpub"
                            )
                        },
                    ):
                        if "isPublishMode" in str(
                            BeautifulSoup(session.get("https:" + i["src"]).text, "lxml")
                        ):
                            geo_data = json.loads(
                                session.get("https:" + i["src"])
                                .text.split("})(")[1]
                                .split(',{"widgetId"')[0]
                            )
                            latitude = geo_data["lat"]
                            longitude = geo_data["lon"]

                        if "structuredHours" in str(
                            BeautifulSoup(session.get("https:" + i["src"]).text, "lxml")
                        ):
                            hour_data = json.loads(
                                session.get("https:" + i["src"])
                                .text.split("})(")[1]
                                .split(',{"widgetId"')[0]
                            )["structuredHours"]
                            hoo = []
                            for k in hour_data[:-1]:

                                day = k["hour"]["day"]
                                closetime = k["hour"]["closeTime"]
                                opentime = k["hour"]["openTime"]
                                frame = day + ": " + opentime + " - " + closetime
                                hoo.append(frame)
                            hours_of_operation = ", ".join(hoo)
                    hours_of_operation = hours_of_operation + ", Sun: Closed"
        except TypeError:
            continue

        store = []
        store.append(base_url)
        store.append(name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(link)

        store = [str(x).strip() if x else "<MISSING>" for x in store]
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
