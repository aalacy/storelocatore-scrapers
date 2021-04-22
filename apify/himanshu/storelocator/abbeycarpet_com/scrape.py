import csv
import re

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
        location_url = (
            "https://www.abbeycarpet.com/StoreLocator.aspx?searchZipCode="
            + str(zip_code)
        )
        logger.info(location_url)
        try:
            r = session.get(location_url, headers=headers)
            soup = BeautifulSoup(r.text, "lxml")
        except:
            continue

        results = soup.find_all(class_="search-store__results-item")
        for result in results:
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
                logger.info(page_url)
            except:
                page_url = ""

            store_number = "<MISSING>"
            phone = "<MISSING>"
            hours_of_operation = "<MISSING>"
            location_type = "<MISSING>"

            got_page = False
            if page_url:
                home = session.get(page_url, headers=headers)
                if ".abbeycarpet.com" in home.url:
                    page_url = home.url
                    logger.info(page_url)
                    got_page = True

            # Get data from page_url
            if got_page:
                page_soup = BeautifulSoup(home.text, "lxml")

                if page_soup.find("a", {"class": "footer-address"}):
                    addresses = page_soup.find_all("a", {"class": "footer-address"})
                    phones = page_soup.find_all("a", {"class": "footer-phone"})
                    hours = page_soup.find_all("p", {"class": "hours"})

                    for i, address in enumerate(addresses):
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
                        hrs = hours[i].text.split("\n")
                        hours_of_operation = " ".join(hrs)
                        hours_of_operation = (
                            re.sub(" +", " ", hours_of_operation)
                        ).strip()

                        iframe = ""
                        src = None
                        if i == 0:
                            if (
                                page_soup.find("div", {"class": "mapWrapper"})
                                is not None
                            ):
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
                            elif len(addresses) == 3:
                                maps = page_soup.find_all(
                                    "div", {"class": "mapWrapper"}
                                )
                                if len(maps) == 3:
                                    iframe = maps[i].find("iframe")
                                elif (
                                    page_soup.find_all(
                                        "div",
                                        {
                                            "class": "col-xs-12 col-sm-12 col-md-4 col-lg-4"
                                        },
                                    )[i]
                                    is not None
                                ):
                                    iframe = page_soup.find_all(
                                        "div",
                                        {
                                            "class": "col-xs-12 col-sm-12 col-md-4 col-lg-4"
                                        },
                                    )[i].find("iframe")
                        try:
                            src = iframe["src"]
                        except:
                            src = None
                        if src is not None and src != []:
                            if "!3d" in src:
                                longitude = src.split("!2d")[1].split("!3d")[0]
                                latitude = (
                                    src.split("!2d")[1].split("!3d")[1].split("!")[0]
                                )
                            elif "place?zoom" in src:
                                latitude = src.split("=")[2].split(",")[0]
                                longitude = (
                                    src.split("=")[2].split(",")[1].split("&")[0]
                                )
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

                        if len(addresses) > 3:
                            latitude = "<INACCESSIBLE>"
                            longitude = "<INACCESSIBLE>"

                        if name == "font>":
                            name = "Southern Carpet & Interiors"

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
                        store.append(phone.split("&")[0].strip())
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
                    try:
                        divs = page_soup.find_all(
                            "div", {"class": "col-xs-12 col-sm-12 col-md-3 col-lg-3 "}
                        )
                        for div in divs:
                            lst = div.text.split("\n")
                            del lst[0]
                            del lst[-1]
                            if len(lst) > 4:
                                del lst[1]
                                name = lst[0]
                                street = lst[1]
                                city = lst[2].split(",")[0]
                                state = lst[2].split(",")[1].split()[0]
                                zip_code = lst[2].split(",")[1].split()[-1]
                                for i in lst:
                                    if "T:" in i:
                                        phone = i[3:]
                            else:
                                hours_of_operation = " ".join(lst[1:])
                    except:
                        got_page = False
                    hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()

                    if page_soup.find("div", {"class": "mapWrapper"}) is not None:
                        iframe = page_soup.find("div", {"class": "mapWrapper"}).find(
                            "iframe"
                        )
                        src = iframe["src"]
                        if src is not None and src != []:
                            if "!3d" in src:
                                longitude = src.split("!2d")[1].split("!3d")[0]
                                latitude = (
                                    src.split("!2d")[1].split("!3d")[1].split("!")[0]
                                )
                            elif "place?zoom" in src:
                                latitude = src.split("=")[2].split(",")[0]
                                longitude = (
                                    src.split("=")[2].split(",")[1].split("&")[0]
                                )
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
                    else:
                        try:
                            src = page_soup.find_all("iframe")[-1]
                            if "!3d" in src["src"]:
                                longitude = src["src"].split("!2d")[1].split("!3d")[0]
                                latitude = (
                                    src["src"]
                                    .split("!2d")[1]
                                    .split("!3d")[1]
                                    .split("!")[0]
                                )
                            elif "place?zoom" in src:
                                latitude = src["src"].split("=")[2].split(",")[0]
                                longitude = (
                                    src["src"].split("=")[2].split(",")[1].split("&")[0]
                                )
                            elif "!3f" in src["src"]:
                                longitude = src["src"].split("!2d")[1].split("!3f")[0]
                                latitude = (
                                    src["src"]
                                    .split("!2d")[1]
                                    .split("!3f")[1]
                                    .split("!4f")[0]
                                )
                            else:
                                latitude = ""
                                longitude = ""
                        except:
                            latitude = ""
                            longitude = ""

                    if not latitude:
                        try:
                            geo = re.findall(
                                r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", str(page_soup)
                            )[0].split(",")
                            latitude = geo[0]
                            longitude = geo[1]
                        except:
                            pass

                    if name == "font>":
                        name = "Southern Carpet & Interiors"

            # Get data from results list
            if not got_page:
                raw_address = list(
                    result.find(class_="search-store__results-address").stripped_strings
                )
                name = " ".join(raw_address[:-3])
                street = raw_address[-3]
                city_line = raw_address[-2].strip().split(",")
                city = city_line[0].strip()
                state = city_line[-1].strip().split()[0].strip()
                zip_code = city_line[-1].strip().split()[1].strip()
                phone = raw_address[-1]
                page_url = location_url
                latitude = ""
                longitude = ""

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
            store.append(phone.split("&")[0].strip())
            store.append(location_type)
            store.append(str(latitude) if latitude else "<MISSING>")
            store.append(str(longitude) if longitude else "<MISSING>")
            store.append(hours_of_operation)
            store.append(page_url)
            if street in adress2:
                continue
            adress2.append(street)

            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
