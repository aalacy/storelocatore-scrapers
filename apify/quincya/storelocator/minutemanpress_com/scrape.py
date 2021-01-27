import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests


logger = SgLogSetup().get_logger("minutemanpress.com")


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
            writer.writerow(row)


def fetch_data():

    base_links = [
        "https://www.minutemanpress.com/locations/locations.html/ca",
        "https://www.minutemanpress.com/locations/locations.html/us",
    ]

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    data = []
    found = []
    locator_domain = "minutemanpress.com"

    for base_link in base_links:
        req = session.get(base_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        if "/us" in base_link:
            country_code = "US"
        else:
            country_code = "CA"

        items = base.find(class_="mmp-corp-store-search-filter-options").find_all(
            "form"
        )

        for item in items:
            page = 1

            for i in range(20):
                next_link = item["action"] + "?page=%s" % page
                logger.info(next_link)

                req = session.get(next_link, headers=headers)
                next_base = BeautifulSoup(req.text, "lxml")

                final_items = next_base.find_all(class_="mmp-store")
                for final_item in final_items:

                    raw_address = list(
                        final_item.find(class_="mmp-store__address").stripped_strings
                    )
                    location_name = raw_address[0].strip()
                    street_address = " ".join(raw_address[1:-1]).strip()
                    if street_address[-1:] == ",":
                        street_address = street_address[:-1].strip()
                    city_line = raw_address[-1].strip().split(",")
                    city = city_line[0].strip()
                    if country_code == "US":
                        state = city_line[1].strip()[:-6].strip()
                        zip_code = city_line[1].strip()[-6:].strip()
                    else:
                        state = city_line[1].strip()[:-7].strip()
                        zip_code = city_line[1].strip()[-7:].strip()
                    if "-" in zip_code:
                        zip_code = state[-4:] + zip_code
                        state = state[:-4].strip()
                    store_number = "<MISSING>"
                    location_type = "<MISSING>"
                    phone = final_item.find(class_="mmp-store__phone").text.strip()

                    zip_orig = zip_code
                    street_orig = street_address

                    try:
                        link = final_item.find(class_="visit-website button")["href"]
                        if link in found:
                            continue
                        found.append(link)
                        req = session.get(link, headers=headers)
                        base = BeautifulSoup(req.text, "lxml")

                        try:
                            street_address = base.find(
                                class_="location-address location-address--1"
                            ).text.strip()
                        except:
                            pass

                        try:
                            city_line = base.find(
                                class_="location-address location-address--2"
                            ).text.strip()
                            if "," in city_line:
                                if country_code == "US":
                                    zip_code = city_line.strip().split()[-1].strip()
                                else:
                                    zip_code = city_line.strip()[-7:].strip()
                            else:
                                if "(" not in city_line:
                                    street_address = (
                                        street_address + " " + city_line
                                    ).strip()
                                city_line = base.find(
                                    class_="location-address location-address--3"
                                ).text.strip()
                                if "," in city_line:
                                    if country_code == "US":
                                        zip_code = city_line.strip().split()[-1].strip()
                                    else:
                                        zip_code = city_line.strip()[-7:].strip()
                                else:
                                    street_address = street_orig
                                    zip_code = zip_orig
                        except:
                            pass

                        if country_code == "US":
                            if not zip_code[-4:].isdigit() or len(zip_code) < 5:
                                street_address = street_orig
                                zip_code = zip_orig
                        else:
                            if (
                                " " not in zip_code
                                or "," in zip_code
                                or len(zip_code.replace(" ", "").strip()) < 6
                            ):
                                street_address = street_orig
                                zip_code = zip_orig

                        if city in street_address:
                            street_address = street_orig

                        street_address = (
                            street_address.replace("See Below", "")
                            .replace("Tech Mart Commerce Center", "")
                            .replace("Minuteman Press", "")
                            .split("(")[0]
                            .split(", Philadelphia")[0]
                            .split(", North Arlington")[0]
                            .split(", HICKSVILLE")[0]
                            .split("Between")[0]
                            .split("(at Wood")[0]
                            .strip()
                        )

                        if "18 Technology Dr" in street_address:
                            zip_code = "92618"
                        if (
                            link == "http://www.mmpressfitchburg.com"
                            or "day -" in street_address
                            or "minuteman" in street_address.lower()
                        ):
                            street_address = street_orig
                        if (
                            link == "http://www.seekonk.minutemanpress.com"
                            or link == "http://www.minutemanbutler.com"
                            or link == "https://www.arlington.minutemanpress.com"
                        ):
                            street_address = street_orig
                            zip_code = zip_orig
                        if "3706 Mercer University" in street_address:
                            street_address = (
                                "3706 Mercer University Drive Mission Square, Suite 14"
                            )
                            zip_code = "31204"
                        if street_address == "123 South Main Street":
                            street_address = (
                                "123 South Main Street Highland Plaza, Unit 110"
                            )
                            zip_code = "06470"
                        if "After hours" in street_address:
                            street_address = street_orig
                            zip_code = zip_orig

                        street_address = (re.sub(" +", " ", street_address)).strip()

                        if not phone:
                            phone = base.find(
                                "span", attrs={"itemprop": "telephone"}
                            ).text.strip()

                        if location_name + street_address in found:
                            continue
                        found.append(location_name + street_address)

                        try:
                            hours_of_operation = (
                                base.find(class_="location__hours")
                                .text.strip()
                                .replace("\n", " ")
                                .replace("  ", " ")
                                .replace("Email:", "")
                                .replace("Email", "")
                                .replace("E-mail:", "")
                                .replace(
                                    "Serving Downtown, Midtown, Montrose, Museum District, Medical Center, and Greater Houston Area.",
                                    "",
                                )
                                .replace(
                                    "Free Pickup and Delivery to American Canyon, Benicia, and Fairfield as well as Vallejo.",
                                    "",
                                )
                                .replace(
                                    "We are open with shorter hours during the Covid pandemic.",
                                    "",
                                )
                                .replace(
                                    "Visit our website for pricing & ordering: www.beavercreekminutemanpress.com",
                                    "",
                                )
                                .replace(
                                    "For pricing & ordering, visit: www.CincinnatiMinutemanPress.com",
                                    "",
                                )
                                .replace("http://www.mmpcfl.com", "")
                                .replace("Minuteman Press Fort Worth ~ ", "")
                                .replace(" 24/7 Online", "")
                                .replace("Locally Owned and Operated Since 2009", "")
                                .replace("Free pick-up and delivery", "")
                                .replace("Free Parking Available", "")
                                .replace(
                                    "Renee Braund - Account Specialist - Where we appreciate your business!",
                                    "",
                                )
                                .replace("Located just off I-35 and Valley View.", "")
                                .replace(
                                    "We will make every effort to accommodate!", ""
                                )
                                .replace("Like us on Facebook:", "")
                                .replace("(Other times available by appointment)", "")
                                .replace("Corner of 114th and Halsey Hours:", "")
                                .replace(". :", "")
                                .replace("->Hours & Information:", "")
                                .replace('"Next to Wings Plus"', "")
                                .replace("CURRENT HOURS:", "")
                                .replace("Our hours of operation are", "")
                                .replace("Over 30 years of experience •", "")
                                .replace("We open", "")
                                .replace("Our Hours are:", "")
                                .replace("Operation Hours:", "")
                                .replace("Business Hours:", "")
                                .replace("Office Hours -", "")
                                .replace("The Store is typically open:", "")
                                .replace(" Business Hours:", "")
                                .replace("Hours of Operation:", "")
                                .replace("Hours of Operation", "")
                                .replace("Thank You!", "")
                                .replace(". :", "")
                                .strip()
                                .split("www")[0]
                                .split("| Like")[0]
                                .split("_visit our")[0]
                                .split(", We can")[0]
                                .split("Directly across")[0]
                                .split("If you would")[0]
                                .split("Please contact")[0]
                                .split("-- Min")[0]
                                .split("Post office")[0]
                                .split("For Quote")[0]
                                .split("Printing-")[0]
                                .split("Our web")[0]
                                .split("· Click here")[0]
                                .split("Other hours")[0]
                                .split("Check us")[0]
                                .split("| Please stop")[0]
                            ).strip()

                            if (
                                "301 East Montgomery Ave" in hours_of_operation
                                or "87th Avenue to SW" in hours_of_operation
                                or "Browse all" in hours_of_operation
                            ):
                                hours_of_operation = "<MISSING>"
                        except:
                            hours_of_operation = "<MISSING>"

                        if link == "http://www.noblesville-in.minutemanpress.com":
                            zip_code = "46062"
                            state = "Indiana"
                    except:
                        link = "<MISSING>"
                        hours_of_operation = "<MISSING>"
                    hours_of_operation = re.sub(
                        r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})",
                        r"",
                        hours_of_operation,
                    )
                    hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()

                    if not hours_of_operation:
                        hours_of_operation = "<MISSING>"

                    if not phone:
                        phone = "<MISSING>"

                    latitude = "<MISSING>"
                    longitude = "<MISSING>"

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

                if next_base.find(class_="nav--pagination__next"):
                    page += 1
                else:
                    break
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
