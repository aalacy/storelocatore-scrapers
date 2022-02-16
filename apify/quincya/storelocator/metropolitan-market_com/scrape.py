from sgrequests import SgRequests
from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://metropolitan-market.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.findAll("div", attrs={"class": "feature_box"})

    for item in items:
        if "Coming Soon" in item.text or "Opening" in item.text:
            continue

        link = "https://metropolitan-market.com" + item.a["href"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        link = req.url

        locator_domain = "metropolitan-market.com"
        location_name = (
            base.find("h3").text.strip() + " - " + base.find("h2").text.strip()
        )
        section = base.find("div", attrs={"class": "section_col_content"}).p
        raw_data = (
            str(section)
            .replace("<p>", "")
            .replace("</p>", "")
            .replace("\n", "")
            .split("<br/>")
        )
        street_address = raw_data[0].strip()
        city = raw_data[1][: raw_data[1].rfind(",")].strip()
        state = raw_data[1][raw_data[1].rfind(",") + 1 : raw_data[1].rfind(" ")].strip()
        zip_code = raw_data[1][raw_data[1].rfind(" ") + 1 :].strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = base.find("h2", string="Phone").find_next().text
        location_type = "<MISSING>"

        map_link = base.find("a", attrs={"class": "button"})["href"]
        req = session.get(map_link, headers=headers)
        maps = BeautifulSoup(req.text, "lxml")

        try:
            raw_gps = maps.find("meta", attrs={"itemprop": "image"})["content"]
            latitude = raw_gps[raw_gps.find("=") + 1 : raw_gps.find("%")].strip()
            longitude = raw_gps[raw_gps.find("-") : raw_gps.find("&")].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        if "=" in latitude:
            longitude = latitude[latitude.rfind(",") + 1 :].strip()
            latitude = latitude[latitude.rfind("=") + 1 : latitude.rfind(",")].strip()

        hours_of_operation = base.find("h2", string="Hours").find_next().text

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
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
