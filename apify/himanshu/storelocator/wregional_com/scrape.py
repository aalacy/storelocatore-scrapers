import csv
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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
    adressess = []
    locator_domain = "https://www.wregional.com"
    base_url = "https://www.wregional.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    rr = session.get("https://www.wregional.com/main/dialysis-centers", headers=headers)
    soup0 = BeautifulSoup(rr.text, "lxml")
    full = (
        str(soup0.find("div", {"class": "clinics"}))
        .split("</h3>")[-1]
        .split("</strong>")
    )
    names = []
    names = soup0.find_all("strong")
    names.insert(0, "")
    for index, f in enumerate(full):
        soups = BeautifulSoup(f, "lxml")
        full1 = list(soups.stripped_strings)
        if len(full1) != 1:
            address1 = full1[:-1][0]
            location_name = names[index].text.strip()
            city = full1[:-1][1].split(",")[0]
            state = full1[:-1][1].split(",")[1].strip().split()[0]
            zipcode = full1[:-1][1].split(",")[1].strip().split()[-1]
            phone = full1[:-1][3].replace("Phone ", "")
            hours = (
                " ".join(full1[:-1][5:])
                .replace("or later as needed for patient care", "")
                .replace("(will soon open Tuesday, Thursday, Saturday)", "")
                .replace("or later as needed for patient care", "")
                .replace("Sick call is available", "")
                .replace("The Women and Infants Center clinic is  ", "")
                .replace("Total Spine is  ", "")
                .replace(
                    "  other clinic locations vary. For more information, please call 479-463-8740 .",
                    "",
                )
            )
            location_type = "Facilities"
            store_number = "<MISSING>"
            country_code = "US"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours = (
                hours.replace(
                    "  other clinic locations vary. For more information, please call 479-463-8740 .",
                    "",
                )
                .replace(" Sick call is available", ",")
                .replace(" (or until full).", "")
            )
            store = [
                locator_domain,
                location_name,
                address1,
                city,
                state,
                zipcode,
                country_code,
                store_number,
                phone.strip(),
                "Facilities",
                latitude,
                longitude,
                hours,
                "https://www.wregional.com/main/dialysis-centers",
            ]
            store = [x.replace("–", "-") if type(x) == str else x for x in store]
            store = [x.strip() if type(x) == str else x for x in store]

            yield store

    urls = [
        "https://www.wregional.com/main/sleep-disorders",
        "https://www.wregional.com/main/springdale-center-for-health",
        "https://www.wregional.com/main/medical-plaza",
    ]
    for index, u in enumerate(urls):
        u1 = session.get(u, headers=headers)
        soupp = BeautifulSoup(u1.text, "lxml")
        if index == 0:
            full = list(
                soupp.find("div", {"class": "clinics"})
                .find_all("p")[-1]
                .stripped_strings
            )
            location_name = full[0]
            address1 = full[1]
            city = full[2].split(",")[0]
            zipcode = full[2].split(",")[1].strip().split()[-1]
            state = full[2].split(",")[1].strip().split()[-2]
            phone = full[4].replace("Phone ", "")
            hours = "<MISSING>"
        if index == 1:
            full = list(
                soupp.find("main", {"id": "inside-page"})
                .find("div", {"class": "page-content"})
                .find_all("p")[-2]
                .stripped_strings
            )
            location_name = full[0]
            address1 = full[1]
            city = full[2].split(",")[0]
            zipcode = full[2].split(",")[1].strip().split()[-1]
            state = full[2].split(",")[1].strip().split()[-2]
            hours = (
                full[-2]
                .replace("open", "")
                .replace("Sick call is available", "-")
                .replace("The Women and Infants Center clinic is  ", "")
                .replace("Total Spine is  ", "")
                .replace(
                    "  other clinic locations vary. For more information, please call 479-463-8740 .",
                    "",
                )
            )
            phone = "479-463-5464"
        if index == 2:
            full = str(
                soupp.find("main", {"id": "inside-page"}).find(
                    "div", {"class": "page-content"}
                )
            ).split("</strong>")[-1]
            location_name = soupp.find("strong").text
            soupp = BeautifulSoup(full, "lxml")
            address1 = list(soupp.stripped_strings)[0]
            city = list(soupp.stripped_strings)[1].split(",")[0]
            state = list(soupp.stripped_strings)[1].split(",")[1].strip().split()[0]
            zipcode = list(soupp.stripped_strings)[1].split(",")[1].strip().split()[1]
            phone = "<MISSING>"
            hours = "<MISSING>"
        store_number = "<MISSING>"
        country_code = "US"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours = (
            hours.replace(
                "  other clinic locations vary. For more information, please call 479-463-8740 .",
                "",
            )
            .replace(" Sick call is available", ",")
            .replace(" (or until full).", "")
        )
        store = [
            locator_domain,
            location_name,
            address1.split("(")[0].strip(),
            city,
            state,
            zipcode,
            country_code,
            store_number,
            phone.strip(),
            "Facilities",
            latitude,
            longitude,
            hours,
            u,
        ]
        store = [x.replace("–", "-") if type(x) == str else x for x in store]
        store = [x.strip() if type(x) == str else x for x in store]

        yield store

    r = session.get(
        "https://www.wregional.com/main/find-a-facility-or-clinic", headers=headers
    )
    soup = BeautifulSoup(r.text, "lxml")
    for ul in soup.find("div", class_="template2-row-1").find_all("ul"):
        location_type = ul.parent.parent.find("h3").text.strip()
        for li in ul.find_all("li"):
            if "http" in li.find("a")["href"]:
                page_url = li.find("a")["href"]
            elif "/" not in li.find("a")["href"]:
                page_url = "https://www.wregional.com/main/" + li.find("a")["href"]
            else:
                page_url = "https://www.wregional.com" + li.find("a")["href"]
            location_name = li.find("a").text.strip()
            r1 = session.get(page_url, headers=headers)
            soup1 = BeautifulSoup(r1.text, "lxml")
            hours = ""
            try:
                full_address = list(
                    soup1.find("div", class_="clinics").find("p").stripped_strings
                )
                if "(" in full_address[1]:
                    del full_address[1]
                if len(full_address) >= 14:
                    split_address = "|".join(full_address).split("Map and Directions")
                    for add in split_address:
                        add_list = add.split("|")
                        add_list = [i for i in add_list if i]
                        if "Now Offering Televisits" not in add_list[0]:
                            if "(" in add_list[1]:
                                del add_list[1]
                            try:
                                int(add_list[0].strip()[0])
                                try:
                                    hours = (
                                        " ".join(
                                            list(
                                                soup1.find(
                                                    lambda tag: (tag.name == "h3")
                                                    and "Hours" in tag.text.strip()
                                                ).next_sibling.next_sibling.stripped_strings
                                            )
                                        )
                                        .split("Other clinic")[0]
                                        .replace("Hours at", "")
                                        .replace("\n", " ")
                                        .replace("Fayetteville:", "")
                                        .replace("Springdale", "")
                                        .split("The clinic is")[-1]
                                        .replace("The Fayetteville clinic is", "")
                                        .replace(
                                            "other clinic locations vary. For more information, please call 479-571-4338.",
                                            "",
                                        )
                                        .replace(
                                            "The Fayetteville clinic at the Pat Walker Center for Seniors is",
                                            "",
                                        )
                                        .replace(
                                            "Our clinic on the Lincoln Square is", ""
                                        )
                                        .replace("The  clinic is", "")
                                        .replace("open", "")
                                        .replace(
                                            " The school-based clinic located on the Lincoln Middle School Campus is  ",
                                            ",",
                                        )
                                        .replace(
                                            " The  Center for Health clinic is  from ",
                                            ",",
                                        )
                                        .replace(
                                            "The Women and Infants Center clinic is  ",
                                            "",
                                        )
                                        .replace("Total Spine is  ", "")
                                        .replace(
                                            "  other clinic locations vary. For more information, please call 479-463-8740 .",
                                            "",
                                        )
                                        .replace("Sick call is available ", "")
                                        .replace("The Home is", "")
                                    )
                                except:
                                    hours = "<MISSING>"
                                address01 = add_list[0]
                                city = add_list[1].split(",")[0]
                                state = add_list[1].split(",")[1].strip().split()[0]
                                zipp = add_list[1].split(",")[1].strip().split()[1]
                                phone_tag = add_list[2].replace("Telephone:", "")
                                phone_list = re.findall(
                                    re.compile(
                                        r"(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})"
                                    ),
                                    str(phone_tag),
                                )
                                if phone_list:
                                    phone = phone_list[0]
                                else:
                                    phone = "<MISSING>"
                                store_number = "<MISSING>"
                                country_code = "US"
                                latitude = "<MISSING>"
                                longitude = "<MISSING>"
                                hours = (
                                    hours.replace(
                                        "  other clinic locations vary. For more information, please call 479-463-8740 .",
                                        "",
                                    )
                                    .replace(" Sick call is available", ",")
                                    .replace(" (or until full).", "")
                                    .replace("The Home is", "")
                                )
                                store = [
                                    locator_domain,
                                    location_name,
                                    address01,
                                    city,
                                    state,
                                    zipp,
                                    country_code,
                                    store_number,
                                    phone.replace("Phone: ", "").strip(),
                                    location_type,
                                    latitude,
                                    longitude,
                                    hours.strip(),
                                    page_url,
                                ]
                                store = [
                                    x.replace("–", "-") if type(x) == str else x
                                    for x in store
                                ]
                                store = [
                                    x.strip() if type(x) == str else x for x in store
                                ]
                                yield store
                            except:
                                try:
                                    hours = (
                                        " ".join(
                                            list(
                                                soup1.find(
                                                    lambda tag: (tag.name == "h3")
                                                    and "Hours" == tag.text.strip()
                                                ).nextSibling.next_sibling.stripped_strings
                                            )
                                        )
                                        .split("Other clinic")[0]
                                        .replace("Hours at", "")
                                        .replace("\n", " ")
                                        .replace("Fayetteville:", "")
                                        .replace("Springdale", "")
                                        .split("The clinic is")[-1]
                                        .replace("The Fayetteville clinic is", "")
                                        .replace(
                                            "other clinic locations vary. For more information, please call 479-571-4338.",
                                            "",
                                        )
                                        .replace(
                                            "The Fayetteville clinic at the Pat Walker Center for Seniors is",
                                            "",
                                        )
                                        .replace(
                                            "Our clinic on the Lincoln Square is", ""
                                        )
                                        .replace("The  clinic is", "")
                                        .replace("open", "")
                                        .replace("Sick call is available Monday ", "-")
                                        .replace(
                                            " The school-based clinic located on the Lincoln Middle School Campus is  ",
                                            ",",
                                        )
                                        .replace(
                                            " The  Center for Health clinic is  from ",
                                            ",",
                                        )
                                        .replace(
                                            "The Women and Infants Center clinic is  ",
                                            "",
                                        )
                                        .replace("Total Spine is  ", "")
                                        .replace(
                                            "  other clinic locations vary. For more information, please call 479-463-8740 .",
                                            "",
                                        )
                                        .replace("Sick call is available ", "")
                                        .replace("The Home is", "")
                                    )
                                except:
                                    hours = "<MISSING>"
                                address01 = add_list[1]
                                city = add_list[2].split(",")[0]
                                state = add_list[2].split(",")[1].strip().split()[0]
                                zipp = add_list[2].split(",")[1].strip().split()[1]
                                phone_tag = add_list[4].replace("Telephone:", "")
                                phone_list = re.findall(
                                    re.compile(
                                        r"(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})"
                                    ),
                                    str(phone_tag),
                                )
                                if phone_list:
                                    phone = phone_list[0]
                                else:
                                    phone = "<MISSING>"
                                store_number = "<MISSING>"
                                country_code = "US"
                                latitude = "<MISSING>"
                                longitude = "<MISSING>"
                                hours = (
                                    hours.replace(
                                        "  other clinic locations vary. For more information, please call 479-463-8740 .",
                                        "",
                                    )
                                    .replace(" Sick call is available", ",")
                                    .replace(" (or until full).", "")
                                    .replace("The Home is", "")
                                )
                                store = [
                                    locator_domain,
                                    location_name,
                                    address01,
                                    city,
                                    state,
                                    zipp,
                                    country_code,
                                    store_number,
                                    phone.replace("Phone: ", "").strip(),
                                    location_type,
                                    latitude,
                                    longitude,
                                    hours.strip(),
                                    page_url,
                                ]
                                store = [
                                    x.replace("–", "-") if type(x) == str else x
                                    for x in store
                                ]
                                store = [
                                    x.strip() if type(x) == str else x for x in store
                                ]
                                yield store
                else:
                    try:
                        int(full_address[0].strip()[0])
                        try:
                            hours = (
                                " ".join(
                                    list(
                                        soup1.find(
                                            lambda tag: (tag.name == "h3")
                                            and "Hours" in tag.text.strip()
                                        ).next_sibling.next_sibling.stripped_strings
                                    )
                                )
                                .split("Other clinic")[0]
                                .replace("Hours at", "")
                                .replace("\n", " ")
                                .replace("Fayetteville:", "")
                                .replace("Springdale", "")
                                .split("The clinic is")[-1]
                                .replace("The Fayetteville clinic is", "")
                                .replace(
                                    "other clinic locations vary. For more information, please call 479-571-4338.",
                                    "",
                                )
                                .replace(
                                    "The Fayetteville clinic at the Pat Walker Center for Seniors is",
                                    "",
                                )
                                .replace("Our clinic on the Lincoln Square is", "")
                                .replace("The  clinic is", "")
                                .replace("open", "")
                                .replace(
                                    " The school-based clinic located on the Lincoln Middle School Campus is  ",
                                    ",",
                                )
                                .replace(
                                    " The  Center for Health clinic is  from ", ","
                                )
                                .replace("The Women and Infants Center clinic is  ", "")
                                .replace("Total Spine is  ", "")
                                .replace(
                                    "  other clinic locations vary. For more information, please call 479-463-8740 .",
                                    "",
                                )
                                .replace("Sick call is available ", "")
                                .replace("The Home is", "")
                            )
                        except:
                            hours = "<MISSING>"
                        address01 = full_address[0]
                        city = full_address[1].split(",")[0]
                        state = full_address[1].split(",")[1].strip().split()[0]
                        zipp = full_address[1].split(",")[1].strip().split()[1]
                        phone_tag = full_address[3].replace("Telephone:", "")
                        phone_list = re.findall(
                            re.compile(
                                r"(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})"
                            ),
                            str(phone_tag),
                        )
                        if phone_list:
                            phone = phone_list[0]
                        else:
                            phone = "<MISSING>"
                        store_number = "<MISSING>"
                        country_code = "US"
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                        hours = (
                            hours.replace(
                                "  other clinic locations vary. For more information, please call 479-463-8740 .",
                                "",
                            )
                            .replace(" Sick call is available", ",")
                            .replace(" (or until full).", "")
                            .replace("The Home is", "")
                        )
                        store = [
                            locator_domain,
                            location_name,
                            address01,
                            city,
                            state,
                            zipp,
                            country_code,
                            store_number,
                            phone.replace("Phone: ", "").strip(),
                            location_type,
                            latitude,
                            longitude,
                            hours.strip(),
                            page_url,
                        ]
                        store = [
                            x.replace("–", "-") if type(x) == str else x for x in store
                        ]
                        store = [x.strip() if type(x) == str else x for x in store]
                        yield store
                    except:
                        try:
                            hours = (
                                " ".join(
                                    list(
                                        soup1.find(
                                            lambda tag: (tag.name == "h3")
                                            and "Hours" == tag.text.strip()
                                        ).nextSibling.next_sibling.stripped_strings
                                    )
                                )
                                .split("Other clinic")[0]
                                .replace("Hours at", "")
                                .replace("\n", " ")
                                .replace("Fayetteville:", "")
                                .replace("Springdale", "")
                                .split("The clinic is")[-1]
                                .replace("The Fayetteville clinic is", "")
                                .replace(
                                    "other clinic locations vary. For more information, please call 479-571-4338.",
                                    "",
                                )
                                .replace(
                                    "The Fayetteville clinic at the Pat Walker Center for Seniors is",
                                    "",
                                )
                                .replace("Our clinic on the Lincoln Square is", "")
                                .replace("The  clinic is", "")
                                .replace("open", "")
                                .replace(
                                    " The school-based clinic located on the Lincoln Middle School Campus is  ",
                                    ",",
                                )
                                .replace(
                                    " The  Center for Health clinic is  from ", ","
                                )
                                .replace("The Women and Infants Center clinic is  ", "")
                                .replace("Total Spine is  ", "")
                                .replace(
                                    "  other clinic locations vary. For more information, please call 479-463-8740 .",
                                    "",
                                )
                                .replace("Sick call is available ", "")
                                .replace("The Home is", "")
                            )
                        except:
                            hours = "<MISSING>"
                        address01 = full_address[1]
                        city = full_address[2].split(",")[0]
                        state = full_address[2].split(",")[1].strip().split()[0]
                        zipp = full_address[2].split(",")[1].strip().split()[1]
                        phone_tag = full_address[4].replace("Telephone:", "")
                        phone_list = re.findall(
                            re.compile(
                                r"(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})"
                            ),
                            str(phone_tag),
                        )
                        if phone_list:
                            phone = phone_list[0]
                        else:
                            phone = "<MISSING>"
                        store_number = "<MISSING>"
                        country_code = "US"
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                        hours = (
                            hours.replace(
                                "  other clinic locations vary. For more information, please call 479-463-8740 .",
                                "",
                            )
                            .replace(" Sick call is available", ",")
                            .replace(" (or until full).", "")
                            .replace("The Home is", "")
                        )
                        store = [
                            locator_domain,
                            location_name,
                            address01,
                            city,
                            state,
                            zipp,
                            country_code,
                            store_number,
                            phone.strip(),
                            location_type,
                            latitude,
                            longitude,
                            hours.strip(),
                            page_url,
                        ]
                        store = [
                            x.replace("–", "-") if type(x) == str else x for x in store
                        ]
                        store = [x.strip() if type(x) == str else x for x in store]
                        yield store
            except:
                pass
    prime_urls = [
        "https://www.wregional.com/main/primary-care-fayetteville",
        "https://www.wregional.com/main/primary-care-harrison",
        "https://www.wregional.com/main/primary-care-springdale",
    ]
    for link in prime_urls:
        prime_r = session.get(link, headers=headers)
        prime_soup = BeautifulSoup(prime_r.text, "lxml")
        col = prime_soup.find("div", {"class": "col-1"}).find_all("h2")
        for i in col:
            page_url = i.find("a")["href"]
            if (
                "https://www.wregional.com/senior-health/senior-health-clinic"
                in page_url
            ):
                continue
            page_r = session.get(page_url, headers=headers)
            page_soup = BeautifulSoup(page_r.text, "lxml")
            col2 = list(page_soup.find("div", {"class": "col-2"}).stripped_strings)
            if len(col2) == 9:
                location_name = col2[0]
                street_address = col2[2]
                city = col2[3].split(",")[0]
                state = col2[3].split(",")[1].strip().split(" ")[0]
                zipp = col2[3].split(",")[1].strip().split(" ")[-1]
                store_number = "<MISSING>"
                phone = col2[5]
            else:
                try:
                    location_name = col2[0]
                    street_address = col2[1]
                    city = col2[2].split(",")[0]
                    state = col2[2].split(",")[1].strip().split(" ")[0]
                    zipp = col2[2].split(",")[1].strip().split(" ")[-1]
                    store_number = "<MISSING>"
                    phone = col2[4]
                except:
                    col2 = page_soup.find(class_="site-info").center.text.split("|")
                    street_address = col2[0].strip()
                    city = col2[1].split(",")[0].strip()
                    state = col2[1].split(",")[1].strip()
                    zipp = col2[1].split(",")[2].strip()
                    store_number = "<MISSING>"
                    phone = col2[2].strip()
            if location_name == "Primary Care - Main Sreet":
                phone = "870.741.3592"
            try:
                hours_of_operation = (
                    page_soup.find_all("p", text=re.compile("clinic is open"))[0]
                    .text.replace("\n", ", ")
                    .replace("The clinic is open", "")
                    .replace("Sick call is available ", ",")
                    .replace(
                        "located on the Lincoln Middle School Campus is open ", "-"
                    )
                    .replace(
                        " The school-based clinic located on the Lincoln Middle School Campus is  ",
                        ",",
                    )
                    .replace(" The  Center for Health clinic is  from ", ",")
                    .replace(
                        "  other clinic locations vary. For more information, please call 479-463-8740 .",
                        "",
                    )
                    .replace("Sick call is available ", "")
                    .strip()
                )

            except:
                hours_of_operation = "Monday - Friday 8:00 a.m. - 4:30 p.m."
            location_type = "Primary Care Clinics"
            try:
                map_url = page_soup.find("div", {"class": "col-2"}).find_all(
                    "a", {"target": "_blank"}
                )[1]["href"]
            except:
                try:
                    map_url = page_soup.find("div", {"class": "col-2"}).find_all(
                        "a", {"target": "_blank"}
                    )[0]["href"]
                except:
                    map_url = page_soup.find(class_="site-info").a["href"]
            coords = session.get(map_url).url

            if "/@" in coords:
                lat = coords.split("/@")[1].split(",")[0]
                lng = coords.split("/@")[1].split(",")[1]
            else:
                map_soup = BeautifulSoup(session.get(map_url).text, "lxml")
                file_name = open("data.txt", "w", encoding="utf-8")
                file_name.write(str(map_soup))
                try:
                    map_href = map_soup.find(
                        "a", {"href": re.compile("https://maps.google.com/maps?")}
                    )["href"]
                    lat = (
                        str(BeautifulSoup(session.get(map_href).text, "lxml"))
                        .split("/@")[1]
                        .split(",")[0]
                    )
                    lng = (
                        str(BeautifulSoup(session.get(map_href).text, "lxml"))
                        .split("/@")[1]
                        .split(",")[1]
                    )
                except:
                    lat = str(map_soup).split("/@")[1].split(",")[0]
                    lng = str(map_soup).split("/@")[1].split(",")[1]
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append(store_number)
            store.append(phone)
            store.append(location_type)
            store.append(lat)
            store.append(lng)
            store.append(hours_of_operation)
            store.append(page_url)
            store = [x.replace("–", "-") if type(x) == str else x for x in store]
            store = [x.strip() if type(x) == str else x for x in store]
            if store[2] in adressess:
                continue
            adressess.append(store[2])
            yield store
    health_r = session.get(
        "https://www.wregional.com/senior-health/senior-health-clinic", headers=headers
    )
    health_soup = BeautifulSoup(health_r.text, "lxml")
    col2 = list(health_soup.find("div", {"class": "col-2"}).stripped_strings)
    data1 = col2[:8]
    data2 = col2[8:]
    now_list = [data1, data2]
    for data_list in now_list:
        location_name = data_list[0]
        street_address = data_list[2]
        city = data_list[3].split(",")[0]
        state = data_list[3].split(",")[1].strip().split(" ")[0]
        zipp = data_list[3].split(",")[1].strip().split(" ")[1]
        store_number = "<MISSING>"
        phone = data_list[5]
        page_url = "https://www.wregional.com/senior-health/senior-health-clinic"
        if city == "Fayetteville":
            hours_of_operation = "Monday - Thursday, 8:00 a.m. - 4:30 p.m. and Friday 8:00 a.m. - 2:00 p.m."
            map_url = "https://goo.gl/maps/o8M1FBZcgx72"
        if city == "Springdale":
            hours_of_operation = "Monday - Thursday, 8:00 a.m. - 4:30 p.m."
            map_url = "https://goo.gl/maps/BXQVnv7GDM42"
        coords = session.get(map_url).url
        if "/@" in coords:
            lat = coords.split("/@")[1].split(",")[0]
            lng = coords.split("/@")[1].split(",")[1]
        else:
            map_soup = BeautifulSoup(session.get(map_url).text, "lxml")
            file_name = open("data.txt", "w", encoding="utf-8")
            file_name.write(str(map_soup))
            try:
                map_href = map_soup.find(
                    "a", {"href": re.compile("https://maps.google.com/maps?")}
                )["href"]
                lat = (
                    str(BeautifulSoup(session.get(map_href).text, "lxml"))
                    .split("/@")[1]
                    .split(",")[0]
                )
                lng = (
                    str(BeautifulSoup(session.get(map_href).text, "lxml"))
                    .split("/@")[1]
                    .split(",")[1]
                )
            except:
                lat = str(map_soup).split("/@")[1].split(",")[0]
                lng = str(map_soup).split("/@")[1].split(",")[1]
        location_type = "Senior Health Clinic"
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(lat)
        store.append(lng)
        store.append(hours_of_operation)
        store.append(page_url)
        store = [x.replace("–", "-") if type(x) == str else x for x in store]
        store = [x.strip() if type(x) == str else x for x in store]
        if store[2] in adressess:
            continue
        adressess.append(store[2])
        yield store
    urgent = [
        "https://www.urgentteam.com/locations/washington-regional-urgent-care-bentonville-ar/",
        "https://www.urgentteam.com/locations/washington-regional-urgent-care-fayetteville-ar/",
        "https://www.urgentteam.com/locations/washington-regional-urgent-care-harrison-ar/",
        "https://www.urgentteam.com/locations/washington-regional-urgent-care-rogers-ar/",
        "https://www.urgentteam.com/locations/washington-regional-urgent-care-springdale-ar/",
    ]
    for dl in urgent:
        page_url = session.get(dl, headers=headers)
        urgent_soup = BeautifulSoup(page_url.text, "lxml")
        location_name = urgent_soup.find(
            "h1", {"class": "o-location-hero__title u-h2"}
        ).text
        addr = list(
            urgent_soup.find_all("div", {"class": "m-location-panel__section"})[1]
            .find("p", {"class": "m-location-panel__text"})
            .stripped_strings
        )
        street_address = addr[0].strip(",")
        city = addr[1].split(",")[0]
        state = addr[1].split(",")[1].strip().split(" ")[0]
        zipp = addr[1].split(",")[1].strip().split(" ")[1]
        phone = urgent_soup.find("a", {"class": "m-location-panel__phone"}).text
        hours_of_operation = " ".join(
            list(
                urgent_soup.find(
                    "ul", {"class": "m-location-hours__list"}
                ).stripped_strings
            )
        )
        location_type = "Urgent Care"
        store_number = "<MISSING>"
        lat = "<MISSING>"
        lng = "<MISSING>"
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(lat)
        store.append(lng)
        store.append(hours_of_operation)
        store.append(dl)
        store = [x.replace("–", "-") if type(x) == str else x for x in store]
        store = [x.strip() if type(x) == str else x for x in store]
        if store[2] in adressess:
            continue
        adressess.append(store[2])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
