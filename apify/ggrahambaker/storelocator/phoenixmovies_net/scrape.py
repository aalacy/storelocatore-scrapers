from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

import usaddress


def parse_address(addy_string):
    parsed_add = usaddress.tag(addy_string)[0]

    street_address = ""

    if "AddressNumber" in parsed_add:
        street_address += parsed_add["AddressNumber"] + " "
    if "StreetNamePreDirectional" in parsed_add:
        street_address += parsed_add["StreetNamePreDirectional"] + " "
    if "StreetName" in parsed_add:
        street_address += parsed_add["StreetName"] + " "
    if "StreetNamePostType" in parsed_add:
        street_address += parsed_add["StreetNamePostType"] + " "
    if "OccupancyType" in parsed_add:
        street_address += parsed_add["OccupancyType"] + " "
    if "OccupancyIdentifier" in parsed_add:
        street_address += parsed_add["OccupancyIdentifier"] + " "

    if "PlaceName" not in parsed_add:
        city = "<MISSING>"
    else:
        city = parsed_add["PlaceName"]

    if "StateName" not in parsed_add:
        state = "<MISSING>"
    else:
        state = parsed_add["StateName"]

    if "ZipCode" not in parsed_add:
        zip_code = "<MISSING>"
    else:
        zip_code = parsed_add["ZipCode"]

    return street_address.strip(), city.strip(), state.strip(), zip_code.strip()


def fetch_data(sgw: SgWriter):
    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }

    locator_domain = "https://phoenixmovies.net/"

    r = session.get(locator_domain, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")

    locs = soup.find("div", {"class": "theatre-set"}).find_all("a")

    for loc in locs:
        link = locator_domain[:-1] + loc["href"]
        if "theatre" not in link:
            continue
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")

        main = soup.find("div", {"id": "theatre-information"})
        location_name = main.find("h1").text

        a_tag = loc.find(class_="address")
        street_address, city, state, zip_code = parse_address(
            a_tag.get_text(" ").strip()
        )
        if street_address == "17310 Laurel Park Drive":
            street_address = "17310 Laurel Park Drive North"
        phone_number = (
            soup.find("p", {"class": "phone"})
            .text.replace("Virtual Spin Tour", "")
            .strip()
        )
        if not phone_number:
            phone_number = "<MISSING>"
        country_code = "US"
        store_number = link.split("/")[-1]
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=link,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone_number,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
