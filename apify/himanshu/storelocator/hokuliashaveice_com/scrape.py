import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("hokuliashaveice_com")

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
    return_main_object = []

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
        "accept": "application/json, text/javascript, */*; q=0.01",
    }

    locator_domain = "https://hokuliashaveice.com"
    location_name = ""
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    location_type = "<MISSING>"
    page_url = "https://hokuliashaveice.com/locations/"

    r = session.get("https://hokuliashaveice.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    script = soup.find("div", {"id": "locations"}).find_next("script")
    s = script.text.split(" var features = ")[-1].split("];")[0] + "]".replace("\n", "")
    sc = s.split(" position:")
    sc.pop(0)

    for i in sc:
        info = i.replace("\n", "").replace("  ", "")
        latitude = info.split("(")[1].split(")")[0].split(",")[0]
        longitude = info.split("(")[1].split(")")[0].split(",")[-1]
        address = (
            info.split("message:")[-1].split("<br>")[0].replace('"', "").split("<br />")
        )

        add_list = []
        for element in address:
            if element != "":
                add_list.append(element)

        if len(add_list) == 2:

            add = " ".join(add_list).split(",")

            if len(add) == 2:
                street_address = add[0]
                if len(add[-1].split()) == 1:
                    city = add[0].split()[-1]
                    state = add[-1]
                    zipp = "<MISSING>"
                    location_name = city
                else:
                    city = add[-1].split()[0]
                    state = add[-1].split()[1]
                    zipp = add[-1].split()[-1]
                    location_name = city

            else:
                street_address = add[0].strip()
                city = add[-2].strip()
                state = add[-1].split()[0]
                zipp = add[-1].split()[-1]

        elif len(add_list) == 3:
            if (
                " 1143 Prince Ave" not in add_list[0]
                and " 3341 Lexington Road" not in add_list[0]
            ):
                location_name = add_list[0].strip()
                street_address = add_list[1]
                city = add_list[2].split(",")[0]

                sz = add_list[2].split(",")[-1]

                us_zip_list = re.findall(
                    re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(sz)
                )
                if us_zip_list:
                    zipp = us_zip_list[0]

                else:
                    m = re.findall(r"\d", sz)
                    zip = "".join(m)

                    if zip.split():
                        zipp = zip

                    else:
                        zipp = "<MISSING>"

                if len(sz.split()) == 2:
                    state = sz.split()[0].strip()

                else:

                    if zip.split():
                        state = sz.split(zip)[0].strip()

                    else:
                        state = sz.strip()
            else:
                street_address = add_list[0].strip()
                city = "Athens"
                state = "GA"
                zipp_list = re.findall(
                    re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), " ".join(add_list)
                )
                if not zipp_list:
                    zipp = "<MISSING>"
                else:
                    zipp = zipp_list[0]
                location_name = city

        elif len(add_list) == 4:

            location_name = add_list[0].strip()
            street_address = " ".join(add_list[1:-1]).replace(", KS 66061", "")

            csz = add_list[-1].split(",")
            if len(csz) > 1:
                city = csz[0].strip()
                if len(csz[1].split()) == 1:
                    state = csz[1].split()[0]
                    zipp = "<MISSING>"
                else:
                    state = csz[1].split()[0]
                    zipp = csz[1].split()[-1]

        elif len(add_list) == 5:
            if add_list[0] == " 3341 Lexington Road":
                continue
            else:
                location_name = add_list[0].strip()
                street_address = add_list[2].strip()
                city = add_list[3].split(",")[0].strip()
                try:
                    state = add_list[3].split(",")[1].split()[0].strip()
                except:
                    state = add_list[1].split(",")[1].split()[0].strip()
                try:
                    zipp = add_list[3].split(",")[1].split()[-1].strip()
                except:
                    zipp = add_list[1].split(",")[1].split()[-1].strip()
        else:
            continue
        phone_list = re.findall(
            re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),
            info.split("message:")[-1],
        )
        if phone_list:
            phone = phone_list[0].strip()
        else:
            phone = "<MISSING>"
        hours = " ".join(info.split("message:")[-1].split("<br />")[-2:]).split("<br>")

        if "Check for " in " ".join(hours) or "Call for" in " ".join(hours):
            hours_of_operation = "<MISSING>"
        else:

            if len(hours) == 2:
                hours_of_operation = hours[0].strip()
            else:
                hours_list = hours[1].strip()
                if hours_list.split():

                    if len(hours_list.split()) > 1:
                        p = re.findall(
                            re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),
                            str(hours_list),
                        )
                        if not p:
                            hours_of_operation = hours_list
                        else:
                            p1 = "".join(p)
                            h = hours_list.split(p1)[-1].split()
                            if not h:
                                hours_of_operation = "<MISSING>"
                            else:
                                hours_of_operation = hours_list.split(p1)[-1].strip()

                    else:
                        hours_of_operation = "<MISSING>"
                else:
                    hours_of_operation = "<MISSING>"

        if (
            location_name == "Temecula - Promenade Mall"
            or location_name == "Victoria Gardens"
            or location_name == "Delaware"
        ):
            continue
        else:
            location_name = location_name.split("(")[0]
            street_address = (
                street_address.replace(" (by Burt Bros.)", "")
                .replace(" (Fresh Market Parking Lot)", "")
                .replace("(Down East Lot)", "")
                .replace("(Near Honeybaked Ham) ", "")
                .replace("(Dominos Parking Lot) ", "")
                .replace("(Inside Walmart) ", "")
                .replace("  (Fresh Market)", "")
                .replace(" (Ft. Union Blvd)", "")
            )
            store = [
                locator_domain,
                location_name,
                street_address,
                city,
                state,
                zipp,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
                page_url,
            ]
            store = [
                "<MISSING>" if x == "" or x is None or x == "." else x for x in store
            ]

        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
