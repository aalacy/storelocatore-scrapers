import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.discounttirecenters.com/location-detail"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    main_links = []
    main_items = base.find(id="dm_content").find_all("a")
    for main_item in main_items:
        main_link = "https://www.discounttirecenters.com" + main_item["href"]
        main_links.append(main_link)

    for link in main_links:
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        locator_domain = "discounttirecenters.com"

        if (
            "COMING SOON"
            in base.find(id="dm_content").find(class_="dmRespColsWrapper").text.upper()
        ):
            continue

        location_name = (
            " ".join(list(base.h1.stripped_strings)).replace("NEW LOCATION", "").strip()
        )
        base.find("h4", attrs={"data-uialign": "center"})

        city = location_name.split(" in")[1].split(",")[0].strip()
        state = location_name.split(" in")[1].split(",")[1].strip()
        zip_code = ""
        raw_data = list(base.find_all("h4")[-1].stripped_strings)

        hours_of_operation = ""
        if len(raw_data) > 1:
            street_address = raw_data[0].split(city + ",")[0].strip()

            if state in raw_data[0]:
                zip_code = raw_data[0].split(state)[-1].strip()
            elif state in raw_data[1]:
                zip_code = raw_data[1].split(state)[-1].strip()
            else:
                zip_code = "<MISSING>"

            phone = raw_data[-2]
            if "," in phone:
                phone = raw_data[-1]

            try:
                hours_of_operation = " ".join(
                    list(base.find(id="main").stripped_strings)
                )
            except:
                pass
        else:
            try:
                new_raw_data = base.find(
                    class_="m-font-size-11 font-size-14"
                ).text.strip()
                street_address = (
                    new_raw_data.split(city + ",")[0].replace(",", "").strip()
                )

                if state in new_raw_data:
                    zip_code = new_raw_data.split(state)[-1].strip()
                elif state in new_raw_data:
                    zip_code = new_raw_data.split(state)[-1].strip()
                else:
                    zip_code = "<MISSING>"

                phone = base.find(class_="m-font-size-14 font-size-18").text.strip()
                hours_of_operation = base.find_all(class_="dmNewParagraph")[3].get_text(
                    " "
                )
                if "day" not in hours_of_operation:
                    try:
                        hours_of_operation = " ".join(
                            list(base.find(id="main").stripped_strings)
                        )
                    except:
                        pass
            except:
                new_raw_data2 = list(
                    base.find_all(class_="dmNewParagraph")[3].stripped_strings
                )
                street_address = new_raw_data2[0].split(city)[0].strip()
                phone = new_raw_data2[1]
                if not zip_code:
                    zip_code = new_raw_data2[0].split(city)[1].strip().split()[1]

        if not hours_of_operation or "day" not in hours_of_operation:
            hours_of_operation = " ".join(
                list(base.find(class_="open-hours-data").stripped_strings)
            )

        if street_address[-1] == ",":
            street_address = street_address[:-1]

        zip_code = zip_code.replace(",", "").strip()

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", str(base))[0].split(
            ","
        )
        latitude = geo[0]
        longitude = geo[1]

        if "4304 West Shaw" in street_address:
            latitude = "36.808608"
            longitude = "-119.86938"

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
