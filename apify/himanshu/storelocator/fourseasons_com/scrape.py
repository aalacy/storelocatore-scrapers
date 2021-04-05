import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("fourseasons_com")

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8") as output_file:
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
    return_main_object = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }

    base_url = "https://www.fourseasons.com/find_a_hotel_or_resort/"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    semi_part = soup.find(id="region-north-america-236agu").find_all(
        class_="LinksList-linkContainer"
    )

    locator_domain = "https://www.fourseasons.com"

    for in_semi_part in semi_part:
        page_url = locator_domain + in_semi_part.find("a")["href"]
        logger.info(page_url)
        location_name = in_semi_part.find("a").text
        city = in_semi_part.find("a").text.split(",")[-1].strip()
        city = (
            city.split("(")[0]
            .replace("Downtown", "")
            .replace("at Embarcadero", "")
            .strip()
        )
        store_re = session.get(page_url)
        main_store_soup = BeautifulSoup(store_re.text, "lxml")

        inner_semi_part = main_store_soup.find("div", {"id": "LocationBar"})
        temp_storeaddresss = list(inner_semi_part.stripped_strings)

        return_object = []
        address = temp_storeaddresss[0].split(",")
        if len(address) == 1:
            street_address = "".join(address)
            state = "<MISSING>"
            zipp = "<MISSING>"
        elif len(address) == 2:
            if "Lanai City" != address[0] and "Punta Mita" != address[0]:
                street_address = address[0]
                state = "<MISSING>"
                zipp = "<MISSING>"
            else:
                street_address = "<MISSING>"
                us_zip_list = re.findall(
                    re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(address[-1])
                )
                if us_zip_list:
                    zipp = us_zip_list[0]
                    state = address[-1].split()[0]
                else:
                    zipp = "<MISSING>"
                    state = "<MISSING>"
        elif len(address) == 3:
            street_address = address[0].strip()
            state = address[-1].split()
            if len(address[-1].split()) == 1:
                state = address[-1].strip()
                zipp = "<MISSING>"
            elif len(address[-1].split()) == 2:
                state = address[-1].split()[0]
                zipp = address[-1].split()[1]
            elif "U.S.A." in " ".join(address):
                state = " ".join(address[-1].split()[:-2])
                zipp = address[-1].split()[-2].strip()
            elif "Canada" in " ".join(address):
                state = " ".join(address[-1].split()[:-3])
                zipp = " ".join(address[-1].split()[-3:-1])
        elif len(address) == 4:
            if "Canada" in " ".join(address):
                street_address = address[0].strip()
                state = address[1].split()[-1].strip()
                zipp = address[-2].strip()
            elif " U.S.A." == address[-1]:
                street_address = address[0].strip()
                state = address[-2].split()[0].strip()
                zipp = address[-2].split()[1].strip()
            elif "Mexico" in " ".join(address):
                street_address = address[0].strip()
                state = "<MISSING>"
                zipp = address[-1].split()[0].strip()
            else:
                street_address = " ".join(address[:2]).strip()
                state = address[-1].split()[0].strip()
                zipp = address[-1].split()[1].strip()
        elif len(address) == 5:
            street_address = " ".join(address[:2]).strip()
            if len(address[-1].split()) > 1:
                state = address[-1].split()[0].strip()
                zipp = address[-1].split()[1].strip()
            else:
                state = address[-1].strip()
                zipp = "<MISSING>"
        else:
            street_address = address[0].strip()
            zipp = address[3].strip()
            state = address[-2].strip()
        street_address = street_address.replace("  ", " ")
        if zipp != "<MISSING>":
            if " " in zipp:
                country_code = "CA"
            else:
                country_code = "US"
        else:
            country_code = "US"
        if "Location" in temp_storeaddresss:
            temp_storeaddresss.remove("Location")

        if len(temp_storeaddresss) == 1:
            phone = "<MISSING>"
        else:
            phone = temp_storeaddresss[1].split("or")[0].strip()
        if "York" == zipp:
            zipp = address[-2].split()[-1].strip()
        if "New" == state:
            state = address[1].strip()
        if "U.S.A." in state:
            state = address[-2].split()[0].strip()
        if "Caribbean" in state:
            state = "<MISSING>"
        if "Baja California Sur" in state or "Bahamas" in state:
            continue
        if "Anguilla" in state:
            continue
        if "xico" in city.lower() or "xico" in city.lower() or "Nevis" in city:
            continue
        if "9500 Wilshire" in street_address:
            city = "Beverly Hills"
        if "Two Dole Drive" in street_address:
            city = "Westlake Village"
        if "DC" in city:
            city = "Washington"
            state = "DC"

        return_object.append(locator_domain)
        return_object.append(location_name)
        return_object.append(street_address)
        return_object.append(city)
        return_object.append(state)
        return_object.append(zipp)
        return_object.append(country_code)
        return_object.append("<MISSING>")
        return_object.append(phone)
        return_object.append("<MISSING>")
        return_object.append("<MISSING>")
        return_object.append("<MISSING>")
        return_object.append("<MISSING>")
        return_object.append(page_url)
        return_main_object.append(return_object)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
