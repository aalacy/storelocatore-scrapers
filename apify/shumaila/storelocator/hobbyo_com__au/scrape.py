from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

import ssl

ssl._create_default_https_context = ssl._create_unverified_context
from sgselenium.sgselenium import SgChrome


session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    cleanr = re.compile(r"<[^>]+>")

    pattern = re.compile(r"\s\s+")

    url = "https://blog.hobbyco.com.au/about/stores/"

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    with SgChrome(user_agent=user_agent) as driver:

        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        divlist = soup.findAll("section")
        coordlist = soup.findAll("iframe")

        i = 0
        for div in divlist:

            try:
                title = div.find("h2").text
                address = div.find("p")
                address = re.sub(cleanr, "\n", str(address))
                address = re.sub(pattern, "\n", str(address)).strip()
                address = address.split("\n")

                state = address[-1].split(" ")[-2]
                pcode = address[-1].split(" ")[-1]
                city = address[-1].split(state, 1)[0]
                street = (
                    " ".join(address[0 : len(address) - 1]).replace("&amp;", "").strip()
                )
                content = re.sub(cleanr, "\n", str(div))
                content = re.sub(pattern, "\n", str(content)).strip()
                phone = content.split("PHONE", 1)[1].split("\n", 1)[1].split("\n", 1)[0]

                hours = (
                    content.split("OPENING HOURS", 1)[1]
                    .split("\n", 1)[1]
                    .replace("\n", " ")
                    .strip()
                )

                r = session.get(coordlist[i]["src"], headers=headers)

                lat, longt = (
                    r.text.split('",null,[null,null,', 1)[1].split("]", 1)[0].split(",")
                )

                i = i + 1
                yield SgRecord(
                    locator_domain="https://www.hobbyco.com.au/",
                    page_url="<MISSING>",
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode.strip(),
                    country_code="AU",
                    store_number=SgRecord.MISSING,
                    phone=phone.strip(),
                    location_type=SgRecord.MISSING,
                    latitude=str(lat),
                    longitude=str(longt),
                    hours_of_operation=hours.encode("ascii", "ignore").decode("ascii"),
                )
            except:
                continue


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
