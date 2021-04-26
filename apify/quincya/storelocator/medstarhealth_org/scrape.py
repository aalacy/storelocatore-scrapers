import csv
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
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
            ]
        )
        # Body
        for row in data:
            if row:
                writer.writerow(row)


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    url = "https://www.medstarhealth.org/mhs/our-locations/"

    session = SgRequests()
    req = session.get(url, headers=headers)
    soup = BeautifulSoup(req.content, "html.parser")

    all_scripts = soup.find_all("script")
    for script in all_scripts:
        if "maps.LatLng" in str(script):
            script = str(script).replace("\\", "")
            break

    data = []
    found = []

    items = script.split("google.maps.LatLng")
    locator_domain = "medstarhealth.org"

    for item in items:
        if ',title:"' in item:
            location_name = (
                item.split('title:"')[1].split('",click')[0].replace("amp;", "").strip()
            )
            country_code = "US"

            store_number = "<MISSING>"
            location_type = "<MISSING>"

            geo = re.findall(r"[0-9]{2}\.[0-9]+, -[0-9]{2,3}\.[0-9]+", item)[0].split(
                ","
            )
            latitude = geo[0].strip()
            longitude = geo[1].strip()

            try:
                link = (
                    item.split('href="')[1]
                    .split('"')[0]
                    .replace("hhttps", "https")
                    .strip()
                )
                if link[-2:] == "//":
                    link = link[:-1]
            except:
                link = "<MISSING>"

            hours_of_operation = "<INACCESSIBLE>"

            done = False

            if link != "<MISSING>" and "www.medstarhealth.org/mhs" in link:
                req = session.get(link, headers=headers)
                soup = BeautifulSoup(req.content, "html.parser")
                raw_hours = soup.find(class_="well").find_all("h4")
                for raw_hour in raw_hours:
                    if (
                        "hours of op" in raw_hour.text.lower()
                        or "office hours" in raw_hour.text.lower()
                    ):
                        hours = " ".join(
                            list(raw_hour.find_next_sibling().stripped_strings)
                        )
                        if "day" in hours or "p.m" in hours:
                            hours_of_operation = hours
                        break

                try:
                    try:
                        raw_address = list(soup.find(class_="well").h3.stripped_strings)
                    except:
                        raw_address = list(soup.find(class_="well").h4.stripped_strings)
                    if len(raw_address) < 2:
                        raw_address = list(
                            soup.find_all(class_="well")[1].h4.stripped_strings
                        )
                        raw_address = item.split("<br>")[1:-1]
                        phone = raw_address[-1].strip()
                    else:
                        try:
                            phone = (
                                soup.find(class_="well").h2.text.split(":")[1].strip()
                            )
                        except:
                            phone = "<MISSING>"

                    if "directions" in raw_address[-1].lower():
                        raw_address.pop(-1)

                    street_address = raw_address[-2].strip()

                    if len(raw_address) > 2 and not street_address[:1].isdigit():
                        street_address = " ".join(raw_address[:-1]).strip()
                    city = raw_address[-1].split(",")[0].strip()
                    state = raw_address[-1].split(",")[1].split()[0].strip()
                    try:
                        zip_code = raw_address[-1].split(",")[1].split()[1].strip()
                    except:
                        zip_code = raw_address[-1].strip()

                    done = True
                except:
                    pass

            if not done:
                raw_address = (
                    ",".join(item.replace("MD<br>", "MD ").split("<br />")[1:-1])
                    .replace(",<b", "")
                    .replace("705t", "705")
                    .split(",")
                )

                if not raw_address[0]:
                    raw_address = item.split("<br>")[1:-1]
                    try:
                        zip_code = raw_address[1].split(",")[-1].split()[1].strip()
                    except:
                        if raw_address[-2].strip().isnumeric():
                            zip_code = raw_address[-2].strip()
                            raw_address.pop(-2)
                        else:
                            if not raw_address[0][:1].isnumeric():
                                raw_address.pop(0)
                    phone = raw_address[-1].strip()
                    street_address = raw_address[0].strip()

                    if len(raw_address) > 2:
                        street_address = " ".join(raw_address[:-2]).strip()
                        city = raw_address[-2].split(",")[0].strip()
                        state = raw_address[-2].split(",")[1].split()[0].strip()
                        if not zip_code.isdigit():
                            zip_code = raw_address[-2].split(",")[1].split()[1].strip()
                    else:
                        city = raw_address[1].split(",")[0].strip()
                        state = raw_address[1].split(",")[1].split()[0].strip()

                    if "-" not in phone:
                        try:
                            phone = re.findall(r"[\d]{3}-[\d]{3}-[\d]{4}", str(item))[0]
                        except:
                            phone = "<MISSING>"

                else:
                    if len(raw_address) == 1:
                        raw_address = (
                            ",".join(
                                item.replace("MD<br>", "MD ")
                                .split("</a><br>")[1]
                                .split("</div>")[0][:-4]
                                .split("<br>")
                            )
                            .replace(",<b", "")
                            .split(",")
                        )

                    try:
                        street_address = " ".join(raw_address[:-2]).strip()
                        city = raw_address[-2].strip()
                        state = raw_address[-1].split()[0].strip()
                        zip_code = raw_address[-1].split()[1].strip()
                    except:
                        street_address = " ".join(raw_address[:-3]).strip()
                        city = raw_address[-3].strip()
                        state = raw_address[-2].split()[0].strip()
                        try:
                            zip_code = raw_address[-2].split()[1].strip()
                        except:
                            zip_code = "<MISSING>"

                phone = raw_address[-1].strip()

            street_address = street_address.replace("Olney, MD 20832", "")
            street_address = (re.sub(" +", " ", street_address)).strip()
            state = state.replace("District", "DC")

            if ">" in street_address:
                street_address = street_address.split(">")[-1].strip()

            if "3455 Wilkens Avenue Suite 306" in street_address:
                street_address = "3455 Wilkens Avenue Suite 306"
                city = "Baltimore"
                state = "MD"

            if "18111 Prince Philip Drive" in street_address:
                city = "Olney"
                state = "MD"

            if "Dorsey Hall Medical Center" in street_address:
                street_address = "9501 Old Annapolis Road Suite 220"
                city = "Washington"

            if "MedStar Georgetown University Hospital" in street_address:
                street_address = "3800 Reservoir Road, NW"
                city = "Washington"
                state = "DC"

            if "201 East University Parkway" in street_address:
                city = "Baltimore"

            if "4301 Connecticut Ave NW" in street_address:
                zip_code = "20008"

            if "MedStar Spine Center at Chevy Chase" in location_name:
                street_address = street_address + "Barlow Building, 11th Floor"
                zip_code = "20815"

            if "102 Irving Street Northwest" in street_address:
                zip_code = "20010"

            if city == "Rosedale":
                city = "Baltimore"
                state = "MD"

            if state == "MD20904t":
                state = "MD"
                zip_code = "20904"

            if "<br" in city:
                street_address = street_address + " " + city.split("<")[0].strip()
                city = city.split(">")[1].strip()

            if len(phone) > 12:
                try:
                    phone = re.findall(r"[\d]{3}-[\d]{3}-[\d]{4}", str(item))[0]
                except:
                    phone = "<MISSING>"

            if len(zip_code.strip()) != 5:
                try:
                    zip_code = (
                        re.findall(r"[\d]{5}<", str(item))[0].replace("<", "").strip()
                    )
                except:
                    zip_code = "<MISSING>"

            if link == "<MISSING>":
                hours_of_operation = "<MISSING>"

            if location_name == "MedStar Health at Mitchellville":
                street_address = "12158 Central Avenue"

            if not street_address[:1].isdigit():
                digit = re.search(r"\d", street_address).start(0)
                if digit != 0:
                    street_address = street_address[digit:]

            if location_name + street_address in found:
                continue
            found.append(location_name + street_address)

            data.append(
                [
                    locator_domain,
                    link,
                    location_name,
                    street_address,
                    city,
                    state,
                    zip_code,
                    country_code,
                    store_number,
                    phone,
                    location_type,
                    latitude,
                    longitude,
                    hours_of_operation,
                ]
            )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
