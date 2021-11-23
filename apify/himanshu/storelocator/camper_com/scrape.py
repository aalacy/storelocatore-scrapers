import csv
import json

from bs4 import BeautifulSoup

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
    base_url = "https://www.camper.com"

    return_main_object = []

    countries = ["usa", "ca", "uk"]
    for country in countries:
        r1 = session.get(base_url + "/en_US/shops/" + country)
        soup1 = BeautifulSoup(r1.text, "lxml")
        main1 = soup1.find("div", {"id": "lista"}).find_all(
            "div", {"class": "store_item"}
        )
        for atag in main1:
            link = atag.find("a", {"class": "btn_view_store"})["href"]
            storeno = link.split("-")[-1]
            final_link = base_url + link
            r2 = session.get(final_link)
            soup2 = BeautifulSoup(r2.text, "lxml")
            name = soup2.find("h2", {"itemprop": "name"}).text.strip()
            address = soup2.find("span", {"itemprop": "streetAddress"}).text.strip()
            zip = soup2.find("span", {"itemprop": "postalCode"}).text.strip()
            city = soup2.find("span", {"itemprop": "addressLocality"}).text.strip()
            state = "<MISSING>"
            if city == "NEW YORK":
                state = city
            phone = soup2.find("a", {"itemprop": "telephone"}).text.strip()
            hour = ""
            if soup2.find("div", {"class": "hours"}) is not None:
                days = list(soup2.find(class_="hours").td.stripped_strings)
                hours = list(
                    soup2.find(class_="hours").find_all("td")[1].stripped_strings
                )
                for i in range(len(days)):
                    hour = (hour + " " + days[i] + " " + hours[i]).strip()
            script = (
                soup2.find_all("script", attrs={"type": "application/ld+json"})[-1]
                .contents[0]
                .replace("47,\n\t\t\t", "47.6156463,")
                .replace(" 6156463,", "")
                .replace("-122,203", "-122.203")
            )
            store = json.loads(script)

            lat = store["geo"]["latitude"]
            lng = store["geo"]["longitude"]

            if not hour:
                raw_hours = store["openingHoursSpecification"]
                for hours in raw_hours:
                    day = hours["dayOfWeek"]
                    if len(day[0]) != 1:
                        day = " ".join(hours["dayOfWeek"])
                    opens = hours["opens"]
                    closes = hours["closes"]
                    if opens != "" and closes != "":
                        clean_hours = day + " " + opens + "-" + closes
                        hour = (hour + " " + clean_hours).strip()
            if (
                "temporarily closed"
                in soup2.find(class_="div_info_tienda").text.lower()
            ):
                hour = "Temporarily Closed"

            store = []
            store.append(base_url)
            store.append(name)
            store.append(address)
            store.append(city)
            store.append(state)
            store.append(zip)
            store.append(country.replace("usa", "us").upper())
            store.append(storeno)
            store.append(phone)
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hour)
            store.append(final_link)
            return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
