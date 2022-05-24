import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgpostal.sgpostal import parse_address_intl


def fetch_data(sgw: SgWriter):

    base_link = "https://www.shakeshack.co.uk/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="u-c-green u-ta-center")
    locator_domain = "shakeshack.co.uk"

    for i in items:
        item = i.find_previous("div")
        location_name = item.a.text.strip().title()
        link = item.a["href"]

        raw_address = item.p.text.replace("\r\n", " ").replace("\n", " ")
        addr = parse_address_intl(raw_address)
        try:
            street_address = addr.street_address_1 + " " + addr.street_address_2
        except:
            street_address = addr.street_address_1

        city = addr.city
        state = addr.state
        zip_code = addr.postcode

        if "London" in raw_address:
            city = "London"

        if len(street_address) < 15:
            if city:
                street_address = raw_address[: raw_address.find(city)].strip()
            else:
                if "West Suss" in raw_address:
                    street_address = raw_address.split("West Suss")[0].strip()

        if "RH6 0PJ" in raw_address:
            zip_code = "RH6 0PJ"
        zip_code = zip_code.replace("BATTERSEA", "").strip()

        country_code = "GB"
        store_number = "<MISSING>"
        latitude = ""
        longitude = ""

        if item.find(string="Order on Deliveroo"):
            location_type = "Delivery only"
        else:
            location_type = "Dine in,  Takeaway + Delivery"
            try:
                map_str = item.find(string="Get Directions").find_previous()["href"]
                geo = re.findall(r"[0-9]{1,3}\.[0-9]+,-[0-9]{1,3}\.[0-9]+", map_str)[
                    0
                ].split(",")
                latitude = geo[0]
                longitude = geo[1]
            except:
                pass

        hours_of_operation = (
            item.find(string="Hours")
            .find_previous("p")
            .text.replace("Hours", "")
            .replace("–", "-")
            .replace("\r\n", " ")
            .replace("\n", " ")
            .replace("—-", "")
            .split("(")[0]
            .strip()
        )

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        try:
            phone = re.findall(
                r"[\d]{5} [\d]{3} [\d]{3}",
                str(base.find(id="section-2")).replace("0192 3886", "01923 886"),
            )[0]
        except:
            phone = "<MISSING>"

        if not latitude:
            try:
                map_link = map_str = base.find_all("iframe")[-1]["data-src"]
                lat_pos = map_link.rfind("!3d")
                latitude = map_link[
                    lat_pos + 3 : map_link.find("!", lat_pos + 5)
                ].strip()
                lng_pos = map_link.find("!2d")
                longitude = map_link[
                    lng_pos + 3 : map_link.find("!", lng_pos + 5)
                ].strip()
            except:
                pass

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
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
