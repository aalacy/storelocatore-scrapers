import json
import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="swedish.org")

session = SgRequests()

user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
headers = {"User-Agent": user_agent}


def create_url(loctype):
    return {
        "loctype": loctype,
        "url": f"https://www.swedish.org/locations/list-view?loctype={loctype.replace(' ', '+')}&within=5000",
    }


def fetch_populated_location_map():
    locator_url = "https://www.swedish.org/locations/list-view"
    r = session.get(locator_url, headers=headers)
    groups = fetch_json_data(r.text)

    location_map = {}

    for group in groups:
        latitude = group.get("Latitude", "<MISSING>")
        longitude = group.get("Longitude", "<MISSING>")

        locations = group.get("Locations", [])

        for location in locations:
            location_name = location.get("Name").replace("–", "-").split("-")[0].strip()
            if "swedish" not in location_name.split()[0].lower():
                location_name = "Swedish " + location_name
            street_address, city, state, zipcode = parse_address(
                location.get("Address")
            )
            key = location.get("Maps")
            page_url = f"https://www.swedish.org{key}"

            location_map[location.get("Maps")] = {
                "locator_domain": "swedish.org",
                "page_url": page_url,
                "store_number": "<MISSING>",
                "location_name": location_name,
                "street_address": street_address,
                "city": city,
                "state": state,
                "zip": zipcode,
                "latitude": latitude,
                "longitude": longitude,
                "country_code": "US",
            }

    return location_map


def fetch_loctype_urls():
    locator_url = "https://www.swedish.org/locations"
    r = session.get(locator_url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    loctype_options = soup.select("#main_0_contentpanel_1_ddlLocationType option")
    loctypes = [option["value"] for option in loctype_options if option["value"]]

    urls = []
    for loctype in loctypes:
        urls.append(create_url(loctype))

    return urls


def fetch_json_data(content):
    match = re.search(r"locationsList\s*=\s*[\'|\"](.*?)[\'|\"];", content)
    data = json.loads(match.group(1))
    return data


def parse_address(address):
    if address == "":
        return ["<MISSING>", "<MISSING>", "<MISSING>", "<MISSING>"]

    parts = address.split("<br/>")
    city_state_zip = parts.pop(-1)
    city_state_zip_parts = city_state_zip.split(", ")

    if len(city_state_zip_parts) == 2:
        city, state_zip = city_state_zip_parts
        state, zipcode = state_zip.split(" ")
    else:
        state = "<MISSING>"
        city, zipcode = city_state_zip_parts[0].split(" ")

    street_address = " ".join(parts).strip()
    return [street_address, city, state, zipcode[0:5]]


def clean_phone(phone):
    if not phone or "-" not in phone.text:
        return None

    phoneNumber = phone.text.strip()
    if " (" in phoneNumber:
        phoneNumber = phoneNumber.split(" (")[1][:-1].strip()

    return phoneNumber


def fetch_data(sgw: SgWriter):

    location_map = fetch_populated_location_map()
    found = []

    for key in location_map:
        location = location_map[key]
        page_url = location.get("page_url")

        if ".providence.org" in page_url:
            page_url = page_url.replace("https://www.swedish.org", "")
        log.info("Pull content => " + page_url)
        r = session.get(page_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        if ".providence.org" in page_url:
            try:
                phone = soup.find(class_="loc-phone")
            except:
                phone = soup.find("a", {"href": re.compile(r"tel:.*")}).text.strip()
            try:
                hours_of_operation = " ".join(
                    list(soup.find(class_="clinic_hours").stripped_strings)
                )
            except:
                hours_of_operation = (
                    "Mon - Fri: 8 a.m. - 8 p.m.,Sat - Sun: 8 a.m. - 4 p.m."
                )
        else:
            phone = soup.find(class_="mobile-only-phone")
            phoneNumber = clean_phone(phone)
            if not phoneNumber:
                try:
                    phoneNumber = re.findall(
                        r"[\d]{3}-[\d]{3}-[\d]{4}",
                        str(soup.find(id="main-content").text),
                    )[0]
                except:
                    pass

            hours = soup.select_one(
                "#main_0_rightpanel_0_pnlOfficeHours .option-content"
            )
            if not hours:
                hours = soup.find(id="main_0_contentpanel_2_pnlOfficeHours")
            hours_of_operation = (
                hours.text.replace("\n", " ").strip()
                if hours and hours.text != ""
                else ""
            )
        hours_of_operation = (
            hours_of_operation.split("Schedule your")[0]
            .split("A pharmacist")[0]
            .split("; please call")[0]
            .split("Please contact")[0]
            .split("Printable")[0]
            .split("Call to")[0]
            .split("Patients and")[0]
            .split("Schedule a")[0]
            .split("Lab hours vary")[0]
        )

        if (
            "Each provider sets their hours" in hours_of_operation
            or "Hours may vary;" in hours_of_operation
        ):
            hours_of_operation = "<MISSING>"
        hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()

        location_map[key]["phone"] = phoneNumber or "<MISSING>"
        location_map[key]["hours_of_operation"] = hours_of_operation or "<MISSING>"

        if location.get("location_name") + location.get("street_address") in found:
            continue
        found.append(location.get("location_name") + location.get("street_address"))

        sgw.write_row(
            SgRecord(
                locator_domain=location.get("locator_domain"),
                page_url=page_url,
                location_name=location.get("location_name"),
                street_address=location.get("street_address"),
                city=location.get("city"),
                state=location.get("state"),
                zip_postal=location.get("zip").replace("98209", "98029"),
                country_code=location.get("country_code"),
                store_number=location.get("store_number"),
                phone=location.get("phone"),
                location_type="<MISSING>",
                latitude=location.get("latitude"),
                longitude=location.get("longitude"),
                hours_of_operation=location.get("hours_of_operation"),
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
