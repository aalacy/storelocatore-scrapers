import csv
import re
import time

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

logger = SgLogSetup().get_logger("abbeycarpet_com")
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

    adress = []
    adress2 = []
    all_links = []
    all_zips = []
    links_data = []

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
    }
    base_url = "https://www.abbeycarpet.com"
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_results=5,
        max_radius_miles=50,
    )
    logger.info("Running sgzips ..")

    for zip_code in search:
        if len(str(zip_code)) == 4:
            zip_code = "0" + str(zip_code)
        if len(str(zip_code)) == 3:
            zip_code = "00" + str(zip_code)
        location_url = (
            "https://www.abbeycarpet.com/StoreLocator.aspx?searchZipCode="
            + str(zip_code)
        )
        all_zips.append(location_url)

    extra_zips = [
        "11803",
        "11791",
        "11731",
        "11704",
        "11756",
        "10010",
        "90670",
        "92806",
        "94510",
        "94541",
        "94901",
        "59105",
        "10024",
        "45601",
        "20151",
        "95531",
        "95212",
        "85251",
        "27609",
        "56444",
        "84321",
        "22701",
        "22408",
        "30907",
        "98236",
        "71111",
        "79424",
        "79410",
        "98520",
        "76248",
        "22601",
    ]

    for _zip in extra_zips:
        all_zips.append(
            "https://www.abbeycarpet.com/StoreLocator.aspx?searchZipCode=" + _zip
        )

    for location_url in all_zips:
        try:
            r = session.get(location_url, headers=headers)
            soup = BeautifulSoup(r.text, "lxml")
        except:
            continue

        results = soup.find_all(class_="search-store__results-item")
        for result in results:

            # Skip if location already found
            st = list(
                result.find(class_="search-store__results-address").stripped_strings
            )[-3]
            if st in adress:
                continue
            adress.append(st)

            try:
                page_url = base_url + result.find(
                    class_="search-store__results-links-site"
                ).get("href")
            except:
                page_url = ""

            # Get data from results list
            raw_address = list(
                result.find(class_="search-store__results-address").stripped_strings
            )

            if page_url:
                if page_url not in all_links:
                    all_links.append(page_url)
                    links_data.append([page_url, raw_address])
            else:
                logger.info("---- Saving from result list ----")
                name = " ".join(raw_address[:-3])
                street = raw_address[-3]
                city_line = raw_address[-2].strip().split(",")
                city = city_line[0].strip()
                state = city_line[-1].strip().split()[0].strip()
                zip_code = city_line[-1].strip().split()[1].strip()
                phone = raw_address[-1]
                page_url = location_url
                store_number = "<MISSING>"
                hours_of_operation = "<MISSING>"
                location_type = "<MISSING>"

                store = []
                store.append(base_url)
                store.append(name)
                store.append(street.strip())
                store.append(city.strip())
                store.append(state.replace("N. Carolina", "NC").strip())
                store.append(zip_code)
                if zip_code.isdigit():
                    store.append("US")
                else:
                    store.append("CA")
                store.append(store_number)
                store.append(phone.split("&")[0].replace("T:", "").strip())
                store.append(location_type)
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append(hours_of_operation)
                store.append(page_url)
                yield store

    # Get data from page_url
    logger.info("Processing %s links.." % (len(all_links)))
    for page_url in all_links:
        got_page = False

        store_number = "<MISSING>"
        phone = "<MISSING>"
        hours_of_operation = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        try:
            home = session.get(page_url, headers=headers)
        except:
            try:
                time.sleep(10)
                home = session.get(page_url, headers=headers)
            except:
                logger.info("Error loading page %s..skipping" % (page_url))
                continue

        if ".abbeycarpet.com" in home.url:
            page_url = home.url
            got_page = True

        if not got_page:
            logger.info("---- Saving from result list ----")
            for row in links_data:
                if page_url == row[0]:
                    raw_address = row[1]
                    break
            name = " ".join(raw_address[:-3])
            street = raw_address[-3]
            city_line = raw_address[-2].strip().split(",")
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zip_code = city_line[-1].strip().split()[1].strip()
            phone = raw_address[-1]

            store = []
            store.append(base_url)
            store.append(name)
            store.append(street.strip())
            store.append(city.strip())
            store.append(state.replace("N. Carolina", "NC").strip())
            store.append(zip_code)
            if zip_code.isdigit():
                store.append("US")
            else:
                store.append("CA")
            store.append(store_number)
            store.append(phone.split("&")[0].replace("T:", "").strip())
            store.append(location_type)
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(hours_of_operation)
            store.append(page_url)
            if street in adress2:
                continue
            adress2.append(street)
            logger.info(street)
            yield store
        else:
            data_style = ""
            page_soup = BeautifulSoup(home.text, "lxml")
            if page_soup.find(class_="home__showroom-information"):
                data_style = "showroom"
                show_data = page_soup.find_all(class_="home__showroom-information")
                row_data = []
                for i, show in enumerate(show_data):
                    if i % 2 == 0:
                        try:
                            row_data.append([show, show_data[i + 1]])
                        except:
                            row_data.append([show, "<MISSING>"])

                addresses = []
                hours = []

                for row in row_data:
                    addresses.append(row[0])
                    hours.append(row[1])

            elif page_soup.find("a", {"class": "footer-address"}):
                data_style = "footer"
                addresses = page_soup.find_all("a", {"class": "footer-address"})
                phones = page_soup.find_all("a", {"class": "footer-phone"})
                hours = page_soup.find_all("p", {"class": "hours"})

            elif page_soup.find(class_="CustomBTN_White button3"):
                more_links = page_soup.find_all(class_="CustomBTN_White button3")
                for more_link in more_links:
                    link = (page_url + more_link["href"]).replace(".com//", ".com/")
                    all_links.append(link)
                    data_style = "move on"

            if data_style == "move on":
                continue

            if data_style:
                for i, address in enumerate(addresses):
                    store_number = "<MISSING>"
                    phone = "<MISSING>"
                    hours_of_operation = "<MISSING>"
                    location_type = "<MISSING>"
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                    if data_style == "footer":
                        address = address["href"].split("/")[-1]
                        if len(address.split(",")) == 4:
                            name = address.split(",")[0]
                            street = address.split(",")[1]
                        else:
                            name = address.split(",")[0]
                            street = "".join(address.split(",")[1:-2])
                        city = address.split(",")[-2]
                        state = address.split(",")[-1].split()[:-1]
                        if len(address.split(",")[-1].split()) > 2:
                            state = " ".join(state)
                        else:
                            state = address.split(",")[-1].split()[0]
                        zip_code = address.split(",")[-1].split()[-1]
                        phone = phones[i].text
                        location_type = "<MISSING>"
                        hrs = hours[i].text.split("  ")
                        try:
                            hours_of_operation = ""
                            for hr in hrs:
                                if (
                                    "mon" in hr.lower()
                                    or "am" in hr.lower()
                                    or "day" in hr.lower()
                                    or "pm" in hr.lower()
                                    or "appointment" in hr.lower()
                                    or "close" in hr.lower()
                                    or "by app" in hr.lower()
                                    or "m-" in hr.lower()
                                ):
                                    hours_of_operation = (
                                        hours_of_operation + " " + hr
                                    ).strip()
                            hours_of_operation = (
                                re.sub(" +", " ", hours_of_operation)
                            ).strip()
                        except:
                            hours_of_operation = "<MISSING>"
                        if not hours_of_operation:
                            hours_of_operation = "<MISSING>"
                    else:
                        try:
                            name = address.find(class_="home__showroom-title").text
                            street = address.find(
                                class_="home__showroom-address-line"
                            ).text
                        except:
                            name = address.strong.text.strip()
                            street = (
                                address.find(class_="home__showroom-address-line")
                                .text.split("\n\n")[1]
                                .strip()
                            )
                        city_line = address.find_all(
                            class_="home__showroom-address-line"
                        )[1].text
                        city = city_line.split(",")[0]
                        state = city_line.split(",")[-1].split()[0]
                        zip_code = city_line.split(",")[-1].split()[-1]
                        try:
                            phone = address.a.text
                        except:
                            phone = "<MISSING>"
                        location_type = "<MISSING>"

                        try:
                            hrs = (
                                hours[i]
                                .text.replace("Showroom", "")
                                .strip()
                                .split("\n")
                            )
                            hours_of_operation = " ".join(hrs)
                            hours_of_operation = (
                                re.sub(" +", " ", hours_of_operation)
                            ).strip()
                        except:
                            hours_of_operation = "<MISSING>"

                    iframe = ""
                    src = None
                    if i == 0:
                        if page_soup.find("div", {"class": "mapWrapper"}) is not None:
                            iframe = page_soup.find(
                                "div", {"class": "mapWrapper"}
                            ).find("iframe")
                        else:
                            maps = page_soup.find_all("iframe")
                            for mp in maps:
                                if "www.google.com/maps/" in str(mp):
                                    iframe = mp
                                    break
                    else:
                        maps = page_soup.find_all("div", {"class": "mapWrapper"})
                        if len(addresses) == 2:
                            if len(maps) == 2:
                                iframe = maps[i].find("iframe")
                            else:
                                maps = page_soup.find_all("iframe")
                                if len(maps) == 2:
                                    iframe = maps[i]
                                else:
                                    try:
                                        iframe = page_soup.find_all(
                                            "div", {"class": "col-xs-12 col-sm-8"}
                                        )[1:][i].find("iframe")
                                    except:
                                        iframe = page_soup.find_all(
                                            "div", {"class": "col-xs-12 col-sm-8"}
                                        )[i].find("iframe")
                        elif len(addresses) > 2:
                            maps = page_soup.find_all("div", {"class": "mapWrapper"})
                            if len(maps) > 2:
                                iframe = maps[i].find("iframe")
                            elif not maps:
                                try:
                                    maps = page_soup.find_all("iframe")
                                    if "www.google.com/maps/" not in str(maps[0]):
                                        maps.pop(0)
                                    if len(maps) == len(addresses):
                                        iframe = maps[i]
                                except:
                                    pass
                            elif (
                                page_soup.find_all(
                                    "div",
                                    {"class": "col-xs-12 col-sm-12 col-md-4 col-lg-4"},
                                )[i]
                                is not None
                            ):
                                iframe = page_soup.find_all(
                                    "div",
                                    {"class": "col-xs-12 col-sm-12 col-md-4 col-lg-4"},
                                )[i].find("iframe")
                    try:
                        src = iframe["src"]
                    except:
                        src = None
                    if src is not None and src != []:
                        if "!3d" in src:
                            longitude = src.split("!2d")[1].split("!3d")[0]
                            latitude = src.split("!2d")[1].split("!3d")[1].split("!")[0]
                        elif "place?zoom" in src:
                            latitude = src.split("=")[2].split(",")[0]
                            longitude = src.split("=")[2].split(",")[1].split("&")[0]
                        elif "!3f" in src:
                            longitude = src.split("!2d")[1].split("!3f")[0]
                            latitude = (
                                src.split("!2d")[1].split("!3f")[1].split("!4f")[0]
                            )
                        else:
                            latitude = ""
                            longitude = ""
                    else:
                        latitude = ""
                        longitude = ""

                    if not latitude:
                        try:
                            geo = re.findall(
                                r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+",
                                str(page_soup),
                            )[0].split(",")
                            latitude = geo[0]
                            longitude = geo[1]
                        except:
                            pass

                    if name == "font>":
                        name = "Southern Carpet & Interiors"

                    if "643 Danbury" in street:
                        zip_code = "06897"

                    store = []
                    store.append(base_url)
                    store.append(name)
                    store.append(street.strip())
                    store.append(city.strip())
                    store.append(state.replace("N. Carolina", "NC").strip())
                    store.append(zip_code)
                    if zip_code.isdigit():
                        store.append("US")
                    else:
                        store.append("CA")
                    store.append(store_number)
                    store.append(phone.split("&")[0].replace("T:", "").strip())
                    store.append(location_type)
                    store.append(str(latitude) if latitude else "<MISSING>")
                    store.append(str(longitude) if longitude else "<MISSING>")
                    store.append(hours_of_operation)
                    store.append(page_url)
                    if street in adress2:
                        continue
                    adress2.append(street)
                    yield store
            else:
                raise


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
