import csv
import json
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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


def get_data(
    location_name,
    street_address,
    city,
    state,
    zipp,
    phone,
    latitude,
    longitude,
    hours,
    page_url,
):
    store = []
    store.append("http://www.facelogicspa.com/")
    store.append(location_name)
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
    store.append(hours.strip())
    store.append(page_url)
    return store


def fetch_data():
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    r = session.get("http://www.facelogicspa.com/pages/spas")
    soup = BeautifulSoup(r.text, "lxml")
    for link in soup.find("div", {"class": "pt25 pl25 pr25 pb25"}).find_all("a"):
        if "http" not in link["href"]:

            page_url = "http://www.facelogicspa.com" + (
                link["href"].replace("about", "contact-us")
            )
            r1 = session.get(page_url, headers=headers)
            soup1 = BeautifulSoup(r1.text, "lxml")
            location_name = soup1.title.text.strip()
            if "|" in location_name:
                location_name = location_name[: location_name.find("|")].strip()
            addr = list(soup1.select(".mt20.mb20")[0].find("p").stripped_strings)
            street_address = " ".join(addr[:-1])
            city = addr[-1].split(",")[0]
            state = addr[-1].split(",")[1].split(" ")[1]
            zipp = addr[-1].split(",")[1].split(" ")[2]
            phone = (
                soup1.select(".mt20.mb20")[0]
                .find("p")
                .next_sibling.strip()
                .replace("P:", "")
                .replace("-FACE ", "")
                .strip()
            )
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours = (
                soup1.find(class_="grid_5 omega").p.text.replace("\r\n\t", " ").strip()
            )
            store = get_data(
                location_name,
                street_address,
                city,
                state,
                zipp,
                phone,
                latitude,
                longitude,
                hours,
                page_url,
            )
            yield store
        else:

            if "facelogicclovis" in link["href"]:

                page_url = "http://www.facelogicclovis.com/pages/contact"
                r2 = session.get(page_url, headers=headers)
                soup2 = BeautifulSoup(r2.text, "lxml")
                location_name = "<MISSING>"
                addr = list(
                    soup2.find("div", {"id": "le_54868cf8ef5a3"}).stripped_strings
                )
                location_name = addr[1]
                street_address = addr[2]
                city = addr[3].split(",")[0]
                state = addr[3].split(",")[1].split(" ")[1]
                zipp = addr[3].split(",")[1].split(" ")[2]
                phone = addr[4].replace("P.", "").replace("-SKIN ", "").strip()
                latitude = (
                    soup2.find("div", {"class": "le_plugin_map map-responsive"})
                    .find("iframe")["src"]
                    .split("sll=")[1]
                    .split(",")[0]
                )
                longitude = (
                    soup2.find("div", {"class": "le_plugin_map map-responsive"})
                    .find("iframe")["src"]
                    .split("sll=")[1]
                    .split(",")[1]
                    .split("&")[0]
                )
                hours = "<MISSING>"

                store = get_data(
                    location_name,
                    street_address,
                    city,
                    state,
                    zipp,
                    phone,
                    latitude,
                    longitude,
                    hours,
                    page_url,
                )
                yield store
            elif "facelogicupland" in link["href"]:

                page_url = "https://www.facelogicupland.com/about/"
                r2 = session.get(page_url, headers=headers)
                soup2 = BeautifulSoup(r2.text, "lxml")
                location_name = (
                    soup2.find("div", {"class": "entry-content"})
                    .find_all("p")[4]
                    .find_all("strong")[0]
                    .text
                )
                street_address = (
                    soup2.find("div", {"class": "entry-content"})
                    .find_all("p")[4]
                    .find_all("strong")[1]
                    .text
                )
                addr = (
                    soup2.find("div", {"class": "entry-content"})
                    .find_all("p")[4]
                    .find_all("strong")[2]
                    .text
                )
                city = addr.split(",")[0]
                state = addr.split(",")[1].split(" ")[1]
                zipp = addr.split(",")[1].split(" ")[2]
                phone = (
                    soup2.find("div", {"class": "entry-content"})
                    .find_all("p")[5]
                    .find("strong")
                    .text.strip()
                )
                ps = list(
                    soup2.find("div", {"class": "entry-content"})
                    .find_all("p")[6]
                    .stripped_strings
                )

                hours = ""
                for p in ps:
                    if "00pm" in p:
                        hours = (hours + " " + p[: p.rfind("pm") + 2].strip()).strip()

                latitude = "<MISSING>"
                longitude = "<MISSING>"

                store = get_data(
                    location_name,
                    street_address,
                    city,
                    state,
                    zipp,
                    phone,
                    latitude,
                    longitude,
                    hours,
                    page_url,
                )
                yield store
            elif "facelogicco" in link["href"]:
                try:
                    page_url = "https://facelogicbroomfield.com/contact-us"
                    r2 = session.get(page_url, headers=headers)
                except:
                    continue
                soup2 = BeautifulSoup(r2.text, "lxml")
                js = soup2.find("div", {"class": "col sqs-col-6 span-6"}).div[
                    "data-block-json"
                ]
                store = json.loads(js)["location"]
                location_name = "<MISSING>"
                street_address = store["addressLine1"]
                data = store["addressLine2"].strip().split(",")
                city = data[0]
                state = data[-1].split()[0]
                zipp = data[-1].split()[1]
                latitude = store["mapLat"]
                longitude = store["mapLng"]
                ps = soup2.find_all("p")
                for p in ps:
                    if "303-" in p.text:
                        phone = p.text.replace("Phone:\xa0", "").strip()
                        if "skin" in phone.lower():
                            phone = "303-466-7546"

                hours = ""
                for p in ps:
                    if "day" in p.text:
                        hours = (
                            hours + " " + p.text.replace("\xa0", " ").strip()
                        ).strip()

                store = get_data(
                    location_name,
                    street_address,
                    city,
                    state,
                    zipp,
                    phone,
                    latitude,
                    longitude,
                    hours,
                    page_url,
                )
                yield store

            elif "facelogicsc" in link["href"]:
                page_url = link["href"]
                r2 = session.get(page_url, headers=headers)
                soup2 = BeautifulSoup(r2.text, "lxml")
                data = list(
                    soup2.find_all("div", {"class": "textwidget"})[-1].stripped_strings
                )
                location_name = soup2.h3.text.strip()
                street_address = data[-2]
                city = data[-1].split(",")[0]
                state = data[-1].split(",")[1].split(" ")[1]
                zipp = data[-1].split(",")[1].split(" ")[2]
                phone = data[0]
                hours = (
                    " ".join(
                        list(
                            soup2.find_all("div", {"class": "textwidget"})[-2]
                            .find("ul")
                            .stripped_strings
                        )
                    )
                ).replace("  ", " ")
                latitude = "<MISSING>"
                longitude = "<MISSING>"

                store = get_data(
                    location_name,
                    street_address,
                    city,
                    state,
                    zipp,
                    phone,
                    latitude,
                    longitude,
                    hours,
                    page_url,
                )
                yield store
            elif "facelogickisco" in link["href"]:

                page_url = link["href"]
                r2 = session.get(page_url, headers=headers)
                soup2 = BeautifulSoup(r2.text, "lxml")
                data = list(soup2.find(class_="footer-widgets").stripped_strings)
                location_name = soup2.title.text.replace("Home -", "").strip()
                street_address = data[1]
                city = data[2].split(",")[0]
                state = data[2].split(",")[1].split(" ")[1]
                zipp = data[2].split(",")[1].split(" ")[2]
                phone = re.findall(r"[(\d)]{3}-[\d]{3}-[\d]{4}", str(soup2))[0]
                hours = " ".join(
                    list(
                        soup2.find_all("div", {"class": "textwidget"})[-1]
                        .find("p")
                        .stripped_strings
                    )
                )
                latitude = "<MISSING>"
                longitude = "<MISSING>"

                store = get_data(
                    location_name,
                    street_address,
                    city,
                    state,
                    zipp,
                    phone,
                    latitude,
                    longitude,
                    hours,
                    page_url,
                )
                yield store
            elif "cleveland.facelogicspa" in link["href"]:
                page_url = link["href"]
                try:
                    r2 = session.get(page_url, headers=headers)
                    soup2 = BeautifulSoup(r2.text, "lxml")
                except:
                    continue
                if "coming soon" in soup2.title.text.lower():
                    continue
                data = list(soup2.find("span", {"id": "address"}).stripped_strings)
                location_name = data[0]
                street_address = data[1]
                city = data[2].split(",")[0]
                state = data[2].split(",")[1].split(" ")[1]
                zipp = data[2].split(",")[1].split(" ")[2]
                phone = data[-2].replace("P:", "").replace("-SKIN ", "").strip()
                hours = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"

                store = get_data(
                    location_name,
                    street_address,
                    city,
                    state,
                    zipp,
                    phone,
                    latitude,
                    longitude,
                    hours,
                    page_url,
                )
                yield store
            elif "facelogicbcs" in link["href"]:
                page_url = "http://emeraldlotusspa.com/"
                r2 = session.get(page_url, headers=headers)
                soup2 = BeautifulSoup(r2.text, "lxml")
                location_name = "FacelogicBCS"
                raw_adress = soup2.find("h3").text.replace(" \xa0", "").split("|")
                street_address = raw_adress[0]
                city = raw_adress[1].split(",")[0]
                state = raw_adress[1].split(",")[1].strip()
                zipp = raw_adress[-1]
                phone = soup2.find(class_="site-phone").text.strip()
                hours = "<MISSING>"
                js = soup2.find(
                    "div", {"class": "sqs-block map-block sqs-block-map sized vsize-12"}
                )["data-block-json"]
                store = json.loads(js)["location"]
                latitude = store["mapLat"]
                longitude = store["mapLng"]

                store = get_data(
                    location_name,
                    street_address,
                    city,
                    state,
                    zipp,
                    phone,
                    latitude,
                    longitude,
                    hours,
                    page_url,
                )
                yield store
            elif "facelogichighlandpark" in link["href"]:
                page_url = link["href"]
                r2 = session.get(page_url, headers=headers)
                soup2 = BeautifulSoup(r2.text, "lxml")
                location_name = "Facelogic Highland Park"
                data = soup2.find(class_="sub-title").text.split(",")
                street_address = data[0].replace("Dallas", "").strip()
                city = "Dallas"
                state = data[-1].split()[0]
                zipp = data[-1].split()[1]
                phone = soup2.find(class_="contact-list").text
                hours = " ".join(
                    list(soup2.find(class_="section-desc").stripped_strings)[1:]
                )
                latitude = "<MISSING>"
                longitude = "<MISSING>"

                store = get_data(
                    location_name,
                    street_address,
                    city,
                    state,
                    zipp,
                    phone,
                    latitude,
                    longitude,
                    hours,
                    page_url,
                )
                yield store
            elif "facelogictx" in link["href"]:

                page_url = (
                    "https://na02.envisiongo.com/a/facelogicmurphy/OnlineBooking.aspx"
                )
                r2 = session.get(page_url, headers=headers)
                soup2 = BeautifulSoup(r2.text, "lxml")
                location_name = soup2.find(id="title").p.text.strip()
                raw_adress = list(soup2.find(id="divStoreDetails").p.stripped_strings)
                street_address = raw_adress[0].strip()
                city = raw_adress[1].split(",")[0].strip()
                state = raw_adress[1].split(",")[1].strip().split()[0]
                zipp = raw_adress[1].split(",")[1].strip().split()[1]
                phone = raw_adress[-3].replace("Phone:", "").strip()
                hours = (
                    soup2.find(id="tablehours")
                    .text.replace("\xa0", "")
                    .replace("\n", " ")
                    .strip()
                )
                latitude = "<MISSING>"
                longitude = "<MISSING>"

                store = get_data(
                    location_name,
                    street_address,
                    city,
                    state,
                    zipp,
                    phone,
                    latitude,
                    longitude,
                    hours,
                    page_url,
                )
                yield store
            elif "facelogicchinohills" in link["href"]:

                page_url = "https://www.facelogicchinohills.com/contact-us"
                r2 = session.get(page_url, headers=headers)
                soup2 = BeautifulSoup(r2.text, "lxml")
                data = soup2.find(class_="kv-ee-address-text").text.split(",")
                location_name = soup2.title.text.replace("Contact us -", "").strip()
                street_address = data[0].strip()
                city = data[-3].strip()
                state = data[-2].strip()
                zipp = data[1].strip()
                phone = soup2.find(class_="kv-ee-phone-number").text.strip()
                hours = "<MISSING>"
                if "13850 City Center" in street_address:
                    latitude = "-16.652997"
                    longitude = "-97.340023"

                store = get_data(
                    location_name,
                    street_address,
                    city,
                    state,
                    zipp,
                    phone,
                    latitude,
                    longitude,
                    hours,
                    page_url,
                )
                yield store
            elif (
                "facelogicspawaco.com" in link["href"]
                or "puravidafacelogicspa.com" in link["href"]
            ):
                page_url = "https://puravidafacelogicspa.com/contact-us/"
                r2 = session.get(page_url, headers=headers)
                soup2 = BeautifulSoup(r2.text, "lxml")

                items = soup2.find_all(class_="cmsmasters_column one_half")
                for item in items:
                    location_name = item.h2.text
                    data = (
                        item.h4.text.replace(", Suit", " Suit")
                        .replace("Waco", "")
                        .split(",")
                    )
                    street_address = data[0].strip()
                    if "waco" not in item.h4.text.lower():
                        raise
                    city = "Waco"
                    state = data[-1].strip().split()[0]
                    zipp = data[-1].strip().split()[1]
                    phone = data[-1].strip().split()[2]
                    hours = item.p.text.replace("\n", " ")
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"

                    store = get_data(
                        location_name,
                        street_address,
                        city,
                        state,
                        zipp,
                        phone,
                        latitude,
                        longitude,
                        hours,
                        page_url,
                    )
                    yield store
            else:
                raise


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
