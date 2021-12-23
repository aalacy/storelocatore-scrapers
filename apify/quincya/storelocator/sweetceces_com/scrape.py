import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "http://www.sweetceces.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)

    base = BeautifulSoup(req.text, "lxml")

    content = base.find("div", attrs={"id": "main-content"})
    items = content.findAll("li")

    base.findAll("div", attrs={"class": "container"})[2]

    for item in items:
        if "Coming Soon" in item.text:
            continue
        else:
            location_type = "<MISSING>"
        final_link = item.a["href"]
        if "coming-soon" in final_link:
            continue

        req = session.get(final_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        content = base.find("div", attrs={"id": "main-content"})
        locator_domain = "sweetceces.com"

        raw_data = (
            str(content.find("p")).replace("</p>", "").replace("\n", "").split("<br/>")
        )
        location_name = raw_data[0][raw_data[0].rfind(">") + 1 :].strip()
        if location_name != "":
            street_address = raw_data[1].replace(",", "").strip()
            city = raw_data[2][: raw_data[2].find(",")].strip()
            state = raw_data[2][
                raw_data[2].find(",") + 1 : raw_data[2].rfind(" ")
            ].strip()
            zip_code = raw_data[2][raw_data[2].rfind(" ") + 1 :].strip()
        else:
            location_name = raw_data[1].strip()
            street_address = raw_data[2].strip()
            city = raw_data[3][: raw_data[3].find(",")].strip()
            state = raw_data[3][
                raw_data[3].find(",") + 1 : raw_data[3].rfind(" ")
            ].strip()
            zip_code = raw_data[3][raw_data[3].rfind(" ") + 1 :].strip()
        street_address = street_address.replace("The Avenue –", "").strip()
        country_code = "US"
        store_number = "<MISSING>"
        try:
            phone = re.findall(r"[\d]{3}-[\d]{3}-[\d]{4}", str(content.find("p")))[0]
        except:
            if "Cool Springs" in location_name:
                phone = raw_data[-1][
                    raw_data[-1].find(" ") + 1 : raw_data[-1].find("<")
                ]
                phone = (
                    phone
                    + raw_data[-1][
                        raw_data[-1].find('">') + 2 : raw_data[-1].find('">') + 6
                    ]
                )
            else:
                phone = "<MISSING>"

        link = base.findAll("iframe")[1]["src"]
        start_point = link.find("2d") + 2
        longitude = link[start_point : link.find("!", start_point)]
        long_start = link.find("!", start_point) + 3
        latitude = link[long_start : link.find("!", long_start)]

        hours_of_operation = "<MISSING>"

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=final_link,
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
