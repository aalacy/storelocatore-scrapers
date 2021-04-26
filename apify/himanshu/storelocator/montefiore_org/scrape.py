import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("montefiore_org")

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf-8") as output_file:
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
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    base_url = "https://www.montefiore.org"
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    page_url = ""
    addresses = []
    temp = []

    #################################################################################

    location_url1 = "https://www.montefiore.org/westchester-square-campus"
    base_url = "https://www.montefiore.org/"
    r = session.get(location_url1, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find("div", {"class": "content"}).find_all("p")[1]
    data1 = soup.find("div", {"class": "content"}).find_all("p")[2]
    phone = list(data.stripped_strings)[-1]
    zipp = list(data.stripped_strings)[-3].split(" ")[-1]
    state = (list(data.stripped_strings)[-3].split(" ")[-2]).replace("10504", "")
    city = list(data.stripped_strings)[-3].split(" ")[0].replace(",", "")
    street_address = list(data.stripped_strings)[-4]
    location_name = list(data.stripped_strings)[0].strip()
    latitude = (
        data1.find("a")["href"].split("en&ll=")[1].split("&spn=")[0].split(",")[0]
    )
    longitude = (
        data1.find("a")["href"].split("en&ll=")[1].split("&spn=")[0].split(",")[1]
    )
    store = []
    store.append(base_url if base_url else "<MISSING>")
    store.append(location_name if location_name else "<MISSING>")
    store.append(street_address if street_address else "<MISSING>")
    store.append(city if city else "<MISSING>")
    store.append(state if state else "<MISSING>")
    store.append(zipp if zipp else "<MISSING>")
    store.append("US")
    store.append("<MISSING>")
    store.append(phone if phone else "<MISSING>")
    store.append("<MISSING>")
    store.append(latitude if latitude else "<MISSING>")
    store.append(longitude if longitude else "<MISSING>")
    store.append("<MISSING>")
    store.append(location_url1 if location_url1 else "<MISSING>")
    store = [str(x).strip() if x else "<MISSING>" for x in store]
    yield store
    location_url = "https://www.montefiore.org/cancer-contact"
    base_url = "https://www.montefiore.org/"
    r = session.get(location_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find("div", {"class": "content"})
    data2 = data.find("table")
    mp = data2.find_all("tr")
    for i in mp:
        mp1 = i.find_all("td")
        link = i.find("a")
        for j in mp1:
            full = list(j.stripped_strings)
            if len(full) != 1 and full != []:
                try:
                    data = int(full[0].strip()[0])
                    street_address = full[0]
                    city = full[1].split(",")[0]
                    state = full[1].split(",")[1].split()[0]
                    zipp = full[1].split(",")[1].split()[1]
                    phone = full[3]
                except:
                    street_address = full[1]
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                    if link is not None:
                        ku = link["href"].split("sll=")[-1].split("&sspn=")[0]
                        latitude = ku.split(",")[0].replace(
                            "http://goo.gl/maps/Hdejr", "<MISSING>"
                        )
                        longitude = ku.split(",")[-1].replace(
                            "http://goo.gl/maps/Hdejr", "<MISSING>"
                        )
                    if "Bronx River Medical Associates" in full:
                        pass
                    else:
                        if full[-1] == "Find on Google Maps":
                            del full[-1]
                        if "Phone:" in full:
                            location_name = full[0]
                            street_address = full[1]
                            city = full[-3].split(",")[0]
                            state = " ".join(full[-3].split(",")[1].split()[0:2])
                            zipp = full[-3].split(",")[1].split()[-1]
                            phone = full[-1]
                        else:
                            location_name = " ".join(full[:-2])
                            street_address = full[-2]
                            city = full[-1].split(",")[0]
                            state = " ".join(full[-1].split(",")[-1].split()[:-1])
                            zipp = full[-1].split(",")[-1].split()[-1]
                            phone = "<MISSING>"

                if street_address == "Oncology/Hematology at Montefiore":
                    street_address = "60 East 208th Street"
                    city = "Bronx"
                    state = "NY"
                    zipp = "10467"

                if "1695 Eastchester Road, 2nd Floor" in str(full):
                    street_address = "1695 Eastchester Road, 2nd Floor"

                store = []
                store.append(base_url if base_url else "<MISSING>")
                store.append(location_name if location_name else "<MISSING>")
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state.replace("10504", "") if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append("US")
                store.append("<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append("<MISSING>")
                store.append("https://www.montefiore.org/cancer-contact")
                store = [str(x).strip() if x else "<MISSING>" for x in store]
                if (str(store[2])) in addresses:
                    continue
                addresses.append(str(store[2]))
                temp.append(store)

    # #################################################################################
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for link in soup.find("div", class_="sectionBox grey-box bg-dkblue").find_all("a"):
        if "www" in link["href"]:
            url = link["href"]

        elif "/" in link["href"]:
            url = "https://www.montefiore.org" + link["href"]

        else:
            url = "https://www.montefiore.org/" + link["href"]

        logger.info(url)
        try:
            r1 = session.get(url, headers=headers)
        except:
            continue
        soup1 = BeautifulSoup(r1.text, "lxml")
        try:
            table = soup1.find("div", class_="content").find("table")
            if table:

                for td in table.find_all("td"):
                    try:
                        latitude = td.find("a")["href"].split("sll=")[1].split(",")[0]
                        longitude = (
                            td.find("a")["href"]
                            .split("sll=")[1]
                            .split(",")[1]
                            .split("&")[0]
                        )
                    except:
                        pass

                    if len(list(td.stripped_strings)) > 1:
                        location_name = list(td.stripped_strings)[0]
                        street_address = list(td.stripped_strings)[1]
                        city = list(td.stripped_strings)[2].split(",")[0]
                        state = list(td.stripped_strings)[2].split(",")[-1].split()[0]
                        zipp = list(td.stripped_strings)[2].split(",")[-1].split()[-1]
                        if "Phone:" in " ".join(list(td.stripped_strings)):
                            phone = list(td.stripped_strings)[-1]
                        else:
                            phone = "<MISSING>"
                        location_type = "Moses Campus"
                        store_number = "<MISSING>"
                        hours_of_operation = "<MISSING>"
                        latitude = "37.0625"
                        longitude = "-95.677068"

                        if "3400 Bainbridge Ave" in street_address:
                            latitude = "40.880825"
                            longitude = "-73.879881"

                        page_url = url

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
                        if store[2] in addresses:
                            continue
                        addresses.append(store[2])
                        temp.append(store)

            else:
                try:
                    url1 = soup1.find("nav", class_="footer-links").find(
                        "a", text=re.compile("Locations")
                    )
                    r = session.get("https://www.cham.org" + url1["href"])
                    soup = BeautifulSoup(r.text, "lxml")
                    loc = list(
                        soup.find_all("div", class_="freeXML")[-1]
                        .find("p")
                        .stripped_strings
                    )
                    street_address = loc[0]
                    city = loc[1].split(",")[0]
                    state = loc[1].split(",")[1]
                    zipp = loc[1].split(",")[-1].split()[-1]
                    phone = loc[2]
                    location_name = city
                    location_type = "Main campus"
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                    store_number = "<MISSING>"
                    hours_of_operation = "<MISSING>"
                    page_url = "https://www.cham.org" + url1["href"]
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
                    temp.append(store)
                    for loc in soup.find("div", class_="freeTxt").find_all(
                        "div", class_="column xsm-24 sm-12"
                    ):
                        list_loc = list(loc.stripped_strings)
                        if "Phone" in list_loc[-2]:
                            del list_loc[-2]
                        location_name = list_loc[0]
                        phone = list_loc[-1]
                        if len(list_loc) > 4:
                            street_address = list_loc[-3]
                            city = list_loc[-2].split(",")[0]
                            state = " ".join(list_loc[-2].split(",")[1].split()[:-1])
                            zipp = list_loc[-2].split(",")[1].split()[-1]
                        elif len(list_loc) == 4 and "NICU" in list_loc[1]:
                            street_address = " ".join(list_loc[2].split(",")[:-2])
                            city = list_loc[2].split(",")[-2]
                            state = list_loc[2].split(",")[-1].split()[0]
                            zipp = list_loc[2].split(",")[-1].split()[-1]
                        else:
                            street_address = list_loc[1]
                            city = list_loc[-2].split(",")[0]
                            state = list_loc[-2].split(",")[1]
                            zipp = "<MISSING>"
                        location_type = "<MISSING>"
                        store_number = "<MISSING>"
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                        hours_of_operation = "<MISSING>"
                        page_url = "https://www.cham.org" + url1["href"]
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
                        store = [str(x).strip() if x else "<MISSING>" for x in store]
                        if store[2] in addresses:
                            continue
                        addresses.append(store[2])
                        temp.append(store)

                except:
                    if "einstein-campus" in url:
                        r = session.get(url)
                        soup = BeautifulSoup(r.text, "lxml")
                        for loc in soup.find("div", class_="content").find_all("p")[:2]:
                            list_loc = list(loc.stripped_strings)

                            if len(list_loc) == 2:
                                page_url = url
                                city = "<MISSING>"
                                state = "<MISSING>"
                                zipp = "<MISSING>"
                                latitude = "<MISSING>"
                                longitude = "<MISSING>"
                                store_number = "<MISSING>"
                                location_type = "Einstein Campus"
                                location_name = list_loc[0]
                                street_address = list_loc[1]
                                phone = "718-904-2800"
                                hours_of_operation = "24 hours"
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
                                    str(x).strip() if x else "<MISSING>" for x in store
                                ]
                                temp.append(store)
                            else:
                                for i in list_loc[1:]:
                                    page_url = url
                                    city = "<MISSING>"
                                    state = "<MISSING>"
                                    zipp = "<MISSING>"
                                    latitude = "<MISSING>"
                                    longitude = "<MISSING>"
                                    store_number = "<MISSING>"
                                    location_type = "Einstein Campus"
                                    location_name = list_loc[0]
                                    street_address = i
                                    phone = "<MISSING>"
                                    hours_of_operation = "Open Monday through Friday, 7:00 A.M. to 7:00 P.M."
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
                                        str(x).strip() if x else "<MISSING>"
                                        for x in store
                                    ]
                                    if store[2] in addresses:
                                        continue
                                    addresses.append(store[2])
                                    temp.append(store)
                    else:
                        try:
                            r = session.get(url)
                        except:
                            continue
                        soup = BeautifulSoup(r.text, "lxml")
                        loc = soup.find("div", {"id": "pagetitlecontainer"})
                        page_url = url
                        store_number = "<MISSING>"
                        if "Wakefield Campus" in loc.text:
                            add = list(
                                soup.find("div", class_="content")
                                .find_all("p")[2]
                                .stripped_strings
                            )
                            latitude = (
                                soup.find("div", class_="content")
                                .find_all("p")[3]
                                .a["href"]
                                .split("sll=")[1]
                                .split(",")[0]
                            )
                            longitude = (
                                soup.find("div", class_="content")
                                .find_all("p")[3]
                                .a["href"]
                                .split("sll=")[1]
                                .split(",")[1]
                                .split("&")[0]
                            )
                            location_name = add[0]
                            location_type = loc.text.strip()
                            street_address = add[1]
                            city = add[2].split(",")[0]
                            state = add[2].split(",")[1].split()[0]
                            zipp = add[2].split(",")[1].split()[-1]
                            phone = add[-1]
                            hours_of_operation = "24-hour"
                        elif "Westchester Square Campus" in loc.text:
                            add = list(
                                soup.find("div", class_="content")
                                .find_all("p")[1]
                                .stripped_strings
                            )
                            location_name = add[0]
                            location_type = loc.text.strip()
                            street_address = add[1]
                            city = add[2].split(",")[0]
                            state = add[2].split(",")[1].split()[0]
                            zipp = add[2].split(",")[1].split()[-1]
                            phone = add[-1]
                            hours_of_operation = "<MISSING>"
                            latitude = (
                                soup.find("div", class_="content")
                                .find_all("p")[2]
                                .a["href"]
                                .split("sll=")[1]
                                .split(",")[0]
                            )
                            longitude = (
                                soup.find("div", class_="content")
                                .find_all("p")[2]
                                .a["href"]
                                .split("sll=")[1]
                                .split(",")[1]
                                .split("&")[0]
                            )
                        else:
                            add = list(
                                soup.find("div", class_="content")
                                .find_all("p")[-2]
                                .stripped_strings
                            )
                            location_type = loc.text.strip()
                            location_name = add[0]
                            street_address = add[1]
                            city = add[2].split(",")[0]
                            state = add[2].split(",")[1].split()[0]
                            zipp = add[2].split(",")[1].split()[-1]
                            phone = "<MISSING>"
                            hours_of_operation = "<MISSING>"
                            latitude = (
                                soup.find("div", class_="content")
                                .find("iframe")["src"]
                                .split("!2d")[1]
                                .split("!2m")[0]
                                .split("!3d")[0]
                            )
                            longitude = (
                                soup.find("div", class_="content")
                                .find("iframe")["src"]
                                .split("!2d")[1]
                                .split("!2m")[0]
                                .split("!3d")[1]
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
                        store = [str(x).strip() if x else "<MISSING>" for x in store]
                        if store[2] in addresses:
                            continue
                        addresses.append(store[2])
                        temp.append(store)

        except:
            if "burke" in url:
                r = session.get(url + "outpatient/locations")
                soup = BeautifulSoup(r.text, "lxml")
                for ul in soup.find_all("ul", class_="locations-list"):
                    for loc in ul.find_all("li", class_="location-item"):
                        location_name = loc.find("h3").text.strip()
                        add = list(
                            loc.find("div", class_="address-proper").stripped_strings
                        )
                        street_address = " ".join(add[:-1])
                        city = add[-1].split(",")[0]
                        state = add[-1].split(",")[-1].split()[0]
                        zipp = add[-1].split(",")[-1].split()[-1]
                        phone = list(
                            loc.find("div", class_="numbers phone").stripped_strings
                        )[1].strip()
                        try:
                            location_type = (
                                loc.find("div", class_="services")
                                .text.split("Click")[0]
                                .strip()
                            )
                        except:
                            location_type = "<MISSING>"
                        page_url = "https://www.burke.org" + loc.a["href"]
                        r_loc = session.get(page_url)
                        soup_loc = BeautifulSoup(r_loc.text, "lxml")
                        try:
                            hours_of_operation = (
                                " ".join(
                                    list(
                                        soup_loc.find(
                                            "table", class_="location-hours"
                                        ).stripped_strings
                                    )
                                )
                                .replace("–", "-")
                                .strip()
                            )
                        except:
                            hours_of_operation = "<MISSING>"
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                        store_number = "<MISSING>"
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
                        store = [str(x).strip() if x else "<MISSING>" for x in store]
                        if store[2] in addresses:
                            continue
                        addresses.append(store[2])
                        temp.append(store)
            else:
                r = session.get(url)
                soup = BeautifulSoup(r.text, "lxml")
                try:
                    loc = soup.find("div", class_="footer-area-1").find(
                        "div", class_="locations"
                    )
                    for li in loc.find("ul").find_all("li"):
                        add = list(li.stripped_strings)
                        if "Directions" in add[-1]:
                            del add[-1]
                        location_name = " ".join(add[:-2])
                        street_address = add[-2]
                        city = add[-1].split(",")[0]
                        state = add[-1].split(",")[-1].split()[0]
                        zipp = add[-1].split(",")[-1].split()[-1]
                        phone = "<MISSING>"
                        hours_of_operation = "<MISSING>"
                        store_number = "<MISSING>"
                        location_type = "Montefiore health system"
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                        page_url = url
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
                        store = [str(x).strip() if x else "<MISSING>" for x in store]
                        if (str(store[2])) in addresses:
                            continue
                        addresses.append(str(store[2]))
                        temp.append(store)
                except:
                    if "montefioreslc" in url:
                        r = session.get(url)
                        soup = BeautifulSoup(r.text, "lxml")
                        loc = soup.find("div", class_="schema-info half")
                        location_name = loc.find("meta", {"itemprop": "name"})[
                            "content"
                        ]
                        for add in loc.find_all("div", class_="location-info"):
                            street_address = list(add.stripped_strings)[0]
                            city = list(add.stripped_strings)[1]
                            state = list(add.stripped_strings)[-4]
                            zipp = list(add.stripped_strings)[-3]
                            phone = list(add.stripped_strings)[-1]
                            latitude = "<MISSING>"
                            hours_of_operation = "<MISSING>"
                            store_number = "<MISSING>"
                            location_type = "<MISSING>"
                            latitude = "<MISSING>"
                            longitude = "<MISSING>"
                            page_url = url
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
                                str(x).strip() if x else "<MISSING>" for x in store
                            ]
                            if store[2] in addresses:
                                continue
                            addresses.append(store[2])
                            temp.append(store)
                    else:
                        pass

    #############################################################################################################################
    r = session.get("https://www.montefiore.org/mmg", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    nav = (
        soup.find("div", class_="leftnav")
        .find("ul", class_="parents")
        .find("li", class_="parent")
    )
    for li in nav.find("ul", class_="children").find_all("li", class_="child"):
        a = "https://www.montefiore.org/" + li.a["href"]
        logger.info(a)
        r1 = session.get(a, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        location_name = soup1.find("div", {"id": "pagetitlecontainer"}).text
        try:
            contact = soup1.find("div", class_="mmgcontact")
            address = list(contact.stripped_strings)
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"

            try:
                phone = re.findall(r"[(\d)]{3}-[\d]{3}-[\d]{4}", str(contact))[0]
            except:
                phone = "<MISSING>"

            for i, row in enumerate(address):
                if "special" in row.lower():
                    try:
                        location_type = row.split(":")[1].strip()
                    except:
                        location_type = address[i + 1].strip()

            page_url = a
            if "Hours of Operation" in str(" ".join(address)):
                hours = (
                    " ".join(address)
                    .split("Hours of Operation")[1]
                    .split("Specialties")[0]
                    .split("Specialty")[0]
                    .strip()
                    .split()
                )
                if ":" == hours[0].strip() or "-" == hours[0].strip():
                    del hours[0]
                hours_of_operation = " ".join(hours).replace("–", "-").strip()

            else:
                hours_of_operation = "<MISSING>"
            try:
                data = int(address[0].strip()[0])
                street_address = address[0]
                city = address[1].split(",")[0]
                state = address[1].split(",")[-1].split()[0]
                zipp = address[1].split(",")[-1].split()[1]
            except:
                try:
                    data = int(address[1].strip()[0])
                    street_address = address[1]
                    city = address[2].split(",")[0]
                    state = address[2].split(",")[-1].split()[0]
                    zipp = address[2].split(",")[-1].split()[1]
                except:
                    continue
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
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            temp.append(store)
        except:
            continue

    # --------------------------------  mmg locations --------------------------------

    url = "https://www.google.com/maps/d/embed?mid=1KdL2nJazZh47ZXogEriVKB3YLVk&msa=0&ll=40.860555025437755%2C-73.84279832234037&spn=0.005136%2C0.011362&iwloc=0004befb4696e25688410&output=embed&z=17"
    r = session.get(url)
    logger.info(url)
    soup = BeautifulSoup(r.text, "lxml")
    script = soup.script.contents[0].split("KIEABWLWCFIQ06A469A1")
    for i in script[26:51]:
        location_type = "Montefiore Medical Group"
        store_number = "<MISSING>"
        page_url = "https://www.montefiore.org/mmg-map"
        hours_of_operation = "<MISSING>"
        latitude = i.split("\\n]\\n]\\n,")[0].split("[[[")[1].split(",")[0]
        longitude = (
            i.split("\\n]\\n]\\n,")[0].split("[[[")[1].split(",")[1].split("]")[0]
        )
        location_name = (
            i.split('\\"name\\",')[1]
            .split("\\n,1]")[0]
            .replace('"', "")
            .replace("\\", "")
            .replace("[", "")
            .replace("]", "")
            .strip()
        )
        address = i.split('\\"description\\",')[1].split("\n,1]")[0].split("\\n")

        if len(address) == 7:
            street_address = address[0].split('[\\"')[1].split('\\"]')[0].split(",")[0]
            city = address[0].split('[\\"')[1].split('\\"]')[0].split(",")[1]
            state = (
                address[0].split('[\\"')[1].split('\\"]')[0].split(",")[-1].split()[0]
            )
            zipp = (
                address[0].split('[\\"')[1].split('\\"]')[0].split(",")[-1].split()[-1]
            )
            phone = "<MISSING>"
        elif len(address) == 13:
            street_address = (
                " ".join(address)
                .split("Address: ")[1]
                .split("\\")[0]
                .split(",")[0]
                .replace("Bronx", "")
                .strip()
            )
            city = "Bronx"
            state = (
                " ".join(address)
                .split("Address: ")[1]
                .split("\\")[0]
                .split(",")[1]
                .split()[0]
            )
            zipp = (
                " ".join(address)
                .split("Address: ")[1]
                .split("\\")[0]
                .split(",")[1]
                .split()[-1]
            )
            phone = (
                " ".join(address)
                .split("Phone:")[1]
                .split("\\")[0]
                .replace("CHAM", "")
                .strip()
            )
        else:
            try:
                data = int(address[1].strip()[0])
                street_address = address[1].replace("\\", "")
                city = address[2].split(",")[0]
                state = address[2].split(",")[-1].replace("\\", "").split()[0]
                zipp = address[2].split(",")[-1].replace("\\", "").split()[-1]
                phone = (
                    " ".join(address)
                    .split("Phone:")[1]
                    .split("\\")[0]
                    .replace(" (Adult Medicine) 718-920-5161 (Pediatrics)", "")
                )
            except:
                try:
                    data = int(address[2].strip()[0])
                    street_address = address[2].replace("\\", "")
                    city = address[3].split(",")[0]
                    state = address[3].split(",")[-1].replace("\\", "").split()[0]
                    zipp = address[3].split(",")[-1].replace("\\", "").split()[-1]
                    phone = (
                        " ".join(address)
                        .split("Phone:")[1]
                        .split("\\")[0]
                        .replace(" (Adult Medicine) 718-920-5161 (Pediatrics)", "")
                    )
                except:
                    try:
                        data = int(address[4].strip()[0])
                        street_address = address[4].replace("\\", "")
                        city = address[5].split(",")[0]
                        state = address[5].split(",")[-1].replace("\\", "").split()[0]
                        zipp = address[5].split(",")[-1].replace("\\", "").split()[-1]
                        phone = (
                            " ".join(address)
                            .split("Phone:")[1]
                            .split("\\")[0]
                            .replace(" (Adult Medicine) 718-920-5161 (Pediatrics)", "")
                        )
                    except:
                        phone = (
                            " ".join(address)
                            .split("Phone:")[1]
                            .split("\\")[0]
                            .replace(" (Adult Medicine) 718-920-5161 (Pediatrics)", "")
                        )
                        street_address = (
                            " ".join(address)
                            .split("Address: ")[1]
                            .split("\\")[0]
                            .split(",")[0]
                            .strip()
                        )
                        city = (
                            " ".join(address)
                            .split("Address: ")[1]
                            .split("\\")[0]
                            .split(",")[1]
                            .strip()
                        )
                        state = (
                            " ".join(address)
                            .split("Address: ")[1]
                            .split("\\")[0]
                            .split(",")[-1]
                            .split()[0]
                        )
                        zipp = (
                            " ".join(address)
                            .split("Address: ")[1]
                            .split("\\")[0]
                            .split(",")[-1]
                            .split()[-1]
                        )
        store = [
            locator_domain,
            location_name,
            street_address.replace("Rd.", "Road"),
            city,
            state.strip(),
            zipp.strip(),
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
            page_url,
        ]
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        temp.append(store)

    for i in range(len(temp)):
        if temp[i][1] + " " + temp[i][2] in addresses:
            continue
        addresses.append(temp[i][1] + " " + temp[i][2])
        yield temp[i]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
