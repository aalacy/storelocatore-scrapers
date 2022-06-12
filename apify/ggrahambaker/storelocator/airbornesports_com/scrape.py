import re

from bs4 import BeautifulSoup

from sgpostal.sgpostal import parse_address_usa

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data(sgw: SgWriter):

    url = "https://airbornesports.com/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "lxml")
    divlist = soup.find("div", {"id": "choose-location"}).findAll(
        "a", {"class": "fusion-button"}
    )
    for div in divlist:

        title = div.text
        if "airbornelewisville" in div["href"]:
            link = div["href"] + "contact"
        else:
            link = div["href"] + "contact-us"
        r = session.get(link, headers=headers, verify=False)
        r2 = session.get(div["href"], headers=headers, verify=False)
        soup = BeautifulSoup(r2.text, "lxml")
        address = r.text.split('"address":"', 1)[1].split('"', 1)[0].replace(",", "")
        addr = parse_address_usa(address)
        street = addr.street_address_1
        if addr.street_address_2:
            street = street + " " + addr.street_address_2
        street = street.replace("\\Nsouth", "").strip()
        city = addr.city
        if city == "Jordan":
            city = "South Jordan"
        state = addr.state
        pcode = addr.postcode
        try:
            lat = r.text.split('"latitude":"', 1)[1].split('"', 1)[0]
            longt = r.text.split('"longitude":"', 1)[1].split('"', 1)[0]
        except:
            try:
                lat = r.text.split('"mapLat":', 1)[1].split(",", 1)[0]
                longt = r.text.split('"mapLng":', 1)[1].split(",", 1)[0]
            except:
                lat = longt = "<MISSING>"
        try:
            phone = re.findall(r"[(\d)]{3}-[\d]{3}-[\d]{4}", r.text)[0]
        except:
            phone = "<MISSING>"

        if not city:
            street = r.text.split('"addressLine1":"', 1)[1].split('"', 1)[0]
            city, state, pcode = (
                r.text.split('"addressLine2":"', 1)[1].split('"', 1)[0].split(", ")
            )
            lat = r.text.split('"mapLat":', 1)[1].split(",", 1)[0]
            longt = r.text.split('"mapLng":', 1)[1].split(",", 1)[0]
            phone = r.text.split('"contactPhoneNumber":"', 1)[1].split('"', 1)[0]
            phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:10]

        try:
            hourslist = r.text.split('"businessHours":{', 1)[1].split(
                ',"storeSettings"', 1
            )[0]
            hourslist = hourslist.split('"text":"')
            hours = (
                "Monday "
                + hourslist[1].split('",', 1)[0]
                + " Tuesday "
                + hourslist[2].split('",', 1)[0]
                + " Wednesday "
                + hourslist[3].split('",', 1)[0]
                + " Thursday "
                + hourslist[4].split('",', 1)[0]
                + " Friday "
                + hourslist[5].split('",', 1)[0]
                + " Saturday "
                + hourslist[6].split('",', 1)[0]
                + " Sunday "
                + hourslist[7].split('",', 1)[0]
            )
        except:
            try:
                hours = (
                    soup.find(
                        class_="fusion-builder-row fusion-builder-row-inner fusion-row"
                    )
                    .get_text(" ")
                    .replace("\n", "")
                )
                hours = (re.sub(" +", " ", hours)).strip()
            except:
                hours = "<MISSING>"

            hours = (
                hours.replace("Open Jump (all ages)", "")
                .replace(": Midnight  Teen Flight Night", "")
                .replace("Weekday’s Open Til 8 PM", "")
                .replace("Weekday’s Open Til 9 PM", "")
                .replace("Open until 9 PM", "")
                .replace("Open Jump Open until 11pm", "")
                .split("Sundays")[0]
                .strip()
            )
            hours = (re.sub(" +", " ", hours)).strip()

        sgw.write_row(
            SgRecord(
                locator_domain="https://airbornesports.com/",
                page_url=link.replace("contact-us", "").replace("contact", ""),
                location_name=title,
                street_address=street,
                city=city,
                state=state,
                zip_postal=pcode,
                country_code="US",
                store_number="<MISSING>",
                phone=phone,
                location_type="<MISSING>",
                latitude=lat,
                longitude=longt,
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
