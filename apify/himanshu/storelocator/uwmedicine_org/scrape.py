import json
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("uwmedicine_org")

session = SgRequests()


def fetch_data(sgw: SgWriter):
    addresses = []
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }
    base_url = "https://www.uwmedicine.org"
    links = []
    search_terms = ["s=medicine", "s=liver", "l=98104"]

    for search_term in search_terms:
        base_link = (
            "https://www.uwmedicine.org/search/locations?" + search_term + "&page=0"
        )
        r = session.get(base_link, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        last_page = int(
            (
                soup.find(class_="pager__item pager__item--last")
                .text.strip()
                .split("\n")[1]
            )
        )

        for page in range(0, last_page):
            search_link = (
                "https://www.uwmedicine.org/search/locations?"
                + search_term
                + "&page="
                + str(page)
            )
            logger.info(search_link)
            r = session.get(search_link, headers=headers)
            if r.status_code == 503:
                continue

            soup = BeautifulSoup(r.text, "lxml")
            if soup.find("div", {"class": "clinic-card__street-address"}):
                for link in soup.find_all(
                    "div", {"class": "clinic-card__cta uwm-accent-color__purple"}
                ):
                    if "uwmedicine.org/locations" not in link.find("a")["href"]:
                        continue
                    page_url = link.find("a")["href"]
                    if page_url in links:
                        continue
                    links.append(page_url)
                    r1 = session.get(page_url)
                    soup1 = BeautifulSoup(r1.text, "lxml")

                    try:
                        if (
                            "permanently closed"
                            in soup1.find(class_="clinic-page__hours").text.lower()
                        ):
                            continue
                    except:
                        pass

                    data = json.loads(
                        soup1.find(
                            lambda tag: (tag.name == "script")
                            and '"address"' in str(tag)
                        ).contents[0]
                    )["@graph"][0]
                    location_name = data["name"].replace("&#039;", "'")
                    street_address = data["address"]["streetAddress"]

                    if re.search(r"\d", street_address):
                        digit = str(re.search(r"\d", street_address))
                        start = int(digit.split("(")[1].split(",")[0])
                        street_address = street_address[start:]

                    city = data["address"]["addressLocality"]
                    state = data["address"]["addressRegion"]
                    zipp = data["address"]["postalCode"]
                    try:
                        phone = data["telephone"]
                    except:
                        phone = "<MISSING>"
                    location_type = "<MISSING>"
                    try:
                        hours = " ".join(
                            list(
                                soup1.find(
                                    "table", {"class": "clinic-page__hours-table"}
                                )
                                .find("tbody")
                                .stripped_strings
                            )
                        )
                    except:
                        if soup1.find("div", {"class": "clinic-page__open-current"}):
                            hours = (
                                soup1.find(
                                    "div", {"class": "clinic-page__open-current"}
                                )
                                .find("span")
                                .text
                            )
                        else:
                            hours = "<MISSING>"

                    street_address = (
                        street_address.replace("Main Hospital,", "")
                        .replace("West Clinic", "")
                        .replace("East Clinic,", "")
                        .replace("Emergency Department", "")
                        .replace("McMurray Medical Building,", "")
                        .replace(
                            "Center on Human Development and Disability Center,", ""
                        )
                        .strip()
                    )

                    if street_address + location_name in addresses:
                        continue
                    addresses.append(street_address + location_name)

                    sgw.write_row(
                        SgRecord(
                            locator_domain=base_url,
                            page_url=page_url,
                            location_name=location_name,
                            street_address=street_address,
                            city=city,
                            state=state,
                            zip_postal=zipp,
                            country_code="US",
                            store_number="",
                            phone=phone,
                            location_type=location_type,
                            latitude="",
                            longitude="",
                            hours_of_operation=hours,
                        )
                    )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
