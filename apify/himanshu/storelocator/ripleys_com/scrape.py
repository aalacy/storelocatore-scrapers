import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("ripleys_com")
session = SgRequests()


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }

    base_url = "https://www.ripleys.com"
    addresses = []

    r = session.get("https://www.ripleys.com/attractions/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    for location_img_tag in soup.find(id="tabpanel1").find_all("li"):

        location_tag = location_img_tag.find("a")
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
        page_url = (
            location_tag["href"]
            .replace(
                "https://marinersquare.com/",
                "https://www.ripleys.com/newport/information/",
            )
            .replace(
                "http://www.williamsburgripleys.com/",
                "https://www.ripleys.com/williamsburg/",
            )
        )
        logger.info(page_url)
        location_name = location_tag.text
        r_location = session.get(page_url, headers=headers)
        if r_location is None:
            continue
        soup_location = BeautifulSoup(r_location.text, "lxml")
        full_address_list = []
        hours_list = []
        if soup_location.find("div", {"class": "large-4 medium-4 small-12 columns"}):

            full_address_list = list(
                soup_location.find(
                    "div", {"class": "large-4 medium-4 small-12 columns"}
                ).stripped_strings
            )
            if soup_location.find(
                "div", {"class": "medium-6 columns hide-for-small-only"}
            ):
                hours_list = list(
                    soup_location.find(
                        "div", {"class": "medium-6 columns hide-for-small-only"}
                    ).stripped_strings
                )
                hours_index = [i for i, s in enumerate(hours_list) if "Hours" in s]
                hours_of_operation = " ".join(hours_list[hours_index[0] :])
        elif soup_location.find("div", {"class": "footerText"}):

            full_address_list = list(
                soup_location.find("div", {"class": "footerText"}).stripped_strings
            )
            hours_tag = soup_location.find(
                lambda tag: (tag.name == "h6")
                and "Hours of Operation" == tag.text.strip()
            )
            if hours_tag:
                hours_list = list(hours_tag.find_next_sibling("div").stripped_strings)
                hours_of_operation = " ".join(hours_list)

        elif soup_location.find("span", {"id": "contact"}):

            full_address_list = list(
                soup_location.find(
                    "span", {"id": "contact"}
                ).parent.parent.stripped_strings
            )[1:]
            hours_tag = soup_location.find(
                lambda tag: (tag.name == "span" or tag.name == "h3")
                and "HOURS" == tag.text.strip()
            )

            if hours_tag:
                if hours_tag.parent.find_next_sibling("p"):
                    hours_list = list(
                        hours_tag.parent.find_next_sibling("p").stripped_strings
                    )
                elif hours_tag.find_next_sibling("p"):
                    hours_list = list(hours_tag.find_next_sibling("p").stripped_strings)

                if "$" not in str(hours_list):
                    hours_of_operation = " ".join(hours_list)

        elif soup_location.find("div", {"class": "contact-info-container"}):

            full_address_list = list(
                soup_location.find(
                    "div", {"class": "contact-info-container"}
                ).stripped_strings
            )
            if soup_location.find("section", {"id": "text-4"}):
                hours_list = list(
                    soup_location.find("section", {"id": "text-4"}).stripped_strings
                )[:-1]
                hours_of_operation = " ".join(hours_list)
        elif soup_location.find("div", {"class": "hotel-contact"}):

            full_address_list = list(
                soup_location.find("div", {"class": "hotel-contact"}).stripped_strings
            )
        elif soup_location.find("div", {"class": "block contact-info-block"}):
            full_address_list = list(
                soup_location.find(
                    "div", {"class": "block contact-info-block"}
                ).stripped_strings
            )
            addr = full_address_list[-4].replace("\xa0", " ").split(",")
            if len(addr[0]) < 5:
                addr = (
                    soup_location.find(id="address-1")
                    .text.replace("Click here to view location", "")
                    .split(",")
                )
                map_str = soup_location.find(class_="contact-info-row address").a[
                    "href"
                ]
                geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", map_str)[
                    0
                ].split(",")
                latitude = geo[0]
                longitude = geo[1]

            street_address = addr[0].strip()
            city = addr[1].strip()
            state = addr[2].strip().split()[0]
            zipp = addr[2].strip().split()[1]

            hours_tag = soup_location.find(
                lambda tag: (tag.name == "strong")
                and "Current Hours:" == tag.text.strip()
            )
            try:
                hours_list = list(hours_tag.parent.parent.stripped_strings)
            except:
                hours_list = ""
            hours_of_operation = " ".join(hours_list)

            if not hours_of_operation:
                hours_of_operation = " ".join(
                    list(
                        soup_location.find(class_="hours-of-operation").stripped_strings
                    )
                )
        elif soup_location.find("div", {"id": "text-2"}):

            full_address_list = list(
                soup_location.find("div", {"id": "text-2"}).stripped_strings
            )[1:]
            if soup_location.find(
                "div",
                {"class": "mtphr-dnt-tick mtphr-dnt-default-tick mtphr-dnt-clearfix"},
            ):
                hours_list = list(
                    soup_location.find(
                        "div",
                        {
                            "class": "mtphr-dnt-tick mtphr-dnt-default-tick mtphr-dnt-clearfix"
                        },
                    ).stripped_strings
                )

                hours_of_operation = " ".join(hours_list)

            if "," in full_address_list[0]:
                street_address = full_address_list[0].split(",")[0]
                city = full_address_list[0].split(",")[1]
            else:
                street_address = full_address_list[0]
                city = full_address_list[1].split(",")[0]
        elif soup_location.find("div", {"class": "contact-infotxt"}):

            full_address_list = list(
                soup_location.find("div", {"class": "contact-infotxt"}).stripped_strings
            )[1:]
            hours_of_operation = list(
                soup_location.find("div", {"class": "contact-infotxt"}).stripped_strings
            )[0]

        elif soup_location.find("div", {"id": "text-5"}):

            full_address_list = list(
                soup_location.find("div", {"id": "text-5"}).stripped_strings
            )[1:]
            hours_tag = soup_location.find(
                lambda tag: (tag.name == "h4")
                and "WEEKLY OPERATING HOURS" == tag.text.strip()
            )
            hours_of_operation = hours_tag.find_next_sibling("h5").text

            if "," in full_address_list[0]:
                street_address = full_address_list[0].split(",")[0]
                city = full_address_list[0].split(",")[1]
            else:
                street_address = full_address_list[0]
                city = full_address_list[1].split(",")[0]

        elif soup_location.find("div", {"class": "contentParappa"}):
            street_address = list(
                soup_location.find("div", {"class": "contentParappa"})
                .find_all("div", {"class": "cell medium-4"})[-1]
                .find_all("p")[2]
                .stripped_strings
            )[0]
            addr = list(
                soup_location.find("div", {"class": "contentParappa"})
                .find_all("div", {"class": "cell medium-4"})[-1]
                .find_all("p")[3]
                .stripped_strings
            )[0]
            city = addr.split(",")[0]
            state = addr.split(",")[1].strip().split(" ")[0]
            zipp = addr.split(",")[1].strip().split(" ")[1]
            phone = list(
                soup_location.find("div", {"class": "contentParappa"})
                .find_all("div", {"class": "cell medium-4"})[-1]
                .find_all("p")[4]
                .stripped_strings
            )[0]

            hours_of_operation = list(
                soup_location.find("div", {"class": "contentParappa"})
                .find_all("div", {"class": "cell medium-4"})[-1]
                .find_all("p")[6]
                .stripped_strings
            )[0]
        elif len(soup_location.find_all(id="footer-address-first")) > 1:
            locs = soup_location.find_all(id="footer-address-first")
            for loc in locs:
                full_address_list = list(loc.stripped_strings)
                location_name = full_address_list[0]
                street_address = full_address_list[1].split(",")[0]
                city_line = full_address_list[2].split(",")
                city = city_line[0]
                state = city_line[1].split()[0]
                zipp = city_line[1].split()[1]
                phone = full_address_list[-1]

                sgw.write_row(
                    SgRecord(
                        locator_domain=locator_domain,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zipp,
                        country_code=country_code,
                        store_number=store_number,
                        phone=phone,
                        location_type=location_type,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation,
                    )
                )
            continue
        elif soup_location.find(id="custom_html-3"):
            full_address_list = list(
                soup_location.find(id="custom_html-3").stripped_strings
            )[1:]
            full_address_list[0] = full_address_list[0].replace(" Blvd.", " Blvd,")
            street_address = full_address_list[0].split(",")[0]
            if "," not in full_address_list[1]:
                city = full_address_list[0].split(",")[1].strip()
            else:
                city = full_address_list[1].split(",")[0].strip()
        else:
            continue

        phone_list = re.findall(
            re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),
            str(full_address_list)
            .replace("\xa0", " ")
            .replace("-FISH (3474)", "-3474"),
        )
        ca_zip_list = re.findall(
            r"[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}",
            str(full_address_list).replace("\xa0", " "),
        )
        us_zip_list = re.findall(
            re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"),
            str(full_address_list).replace("\xa0", " "),
        )

        state_list = re.findall(r"\b[A-Z]{2}\b", str(location_name))
        if not state_list:
            state_list = re.findall(r"\b[A-Z]{2}\b", str(full_address_list))

        if state_list:
            state = state_list[0]

        if phone_list:
            phone = phone_list[0]

        if ca_zip_list:
            zipp = ca_zip_list[-1]
            country_code = "CA"

        if us_zip_list:
            zipp = us_zip_list[-1]
            country_code = "US"

        if not city:
            city = location_name.split(",")[0]

        if not street_address:
            if zipp:
                zipp_index = [i for i, s in enumerate(full_address_list) if zipp in s]

                if city in full_address_list[zipp_index[0]]:
                    city_index = full_address_list[zipp_index[0]].rindex(city)

                    state_list = re.findall(r"\b[A-Z]{2}\b", str(location_name))
                    if not state_list:
                        state_list = re.findall(
                            r"\b[A-Z]{2}\b", str(full_address_list[: zipp_index[0] + 1])
                        )

                    if state_list:
                        state = state_list[0]

                    if city_index == 0:
                        street_address = (
                            full_address_list[: zipp_index[0] + 1][0]
                            .replace("\n", ",")
                            .replace("\r", "")
                        )
                    else:
                        street_address = (
                            "".join(full_address_list[: zipp_index[0] + 1])[:city_index]
                            .replace("\n", ",")
                            .replace("\r", "")
                        )
                else:
                    street_address = (
                        " ".join(full_address_list[: zipp_index[0]])
                        .replace("\n", ",")
                        .replace("\r", "")
                    )
                    street_address = street_address.split(",")[0]
            else:
                if city in full_address_list[0]:
                    city_index = full_address_list[0].rindex(city)
                    street_address = (
                        "".join(full_address_list[0])[:city_index]
                        .replace("\n", ",")
                        .replace("\r", "")
                    )
                else:
                    street_address = (
                        full_address_list[0].replace("\n", ",").replace("\r", "")
                    )
                    street_address = street_address.split(",")[0]

        if street_address.strip().isnumeric():
            street_address = street_address + " " + city
        if "329  Alamo Plaza" in street_address:
            city = "San Antonio"
            street_address = "329 Alamo Plaza"
        if "329 Alamo Plaza" in street_address:
            r5 = session.get("https://www.ripleys.com/phillips/", headers=headers)
            soup = BeautifulSoup(r5.text, "lxml")
            hours1 = " ".join(
                list(
                    soup.find_all(
                        "li", {"class": "g1-column g1-one-half g1-valign-top"}
                    )[-2]
                    .find_all("p")[2]
                    .stripped_strings
                )
            )
            hours2 = " ".join(
                list(
                    soup.find_all(
                        "li", {"class": "g1-column g1-one-half g1-valign-top"}
                    )[-2]
                    .find_all("p")[3]
                    .stripped_strings
                )
            )
            hours_of_operation = hours1 + ", " + hours2

        if "800 Parkway" in street_address:
            r6 = session.get("https://www.ripleys.com/gatlinburg/", headers=headers)
            soup6 = BeautifulSoup(r6.text, "lxml")
            hours_of_operation = (
                " ".join(
                    list(
                        soup6.find_all(
                            "li", {"class": "g1-column g1-one-half g1-valign-top"}
                        )[-2].stripped_strings
                    )
                )
                .split("*Weather")[0]
                .replace(
                    "** ALL ATTRACTIONS WILL BE CLOSING EARLY AT 4PM ON WEDNESDAY, DECEMBER 4, 2019 FOR A CHRISTMAS PARTY** Believe It or Not!",
                    "",
                )
            )
        if "Niagara Falls" in city:
            state = "ON"
        hours_of_operation = (
            hours_of_operation.replace(
                "CLOSED FOR THE SEASON We cannot wait to welcome you back next year!",
                "CLOSED FOR THE SEASON",
            )
            .replace("Hours Ripley’s Believe It or Not!", "")
            .replace(
                "Hours Nights of Lights Nightly from November 14th through January 31st. A timed reservation is required. Ripley's Believe It or Not!",
                "",
            )
            .split(" *Last ticket")[0]
            .strip()
        )
        hours_of_operation = hours_of_operation.replace(
            "HOURS NOW OPEN! *Hours are subject to change – Please call to verify hours before visiting: (865) 436-5096 Ripley’s Believe It or Not!",
            "",
        ).replace(
            "Weather Permitting PRICES Buy discounted and combo tickets online! TICKETS & PRICING GROUPS We offer special rates for groups of 10 or more. To get in touch directly, please call (888) 240-1358, ext. 2156 or email our Groups Department . MORE GROUP INFO",
            "",
        )

        street_address = (
            street_address.replace("•", "")
            .replace("Pier Building on the Boardwalk,", "")
            .strip()
        )

        if street_address[-1:] == ",":
            street_address = street_address[:-1]

        if street_address not in addresses and country_code:
            addresses.append(street_address)

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zipp,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
