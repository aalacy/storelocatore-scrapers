from lxml import etree
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
import re
from itertools import groupby
import json

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


DOMAIN = "wregional.com"
BASE_URL = "https://www.wregional.com"
LOCATION_URL = [
    "https://www.wregional.com/main/find-a-facility-or-clinic",
    "https://www.wregional.com/main/medical-services--programs",
]
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def parse_json(soup):
    info = soup.find("script", type="application/ld+json").string
    data = json.loads(info)
    return data


def is_multiple(street_address, location_name, locations):
    for row in locations:
        if street_address in row and location_name in row:
            log.info("Found multiple address => " + street_address)
            return True
    return False


def fetch_store_urls():
    log.info("Fetching store URL")
    store_urls = [
        {
            "url": "https://www.wregional.com/main/dialysis-centers-locations",
            "type": "",
            "name": "",
        }
    ]
    for home_url in LOCATION_URL:
        soup = pull_content(home_url)
        uls = soup.find_all("ul", {"class": "clinics"})
        for ul in uls:
            href = ul.find_all("a")
            for row in href:
                url = (
                    BASE_URL + row["href"]
                    if "urgentteam.com" not in row["href"]
                    and "wregional.com" not in row["href"]
                    else row["href"]
                )
                if "find-a-facility-or-clinic" in home_url:
                    type = row.find_parent("div").parent.find("h3").text
                    info = {
                        "url": url,
                        "type": type,
                        "name": row.parent.text,
                    }
                else:
                    type = row.parent.text
                    info = {
                        "url": url,
                        "type": type,
                        "name": type,
                    }
                store_urls.append(info)
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def get_hoo(link):
    soup = pull_content(link)
    hoo = soup.find("div", {"class": "branch-hours"}).find_all("p")
    hoo = hoo[1].find("span")
    hours_of_operations = "{}: {}".format(hoo.text, hoo.next_sibling.strip())
    return hours_of_operations


def fetch_data():
    except_link = ["https://www.wregional.com/hospice/willard-walker-hospice-home.aspx"]
    log.info("Fetching store_locator data")
    store_urls = fetch_store_urls()
    locations = []
    for row in store_urls:
        page_url = row["url"]
        if page_url in except_link:
            continue
        soup = pull_content(page_url)
        if "dialysis-centers-locations" in page_url:
            contents = soup.find("div", {"class": "page-content"}).find_all("strong")
            for content in contents:
                location_name = content.text
                street_address = content.next_sibling.next_sibling.strip()
                info = content.next_sibling.next_sibling.next_sibling.next_sibling.strip().split(
                    ","
                )
                city = info[0]
                state = info[1].split(" ")[1]
                zip_code = info[1].split(" ")[2]
                country_code = "US"
                store_number = "<MISSING>"
                phone = content.find_next("a").text
                hours_of_operation = (
                    content.find_next("a")
                    .next_sibling.find_next(text=True)
                    .find_next(text=True)
                    .strip()
                    .replace(" or later as needed for patient care", "")
                    .replace("–", "-")
                )
                if "Dialysis Center" in location_name:
                    location_type = "DIALYSIS_CENTER"
                elif "Home Dialysis" in location_name:
                    location_type = "HOME_DIALYSIS"
                else:
                    location_type = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                if not is_multiple(street_address, location_name, locations):
                    locations.append(
                        [
                            DOMAIN,
                            "https://www.wregional.com/main/dialysis-centers-locations",
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
        elif "springdale-center-for-health" in page_url or "medical-plaza" in page_url:
            content = soup.find("div", {"class": "page-content"})
            location = fetch_type_b(content, page_url, row["type"], row["name"])
            if not is_multiple(location[3], location[2], locations):
                locations.append(location)
        elif "urgentteam.com" in page_url:
            location = fetch_type_urgent(soup, page_url)
            if not is_multiple(location[3], location[2], locations):
                locations.append(location)
        elif soup.find("div", {"class": "clinics"}) and soup.find(
            "div", {"class": "clinics"}
        ).find("a", text=re.compile(r"Map and Directions|Map and Driving Directions")):
            content = soup.find("div", {"class": "page-content"})
            location = fetch_type_a(content, page_url, row["type"], row["name"])
            for val in location:
                if isinstance(val, list):
                    if not is_multiple(val[3], val[2], locations):
                        locations.append(val)
                else:
                    if not is_multiple(location[3], location[2], locations):
                        locations.append(location)
                    break
    return locations


def fetch_type_a(content, page_url, location_type, location_name):
    full_address = (
        content.find("div", class_="clinics")
        .find("p")
        .get_text(strip=True, separator="|")
    )
    if len(full_address) <= 1:
        full_address = content.find("div", class_="col-2").get_text(
            strip=True, separator="|"
        )
    full_address = full_address.replace("Telephone (Washington County):", "Telephone:")
    full_address = full_address.replace("Telephone: ", "Telephone:|")
    full_address = full_address.replace("Phone:", "Telephone:").split("|")
    if len(full_address) <= 1:
        return fetch_type_a2(content, page_url, location_type, location_name)
    location = fetch_type_a_proccess(
        page_url, content, full_address, location_name, location_type
    )
    return location


def fetch_type_a2(content, page_url, location_type, location_name):
    locations = []
    main = content.find("div", {"class": "clinics"}).find("div", {"class": "col-1"})
    if not main:
        return fetch_type_a3(content, page_url, location_type, location_name)
    else:
        main = main.find_all("h2")
    for row in main:
        url = row.find("a")
        page_url = (
            BASE_URL + url["href"]
            if "urgentteam.com" not in url["href"]
            and "wregional.com" not in url["href"]
            else url["href"]
        )
        soup = pull_content(page_url)
        if not soup.find("div", class_="clinics"):
            continue
        full_address = (
            soup.find("div", class_="clinics")
            .find("p")
            .get_text(strip=True, separator="|")
        )
        if len(full_address) <= 1:
            el = soup.find("div", class_="col-2")
            full_address = el.get_text(strip=True, separator="|")
            if len(el.find_all("h2")) > 1:
                full_address1 = full_address.replace(
                    "Telephone (Washington County):", "Telephone:"
                )
                full_address1 = full_address1.replace("Telephone: ", "Telephone:|")
                full_address1 = full_address1.replace("Phone:", "Telephone:").split("|")
                i = (
                    list(g)
                    for _, g in groupby(full_address1, key="Map and Directions".__ne__)
                )
                full_address_list = [a + b for a, b in zip(i, i)]
                for row_full_address in full_address_list:
                    row_full_address = "|".join(row_full_address)
                    row_full_address = row_full_address.replace(
                        "Telephone (Washington County):", "Telephone:"
                    )
                    row_full_address = row_full_address.replace(
                        "Telephone: ", "Telephone:|"
                    )
                    row_full_address = row_full_address.replace(
                        "Phone:", "Telephone:"
                    ).split("|")
                    location = fetch_type_a_proccess(
                        page_url,
                        soup,
                        row_full_address,
                        location_name,
                        location_type,
                    )
                    locations.append(location)
            else:
                full_address = full_address.replace(
                    "Telephone (Washington County):", "Telephone:"
                )
                full_address = full_address.replace("Telephone: ", "Telephone:|")
                full_address = full_address.replace("Phone:", "Telephone:").split("|")
                location = fetch_type_a_proccess(
                    page_url,
                    soup,
                    full_address,
                    location_name,
                    location_type,
                )
                locations.append(location)
    return locations


def fetch_type_a3(content, page_url, location_type, location_name):
    dom = etree.HTML(content.text)
    location_name = dom.xpath('//div[@class="page-title"]/h1/text()')
    if location_name:
        location_name = location_name[0]
        raw_adr = dom.xpath(
            '//strong[contains(text(), "{}")]/following::text()'.format(location_name)
        )[:2]
        full_address = [e.strip() for e in raw_adr]

    else:
        main = content.find("div", {"class": "clinics"}).find(
            "ul", {"class": "providers flex"}
        )
        if not main:
            info_addr = (
                content.find("div", {"class": "clinics"})
                .get_text(strip=True, separator="|")
                .split("|")
            )
            if len(info_addr) <= 17:
                del info_addr[:10]
            else:
                del info_addr[:17]
            info_addr = "|".join(info_addr)
            info_addr = info_addr.encode("ascii", "ignore").decode()
        else:
            info_addr = main.find_next("div", {"class": "grey-line"}).find_next("p")
            if not info_addr:
                info_addr = (
                    content.find("div", {"class": "clinics"})
                    .get_text(strip=True, separator="|")
                    .split("|")
                )
                del info_addr[:86]
                info_addr = "|".join(info_addr)
            else:
                info_addr = info_addr.get_text(strip=True, separator="|")
        full_address = info_addr.replace("Telephone (Washington County):", "Telephone:")
        full_address = full_address.replace("Telephone: ", "Telephone:|")
        full_address = full_address.replace("Phone:", "Telephone:").split("|")

    location = fetch_type_a_proccess(
        page_url,
        content,
        full_address,
        location_name,
        location_type,
    )
    return location


def fetch_type_a_proccess(
    page_url, content, full_address, location_name, location_type
):
    formated_address = full_address[: full_address.index("Telephone:") + 2]
    if (
        "(" in formated_address[1]
        and "3 E. Appleby Road" not in formated_address[1]
        or "Springdale Center for Health" in formated_address[1]
        or "Located in the William L. Bradley Medical Plaza" in formated_address[1]
        or "Urgent Care Clinic" in formated_address[0]
    ):
        del formated_address[1]
    if len(formated_address) >= 5:
        location_name = formated_address[0]
        street_address = formated_address[1]
        city = formated_address[2].split(",")[0]
        state = formated_address[2].split(",")[1].strip().split()[0]
        zip_code = formated_address[2].split(",")[1].strip().split()[1]
        phone_tag = formated_address[4].replace("Telephone:", "")
    else:
        street_address = formated_address[0]
        city = formated_address[1].split(",")[0]
        state = formated_address[1].split(",")[1].strip().split()[0]
        zip_code = formated_address[1].split(",")[1].strip().split()[1]
        phone_tag = formated_address[3].replace("Telephone:", "")
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
    regex = re.compile(r"Monday.*|Thursday.*")
    find_hoo = list(filter(regex.match, full_address))
    if find_hoo:
        hours_of_operation = " - ".join(find_hoo) if len(find_hoo) > 1 else find_hoo[0]
    elif content.find(
        lambda tag: (tag.name == "h3" or tag.name == "h2")
        and "Hours" == tag.text.strip()
    ):
        hours_of_operation = (
            " ".join(
                list(
                    content.find(
                        lambda tag: (tag.name == "h3" or tag.name == "h2")
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
    else:
        hours_of_operation = "<MISSING>"
    hours_of_operation = (
        hours_of_operation.replace(
            "  other clinic locations vary. For more information, please call 479-463-8740 .",
            "",
        )
        .replace(" Sick call is available", ",")
        .replace(" (or until full).", "")
        .replace("The Home is", "")
        .replace(", or by appointment", "")
    )
    store = [
        DOMAIN,
        page_url,
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
    return store


def fetch_type_b(content, page_url, location_type, location_name):
    location_name = " ".join([e.strip() for e in location_name.split() if e.strip()])
    dom = etree.HTML(content.text)
    location_name = dom.xpath('//div[@class="page-title"]/h1/text()')
    if location_name:
        raw_adr = dom.xpath(
            '//strong[contains(text(), "{}")]/following::text()'.format(
                location_name[0]
            )
        )[:2]
        full_address = [e.strip() for e in raw_adr]
    else:
        main = content.find("ul").find_next("p")
        if not main:
            info_addr = content.get_text(strip=True, separator="|").split("|")
            if len(info_addr) >= 19:
                del info_addr[:15]
            info_addr = "|".join(info_addr)
            info_addr = info_addr.replace("Map and Directions", "Telephone:|<MISSING>")
        else:
            addr = main.find_next("p").get_text(strip=True, separator="|").split("|")
            info_addr_list = []
            for row in addr:
                if "72762" in row:
                    info_addr_list.append(row)
                    info_addr_list.append("Telephone:|479.463.2333")
                else:
                    info_addr_list.append(row)
            info_addr = "|".join(info_addr_list)
        info_addr = info_addr.encode("ascii", "ignore").decode()
        full_address = info_addr.replace("Telephone (Washington County):", "Telephone:")
        full_address = full_address.replace("Telephone: ", "Telephone:|")
        full_address = full_address.replace("Phone:", "Telephone:").split("|")
    location = fetch_type_a_proccess(
        page_url,
        content,
        full_address,
        location_name,
        location_type,
    )
    return location


def fetch_type_urgent(soup, page_url):
    main = soup.find_all("script", {"type": "application/ld+json"})[1].string
    data = json.loads(main)
    addr = data["address"]
    location_name = data["name"]
    street_address = addr["streetAddress"].rstrip(", ")
    city = addr["addressLocality"]
    state = addr["addressRegion"]
    zip_code = addr["postalCode"]
    phone = data["telephone"]
    hours_of_operation = " ".join(
        list(soup.find("ul", {"class": "m-location-hours__list"}).stripped_strings)
    )
    location_type = "Urgent Care"
    store_number = "<MISSING>"
    latitude = data["geo"]["latitude"]
    longitude = data["geo"]["longitude"]
    store = [
        DOMAIN,
        page_url,
        location_name,
        street_address,
        city,
        state,
        zip_code,
        "US",
        store_number,
        phone,
        location_type,
        latitude,
        longitude,
        hours_of_operation,
    ]
    return store


def scrape():
    log.info("Start {} Scraper".format(DOMAIN))
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for elem in fetch_data():
            item = SgRecord(
                locator_domain=elem[0],
                page_url=elem[1],
                location_name=elem[2],
                street_address=elem[3],
                city=elem[4],
                state=elem[5],
                zip_postal=elem[6],
                country_code=elem[7],
                store_number=elem[8],
                phone=elem[9],
                location_type=elem[10],
                latitude=elem[11],
                longitude=elem[12],
                hours_of_operation=elem[13],
            )
            writer.write_row(item)


scrape()
