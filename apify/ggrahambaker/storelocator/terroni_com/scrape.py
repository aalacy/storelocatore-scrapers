from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):
    locator_domain = "https://www.terroni.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(locator_domain, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    all_locs = base.find(id="nav-footer-left").find_all("li")

    link_list = []
    for loc in all_locs:
        link = loc.a["href"]
        if "terroni" in link:
            link_list.append(link)

    for link in link_list:
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        addy = base.find(class_="location-reservation-address")
        location_name = (
            base.find(class_="location-header-name")
            .text.replace("\n", " ")
            .replace("  ", " ")
            .strip()
        )
        phone_number = base.find(class_="location-reservation-telephone").text
        addy_href = addy.a["href"]
        street_addy_idx = addy_href.find("place/") + 6
        coord_start_idx = addy_href.find("/@")
        address = addy_href[street_addy_idx:coord_start_idx].split(",")
        street_address = address[0].replace("+", " ").strip()
        city = address[1].replace("+", " ").strip()
        if "USA" in addy_href:
            addy_split = address[2].replace("+", " ").strip().split(" ")
            state = addy_split[0]
            zip_code = addy_split[1].strip()
            country_code = "US"
        else:
            addy_split = address[2].replace("+", " ").strip().split(" ")
            country_code = "CA"
            if len(addy_split) == 2:
                state = addy_split[0]
                zip_code = "<MISSING>"
            else:
                state = addy_split[0]
                zip_code = addy_split[1] + " " + addy_split[2]
        if "132 Yonge" in street_address:
            zip_code = "M5C 1X3"

        coords = addy_href[coord_start_idx + 2 :].split(",")
        lat = coords[0]
        longit = coords[1]
        hours = ""

        try:
            p_hours = base.find("div", attrs={"data-align": "right"}).find_all("p")[1:]
            for p in p_hours:
                if "day:" in p.text or "HOURS" in p.text:
                    hours = (hours + " " + p.text.replace("\xa0", " ")).strip()
            hours = (
                hours.replace("Wine List", "")
                .replace("HOURS & INFO", "")
                .replace("\n", "")
                .strip()
            )

            if "HOURS" in hours[:5]:
                hours = hours.split("HOURS")[1].strip()
        except:
            pass

        store_number = "<MISSING>"
        location_type = "<MISSING>"

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
                latitude=lat,
                longitude=longit,
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
