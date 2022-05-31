import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests


from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://www.naturalchickengrill.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.findAll("div", attrs={"class": "c-location-list__content"})

    for item in items:
        locator_domain = "naturalchickengrill.com"
        location_name = item.find("a").text.strip()

        raw_data = (
            str(item.find("p", attrs={"class": "c-location-list__info"}))
            .replace("<p>", "")
            .replace("</p>", "")
            .split("<br/>")
        )
        street_address = raw_data[0][raw_data[0].rfind("\t") :].strip()
        raw_data[1] = raw_data[1].strip()
        city = raw_data[1][: raw_data[1].find(" ")].strip()
        state = raw_data[1][raw_data[1].find(" ") + 1 : raw_data[1].rfind(" ")].strip()
        zip_code = raw_data[1][raw_data[1].rfind(" ") + 1 :].strip()
        country_code = "US"
        store_number = "<MISSING>"
        try:
            phone = (
                item.find("a", {"href": re.compile(r"tel:")})
                .text.replace("P", "")
                .strip()
            )
        except:
            phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = item.findAll(
            "div", attrs={"class": "c-location-list__block"}
        )[1]
        hours_of_operation = hours_of_operation.findAll("span", attrs={"class": "s1"})
        hours_list = []
        for hours in hours_of_operation:
            hours_list.append((hours.text.replace("\n", " ").replace("\xa0", " ")))
        hours_of_operation = ", ".join(hours_list)
        hours_of_operation = hours_of_operation.replace(",", "")

        if hours_of_operation == "":
            hours_of_operation = item.findAll(
                "div", attrs={"class": "c-location-list__block"}
            )[1]
            hours_of_operation = (
                hours_of_operation.findAll("p")[2]
                .text.replace("\n", " ")
                .replace("\xa0", " ")
            )
            hours_of_operation = re.sub(" +", " ", hours_of_operation)

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=base_link,
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


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
