import csv
import unicodedata

from bs4 import BeautifulSoup

from google_trans_new import google_translator

from sgrequests import SgRequests

translator = google_translator()
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf-8") as output_file:
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
    base_url = "https://www.mitsubishi-motors.ca/"
    addressess = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
    }

    link = "https://www.mitsubishi-motors.ca/api/ev_dealer.json"
    json_data = session.get(link, headers=headers).json()

    for loc in json_data:
        address = loc["CompanyAddress"].strip()
        name = loc["CompanyName"].strip()
        city = loc["CompanyCity"].strip().capitalize()
        state = loc["ProvinceAbbreviation"].strip()
        zipp = loc["CompanyPostalCode"].replace("S4R R8R", "S4R 0X3")
        phone = loc["CompanyPhone"].strip()
        lat = loc["Latitude"]
        lng = loc["Longitude"]
        page_url = loc["PrimaryDomain"]
        storeno = loc["CompanyId"]

        hours = ""
        r1 = session.get(page_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        try:
            hours = " ".join(
                list(
                    soup1.find(
                        "ul", {"class": "list-unstyled line-height-condensed"}
                    ).stripped_strings
                )
            )
        except:
            pass
        if not hours:
            try:
                hours = " ".join(
                    list(
                        soup1.find("ul", {"class": "opening-hours-ul"}).stripped_strings
                    )
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(
                        soup1.find(
                            "div", {"class": "footer-hours-col sales-hours"}
                        ).li.stripped_strings
                    )
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(soup1.find("table", {"class": "hours"}).stripped_strings)
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(
                        soup1.find(
                            "div", {"id": "tabs-template-hours1"}.ul.li
                        ).stripped_strings
                    )
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(
                        soup1.find(
                            "div", {"id": "slshours_footer_home"}
                        ).stripped_strings
                    )
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(soup1.find("div", {"id": "HOPSales"}).stripped_strings)
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(soup1.find("table", {"class": "hours_table"}).stripped_strings)
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(
                        soup1.find(
                            "div", {"id": "Sales36412421385f59c2556d399"}
                        ).stripped_strings
                    )
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(
                        soup1.find(
                            "table", {"class": "grid-y department-hours"}
                        ).stripped_strings
                    )
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(
                        soup1.find(
                            "table", {"class": "map_open_hours"}
                        ).stripped_strings
                    )
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(
                        soup1.find(
                            "div", {"class": "map_open_hours"}
                        ).ul.li.stripped_strings
                    )
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(
                        soup1.find(
                            "table", {"class": "footer-hours-tabs__box-wrapper"}
                        ).stripped_strings
                    )
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(
                        soup1.find(
                            "div", {"id": "footer-hours-loc-0-sales"}
                        ).stripped_strings
                    )
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(
                        soup1.find(
                            "div", {"class": "dynamic-hours parts"}
                        ).stripped_strings
                    )
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(
                        soup1.find(
                            "ul", {"class": "list-unstyled line-height-condensed"}
                        ).stripped_strings
                    )
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(soup1.find("div", {"class": "hours-default"}).stripped_strings)
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(
                        soup1.find("div", {"class": "hours1-app-root"}).stripped_strings
                    )
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(
                        soup1.find(
                            "table", {"class": "beaucage_hours"}
                        ).stripped_strings
                    )
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(
                        soup1.find(
                            "div", {"class": "footer-column footer-column--hours"}.ul
                        ).stripped_strings
                    )
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(soup1.find("div", {"class": "hours-list"}).stripped_strings)
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(
                        soup1.find(
                            "table", {"class": "schedule-table"}
                        ).stripped_strings
                    )
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(
                        soup1.find(
                            "div", {"id": "slshours_footer_home"}
                        ).stripped_strings
                    )
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(
                        soup1.find(
                            "div", {"class": "footer-hours"}.find_all("p")[1]
                        ).stripped_strings
                    )
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(
                        soup1.find(
                            "div", {"class": "hours-footer hours-footer-1"}.ul
                        ).stripped_strings
                    )
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(
                        soup1.find(
                            "div", {"class": "footer_dealer_info_hours"}.ul
                        ).stripped_strings
                    )
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(
                        soup1.find(
                            "div", {"class": "footer_dealer_info_hours"}.ul
                        ).stripped_strings
                    )
                )
            except:
                pass
        if not hours:
            try:
                hours = " ".join(
                    list(
                        soup1.find_all("ul", {"class": "footer-column__list"})[
                            1
                        ].stripped_strings
                    )
                )
            except:
                pass
        hours = (
            hours.replace("Heures d'ouverture", "")
            .replace("Days Hours", "")
            .replace("HOURS", "")
            .replace("Hours", "")
            .replace("Hours:", "")
            .replace("Sales", "")
            .replace("Horaires:", "")
            .replace("Business hours", "")
            .replace("Dealership hours of operation", "")
            .split("Tell us")[0]
            .split("Avisez-nous")[0]
            .split("See All")[0]
            .strip()
        )
        try:
            hours = (
                translator.translate(hours, lang_tgt="en")
                .split("Service")[0]
                .replace("Opening hours", "")
                .replace("Business hours", "")
                .split("Notify us of your visit!")[0]
                .strip()
            )
        except:
            pass
        if city == "N.d.p, joliette":
            city = "Joliette"
            address = address + str(", N.D.P")
        store = []
        store.append(base_url)
        store.append(name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("CA")
        store.append(storeno)
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hours.strip())
        store.append(page_url)
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        store = [x.replace("  to  ", " - ") if type(x) == str else x for x in store]
        store = [x.replace("  a  ", " - ") if type(x) == str else x for x in store]
        store = [x.replace(" a ", " - ") if type(x) == str else x for x in store]
        store = [x.replace(" To ", " - ") if type(x) == str else x for x in store]
        store = [x.replace(" à ", " - ") if type(x) == str else x for x in store]
        store = [x.replace(" ", "") if type(x) == str else x for x in store]
        for i in range(len(store)):
            if type(store[i]) == str:
                store[i] = "".join(
                    (
                        c
                        for c in unicodedata.normalize("NFD", store[i])
                        if unicodedata.category(c) != "Mn"
                    )
                )
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
