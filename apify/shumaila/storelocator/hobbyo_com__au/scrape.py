from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
from sgselenium.sgselenium import SgChrome

MISSING = SgRecord.MISSING
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

        for div in divlist:

            try:

                title = div.find("h2").text
                address = div.find("p")
                address = re.sub(cleanr, "\n", str(address))
                address = re.sub(pattern, "\n", str(address)).strip()
                address1 = address.splitlines()
                address = address.replace("\n", " ").strip()
                coordlist = div.find("iframe")["src"]
                r = session.get(coordlist, headers=headers)

                lat, longt = (
                    r.text.split('",null,[null,null,', 1)[1].split("]", 1)[0].split(",")
                )

                pa = parse_address_intl(address)

                street_address = pa.street_address_1
                street = street_address if street_address else MISSING

                city = pa.city
                city = city.strip() if city else MISSING

                state = pa.state
                state = state.strip() if state else MISSING

                zip_postal = pa.postcode
                pcode = zip_postal.strip() if zip_postal else MISSING
                street = street.replace("&amp;", "").strip()
                content = re.sub(cleanr, "\n", str(div))
                content = re.sub(pattern, "\n", str(content)).strip()
                phone = content.split("PHONE", 1)[1].split("\n", 1)[1].split("\n", 1)[0]

                city = address1[-1].lower().split(state.lower(), 1)[0].upper()
                try:
                    city = city.split(state.upper(), 1)[0]
                except:
                    pass
                hours = (
                    content.split("OPENING HOURS", 1)[1]
                    .split("\n", 1)[1]
                    .replace("\n", " ")
                    .strip()
                )
                hours = hours.replace("AM ", "AM - ")

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
                    raw_address=address,
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
