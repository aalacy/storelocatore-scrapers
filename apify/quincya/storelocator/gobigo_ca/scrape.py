from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = (
        "https://apps.elfsight.com/p/boot/?w=84eca792-36b8-45b6-9851-465cd482c3d2"
    )

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["data"]["widgets"][
        "84eca792-36b8-45b6-9851-465cd482c3d2"
    ]["data"]["settings"]["markers"]

    locator_domain = "https://gobigo.ca/"

    for store in stores:
        location_name = store["infoTitle"]
        raw_address = store["position"].split(",")
        street_address = raw_address[0].strip()
        if "BC" in str(raw_address):
            state = "BC"
        elif "AB" in str(raw_address):
            state = "AB"
        else:
            state = ""
        if state:
            city = raw_address[1].split(state)[0].strip()
            try:
                zip_code = (
                    raw_address[-1].split(state)[1].replace("*", "8").strip().upper()
                )
            except:
                raw_address = store["infoAddress"].split(",")
                zip_code = (
                    raw_address[2].split(state)[1].replace("*", "8").strip().upper()
                )
        else:
            city = raw_address[1].strip()
            zip_code = raw_address[-1].strip()
        if not zip_code:
            if "7380 Gilley Avenue" in street_address:
                zip_code = "V5J 4X5"
            elif "V7P 1B7" in str(store):
                zip_code = "V7P 1B7"
            else:
                zip_code = ""
        country_code = "CA"
        location_type = "<MISSING>"
        phone = store["infoPhone"].strip()
        store_number = "<MISSING>"
        try:
            latitude = store["coordinates"].split(",")[0].strip()
            longitude = store["coordinates"].split(",")[1].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        link = store["infoSite"]
        if link == "https://www.bigotireswestvan.ca":
            link = "https://bigotireswestvan.ca/westshore-hometeam/"
        if link == "https://www.bigotirespoco.ca":
            link = "https://www.bigotirespoco.ca/westshore-hometeam/"
        if link == "https://www.bigotiresvictoria.com":
            link = "https://www.bigotiresvictoria.com/Contact-Us"
        if link:
            req = session.get(link, headers=headers)
            if req.status_code:
                base = BeautifulSoup(req.text, "lxml")
                try:
                    hours_of_operation = " ".join(
                        list(
                            base.find_all(class_="list simple margin-top-20")[
                                -1
                            ].stripped_strings
                        )
                    )
                except:
                    try:
                        hours_of_operation = (
                            base.find(class_="ourloc wrapper")
                            .find_all("p")[-1]
                            .text.strip()
                        )
                    except:
                        try:
                            hours_of_operation = (
                                " ".join(
                                    list(
                                        base.find_all(class_="locationhours")[
                                            -1
                                        ].stripped_strings
                                    )
                                )
                                .replace("Hours:", "")
                                .strip()
                            )
                        except:
                            try:
                                hours_of_operation = (
                                    base.find(class_="locwidget-hours")
                                    .text.replace("Hours:", "")
                                    .strip()
                                )
                            except:
                                try:
                                    hours_of_operation = (
                                        base.find_all(
                                            class_="left-aligned secondaryHPT"
                                        )[-1]
                                        .text.split("open")[1]
                                        .split(".")[0]
                                        .strip()
                                    )
                                except:
                                    hours_of_operation = "<MISSING>"
                hours_of_operation = (
                    hours_of_operation.replace("PMSat", "PM Sat")
                    .replace("Hours", "")
                    .split("Holidays: view")[0]
                    .strip()
                )
                if latitude == "<MISSING>":
                    try:
                        map_link = base.iframe["src"]
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
            else:
                link = "https://gobigo.ca/#/!search?season_id=all&search_by=size"
                hours_of_operation = "<MISSING>"
        else:
            link = "https://gobigo.ca/#/!search?season_id=all&search_by=size"
            hours_of_operation = "<MISSING>"

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
