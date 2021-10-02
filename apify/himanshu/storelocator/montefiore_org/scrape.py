import re
import usaddress
from bs4 import BeautifulSoup

from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("montefiore_org")


session = SgRequests()


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    country_code = "US"
    temp = []

    page_url = "https://www.montefiore.org/westchester-square-campus"
    r = session.get(page_url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
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

    row = SgRecord(
        locator_domain=locator_domain,
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zipp,
        country_code=country_code,
        store_number=SgRecord.MISSING,
        phone=phone,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=SgRecord.MISSING,
    )

    sgw.write_row(row)

    page_url = "https://www.montefiore.org/cancer-contact"
    base_url = "https://www.montefiore.org/"
    r = session.get(page_url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
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

                row = SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zipp,
                    country_code=country_code,
                    store_number=SgRecord.MISSING,
                    phone=phone,
                    location_type=SgRecord.MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=SgRecord.MISSING,
                )

                sgw.write_row(row)

    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
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
        soup1 = BeautifulSoup(r1.text, "html.parser")
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
                        latitude = "37.0625"
                        longitude = "-95.677068"

                        if "3400 Bainbridge Ave" in street_address:
                            latitude = "40.880825"
                            longitude = "-73.879881"

                        page_url = url

                        row = SgRecord(
                            locator_domain=locator_domain,
                            page_url=page_url,
                            location_name=location_name,
                            street_address=street_address,
                            city=city,
                            state=state,
                            zip_postal=zipp,
                            country_code=country_code,
                            store_number=SgRecord.MISSING,
                            phone=phone,
                            location_type=location_type,
                            latitude=latitude,
                            longitude=longitude,
                            hours_of_operation=SgRecord.MISSING,
                        )

                        sgw.write_row(row)

            else:
                try:
                    url1 = soup1.find("nav", class_="footer-links").find(
                        "a", text=re.compile("Locations")
                    )
                    r = session.get("https://www.cham.org" + url1["href"])
                    soup = BeautifulSoup(r.text, "html.parser")

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

                        list_loc = list(loc)

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
                        page_url = "https://www.cham.org" + url1["href"]

                        row = SgRecord(
                            locator_domain=locator_domain,
                            page_url=page_url,
                            location_name=location_name,
                            street_address=street_address,
                            city=city,
                            state=state,
                            zip_postal=zipp,
                            country_code=country_code,
                            store_number=SgRecord.MISSING,
                            phone=phone,
                            location_type=SgRecord.MISSING,
                            latitude=SgRecord.MISSING,
                            longitude=SgRecord.MISSING,
                            hours_of_operation=SgRecord.MISSING,
                        )

                        sgw.write_row(row)

                except:
                    if "einstein-campus" in url:
                        r = session.get(url)
                        soup = BeautifulSoup(r.text, "html.parser")
                        for loc in soup.find("div", class_="content").find_all("p")[:2]:
                            list_loc = list(loc.stripped_strings)  # type: ignore

                            if len(list_loc) == 2:
                                page_url = url
                                location_type = "Einstein Campus"
                                location_name = list_loc[0]
                                street_address = list_loc[1]
                                phone = "718-904-2800"
                                hours_of_operation = "24 hours"

                                row = SgRecord(
                                    locator_domain=locator_domain,
                                    page_url=page_url,
                                    location_name=location_name,
                                    street_address=street_address,
                                    city=SgRecord.MISSING,
                                    state=SgRecord.MISSING,
                                    zip_postal=SgRecord.MISSING,
                                    country_code=country_code,
                                    store_number=SgRecord.MISSING,
                                    phone=phone,
                                    location_type=location_type,
                                    latitude=SgRecord.MISSING,
                                    longitude=SgRecord.MISSING,
                                    hours_of_operation=hours_of_operation,
                                )

                                sgw.write_row(row)
                            else:
                                for i in list_loc[1:]:
                                    page_url = url
                                    location_type = "Einstein Campus"
                                    location_name = list_loc[0]
                                    street_address = i
                                    hours_of_operation = "Open Monday through Friday, 7:00 A.M. to 7:00 P.M."
                                    row = SgRecord(
                                        locator_domain=locator_domain,
                                        page_url=page_url,
                                        location_name=location_name,
                                        street_address=street_address,
                                        city=SgRecord.MISSING,
                                        state=SgRecord.MISSING,
                                        zip_postal=SgRecord.MISSING,
                                        country_code=country_code,
                                        store_number=SgRecord.MISSING,
                                        phone=SgRecord.MISSING,
                                        location_type=location_type,
                                        latitude=SgRecord.MISSING,
                                        longitude=SgRecord.MISSING,
                                        hours_of_operation=hours_of_operation,
                                    )

                                    sgw.write_row(row)
                    else:
                        try:
                            r = session.get(url)
                        except:
                            continue
                        soup = BeautifulSoup(r.text, "html.parser")
                        loc = soup.find("div", {"id": "pagetitlecontainer"})
                        page_url = url
                        store_number = "<MISSING>"
                        hours_of_operation = "<MISSING>"
                        if "Wakefield Campus" in loc.text:  # type: ignore
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
                            location_name = location_name.replace("\n", " ").strip()
                            location_type = loc.text.strip()  # type: ignore
                            street_address = add[1]
                            city = add[2].split(",")[0]
                            state = add[2].split(",")[1].split()[0]
                            zipp = add[2].split(",")[1].split()[-1]
                            phone = add[-1]
                            hours_of_operation = "24-hour"
                        elif "Westchester Square Campus" in loc.text:  # type: ignore
                            add = list(
                                soup.find("div", class_="content")
                                .find_all("p")[1]
                                .stripped_strings
                            )
                            location_name = add[0]
                            location_name = location_name.replace("\n", " ").strip()
                            location_type = loc.text.strip()  # type: ignore
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
                            location_type = loc.text.strip()  # type: ignore
                            location_name = add[0]
                            location_name = location_name.replace("\n", " ").strip()
                            street_address = add[1]
                            city = add[2].split(",")[0]
                            state = add[2].split(",")[1].split()[0]
                            zipp = add[2].split(",")[1].split()[-1]
                            phone = "<MISSING>"
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
                        row = SgRecord(
                            locator_domain=locator_domain,
                            page_url=page_url,
                            location_name=location_name,
                            street_address=street_address,
                            city=city,
                            state=state,
                            zip_postal=zipp,
                            country_code=country_code,
                            store_number=SgRecord.MISSING,
                            phone=phone,
                            location_type=location_type,
                            latitude=latitude,
                            longitude=longitude,
                            hours_of_operation=hours_of_operation,
                        )

                        sgw.write_row(row)

        except:
            if "burke" in url:
                r = session.get(url + "outpatient/locations")
                soup = BeautifulSoup(r.text, "html.parser")
                for ul in soup.find_all("ul", class_="locations-list"):
                    for loc in ul.find_all("li", class_="location-item"):
                        location_name = loc.find("h3").text.strip()  # type: ignore
                        location_name = location_name.replace("\n", " ").strip()
                        add = list(
                            loc.find("div", class_="address-proper").stripped_strings  # type: ignore
                        )
                        street_address = " ".join(add[:-1])
                        city = add[-1].split(",")[0]
                        state = add[-1].split(",")[-1].split()[0]
                        zipp = add[-1].split(",")[-1].split()[-1]
                        phone = list(
                            loc.find("div", class_="numbers phone").stripped_strings  # type: ignore
                        )[1].strip()
                        try:
                            location_type = (
                                loc.find("div", class_="services")  # type: ignore
                                .text.split("Click")[0]
                                .strip()
                            )
                        except:
                            location_type = "<MISSING>"
                        page_url = "https://www.burke.org" + loc.a["href"]  # type: ignore
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

                        row = SgRecord(
                            locator_domain=locator_domain,
                            page_url=page_url,
                            location_name=location_name,
                            street_address=street_address,
                            city=city,
                            state=state,
                            zip_postal=zipp,
                            country_code=country_code,
                            store_number=SgRecord.MISSING,
                            phone=phone,
                            location_type=location_type,
                            latitude=SgRecord.MISSING,
                            longitude=SgRecord.MISSING,
                            hours_of_operation=hours_of_operation,
                        )

                        sgw.write_row(row)
            else:
                r = session.get(url)
                soup = BeautifulSoup(r.text, "html.parser")
                try:
                    loc = soup.find("div", class_="footer-area-1").find(
                        "div", class_="locations"
                    )
                    for li in loc.find("ul").find_all("li"):  # type: ignore
                        add = list(li.stripped_strings)
                        if "Directions" in add[-1]:
                            del add[-1]
                        location_name = " ".join(add[:-2])
                        location_name = location_name.replace("\n", " ").strip()
                        street_address = add[-2]
                        city = add[-1].split(",")[0]
                        state = add[-1].split(",")[-1].split()[0]
                        zipp = add[-1].split(",")[-1].split()[-1]
                        phone = "<MISSING>"
                        hours_of_operation = "<MISSING>"
                        location_type = "Montefiore health system"
                        page_url = url
                        row = SgRecord(
                            locator_domain=locator_domain,
                            page_url=page_url,
                            location_name=location_name,
                            street_address=street_address,
                            city=city,
                            state=state,
                            zip_postal=zipp,
                            country_code=country_code,
                            store_number=SgRecord.MISSING,
                            phone=phone,
                            location_type=location_type,
                            latitude=SgRecord.MISSING,
                            longitude=SgRecord.MISSING,
                            hours_of_operation=hours_of_operation,
                        )

                        sgw.write_row(row)
                except:
                    if "montefioreslc" in url:
                        r = session.get(url)
                        soup = BeautifulSoup(r.text, "html.parser")
                        loc = soup.find("div", class_="schema-info half")
                        location_name = loc.find("meta", {"itemprop": "name"})["content"]  # type: ignore
                        location_name = location_name.replace("\n", " ").strip()
                        for add in loc.find_all("div", class_="location-info"):  # type: ignore
                            street_address = list(add.stripped_strings)[0]  # type: ignore
                            city = list(add.stripped_strings)[1]  # type: ignore
                            state = list(add.stripped_strings)[-4]  # type: ignore
                            zipp = list(add.stripped_strings)[-3]  # type: ignore
                            phone = list(add.stripped_strings)[-1]  # type: ignore
                            page_url = url
                            row = SgRecord(
                                locator_domain=locator_domain,
                                page_url=page_url,
                                location_name=location_name,
                                street_address=street_address,
                                city=city,
                                state=state,
                                zip_postal=zipp,
                                country_code=country_code,
                                store_number=SgRecord.MISSING,
                                phone=phone,
                                location_type=SgRecord.MISSING,
                                latitude=SgRecord.MISSING,
                                longitude=SgRecord.MISSING,
                                hours_of_operation=SgRecord.MISSING,
                            )

                            sgw.write_row(row)
                    else:
                        pass

    r = session.get("https://www.montefiore.org/mmg", headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    nav = (
        soup.find("div", class_="leftnav")
        .find("ul", class_="parents")
        .find("li", class_="parent")
    )
    for li in nav.find("ul", class_="children").find_all("li", class_="child"):
        a = "https://www.montefiore.org/" + li.a["href"]
        logger.info(a)
        r1 = session.get(a, headers=headers)
        soup1 = BeautifulSoup(r1.text, "html.parser")
        location_name = soup1.find("div", {"id": "pagetitlecontainer"}).text
        location_name = location_name.replace("\n", " ").strip()
        try:
            contact = soup1.find("div", class_="mmgcontact")
            address = list(contact.stripped_strings)
            location_type = "<MISSING>"

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
            if page_url == "https://www.montefiore.org/mmg-ffp":
                continue
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
                street_address = address[0]

                city = address[1].split(",")[0]
                state = address[1].split(",")[-1].split()[0]
                zipp = address[1].split(",")[-1].split()[1]
            except:
                try:
                    street_address = address[1]

                    city = address[2].split(",")[0]
                    state = address[2].split(",")[-1].split()[0]
                    zipp = address[2].split(",")[-1].split()[1]
                except:
                    continue
            if (
                "".join(address).find("2532 Grand Concourse") != -1
                or "".join(address).find("2100 Bartow Avenue") != -1
            ):
                street_address = address[1]
                city = address[2].split(",")[0]
                state = address[2].split(",")[-1].split()[0]
                zipp = address[2].split(",")[-1].split()[1]

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=location_type,
                latitude=SgRecord.MISSING,
                longitude=SgRecord.MISSING,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)
        except:
            continue

    url = "https://www.google.com/maps/d/embed?mid=1KdL2nJazZh47ZXogEriVKB3YLVk&msa=0&ll=40.860555025437755%2C-73.84279832234037&spn=0.005136%2C0.011362&iwloc=0004befb4696e25688410&output=embed&z=17"
    logger.info(url)
    r = session.get(url)
    tag = {
        "Recipient": "recipient",
        "AddressNumber": "address1",
        "AddressNumberPrefix": "address1",
        "AddressNumberSuffix": "address1",
        "StreetName": "address1",
        "StreetNamePreDirectional": "address1",
        "StreetNamePreModifier": "address1",
        "StreetNamePreType": "address1",
        "StreetNamePostDirectional": "address1",
        "StreetNamePostModifier": "address1",
        "StreetNamePostType": "address1",
        "CornerOf": "address1",
        "IntersectionSeparator": "address1",
        "LandmarkName": "address1",
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "BuildingName": "address2",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }
    cleaned = (
        r.text.replace("\\t", " ")
        .replace("\t", " ")
        .replace("\\n]", "]")
        .replace("\n]", "]")
        .replace("\\n,", ",")
        .replace("\\n", "#")
        .replace('\\"', '"')
        .replace("\\u003d", "=")
        .replace("\\u0026", "&")
        .replace("\\", "")
        .replace("\xa0", " ")
    )

    locations = (
        cleaned.split('var _pageData = "')[1]
        .split('";</script>')[0]
        .replace(
            '"Americau0027s Best Childrenu0027s Hospitals"',
            "Americau0027s Best Childrenu0027s Hospitals",
        )
        .replace("null", "None")
        .replace("false", "False")
        .replace("true", "True")
    )
    locations = eval(locations)[1][6][0][12][0][13][0]
    for l in locations:

        location_type = "Montefiore Medical Group"
        page_url = "https://www.montefiore.org/mmg-map"
        location_name = l[5][0][1][0]
        ad = " ".join(l[5][1][1]).strip()
        if ad.find("#Information") != -1:
            ad = ad.split("#Information")[0].strip()
        if ad.find("Information") != -1:
            ad = ad.split("Information")[0].strip()
        if ad.find("Address:") != -1:
            ad = ad.split("Address:")[1].strip()
        if ad.find("#Website:") != -1:
            ad = ad.split("#Website:")[0]
        ad = (
            ad.replace("##", " ")
            .replace("10467-2940#", "10467-2940")
            .replace("#Family Practice", "Family Practice")
            .replace("#(MHFP)", "(MHFP)")
            .replace("Ground Floor", "")
            .strip()
        )
        if ad.find("#") != -1:
            ad = " ".join(ad.split("#")[1:])
        if ad.find(")") != -1:
            ad = ad.split(")")[1].strip()
        ad = (
            ad.replace("Practice Center", "")
            .replace("AvenueBronx", "Avenue Bronx")
            .strip()
        )

        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()

        info = " ".join(l[5][1][1]).strip()
        state = a.get("state") or "<MISSING>"
        zipp = a.get("postal") or "<MISSING>"
        country_code = "USA"
        city = a.get("city") or "<MISSING>"
        if city.find("Concourse Bronx") != -1:
            street_address = street_address + " " + city.split()[0].strip()
            city = city.split()[1].strip()
        latitude = l[1][0][0][0]
        longitude = l[1][0][0][1]
        phone = "<MISSING>"
        if info.find("#Phone:") != -1:
            phone = info.split("#Phone:")[1].split("#")[0].strip()
        if phone.find("(Adult Medicine)") != -1:
            phone = phone.split("(Adult Medicine)")[0].strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zipp,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.montefiore.org/"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
