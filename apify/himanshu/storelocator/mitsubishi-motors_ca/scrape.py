import httpx

from bs4 import BeautifulSoup

from google_trans_new import google_translator

from sglogging import sglog

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

translator = google_translator()

log = sglog.SgLogSetup().get_logger("www.mitsubishi-motors.ca")

timeout = httpx.Timeout(10.0, connect=10.0)


def fetch_data(sgw: SgWriter):
    session = SgRequests(timeout_config=timeout)
    base_url = "https://www.mitsubishi-motors.ca/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
    }

    link = "https://www.mitsubishi-motors.ca/api/ev_dealer.json"
    json_data = session.get(link, headers=headers).json()

    for loc in json_data:
        address = loc["CompanyAddress"].strip()
        name = loc["CompanyName"].strip()
        city = loc["CompanyCity"].strip().capitalize()
        state = loc["ProvinceAbbreviation"].strip()
        zipp = loc["CompanyPostalCode"].replace("S4R R8R", "S4R 0X3")
        phone = loc["CompanyPhone"].strip()
        lat = loc["Latitude"]
        lng = loc["Longitude"]
        page_url = loc["PrimaryDomain"]
        storeno = loc["CompanyId"]

        hours = ""
        log.info(page_url)
        try:
            r1 = session.get(page_url, headers=headers)
            soup1 = BeautifulSoup(r1.text, "lxml")
        except:
            session = SgRequests(timeout_config=timeout)
            try:
                r1 = session.get(page_url, headers=headers)
                soup1 = BeautifulSoup(r1.text, "lxml")
            except:
                hours = "<INACCESSIBLE>"

        if not hours:
            try:
                hours = " ".join(
                    list(
                        soup1.find(
                            "ul", {"class": "list-unstyled line-height-condensed"}
                        ).stripped_strings
                    )
                )
            except:
                pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find(
                                "ul", {"class": "opening-hours-ul"}
                            ).stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find(
                                "div", {"class": "footer-hours-col sales-hours"}
                            ).li.stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(soup1.find("table", {"class": "hours"}).stripped_strings)
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find(
                                "div", {"id": "tabs-template-hours1"}
                            ).stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find(
                                "div", {"id": "slshours_footer_home"}
                            ).stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(soup1.find("div", {"id": "HOPSales"}).stripped_strings)
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find(
                                "table", {"class": "hours_table"}
                            ).stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find(
                                "div", {"id": "Sales36412421385f59c2556d399"}
                            ).stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find(
                                "table", {"class": "grid-y department-hours"}
                            ).stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find(
                                "table", {"class": "map_open_hours"}
                            ).stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find("div", {"class": "map_open_hours"})
                            .find("li")
                            .stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find(
                                "table", {"class": "footer-hours-tabs__box-wrapper"}
                            ).stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find(
                                "div", {"id": "footer-hours-loc-0-sales"}
                            ).stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find(
                                "div", {"class": "dynamic-hours parts"}
                            ).stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find(
                                "ul", {"class": "list-unstyled line-height-condensed"}
                            ).stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find(
                                "div", {"class": "hours-default"}
                            ).stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find(
                                "div", {"class": "hours1-app-root"}
                            ).stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find(
                                "table", {"class": "beaucage_hours"}
                            ).stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find(
                                "div", {"class": "footer-column footer-column--hours"}
                            ).stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find("div", {"class": "hours-list"}).stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find(
                                "table", {"class": "schedule-table"}
                            ).stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find(
                                "div", {"id": "slshours_footer_home"}
                            ).stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find(
                                "div", {"class": "footer-hours"}
                            ).stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find(
                                "div", {"class": "hours-footer hours-footer-1"}
                            ).stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find(
                                "div", {"class": "footer_dealer_info_hours"}
                            ).stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    hours = " ".join(
                        list(
                            soup1.find_all("ul", {"class": "footer-column__list"})[
                                1
                            ].stripped_strings
                        )
                    )
                except:
                    pass
            if not hours:
                try:
                    if (
                        "Today"
                        in soup1.find(class_="top-bar")
                        .find_all(class_="header-contact__link")[1]
                        .text
                    ):
                        hours = "<INACCESSIBLE>"
                except:
                    pass

        hours = (
            hours.replace("Heures d'ouverture", "")
            .replace("Days Hours", "")
            .replace("HOURS", "")
            .replace("Hours", "")
            .replace("Hours:", "")
            .replace("Sales", "")
            .replace("Horaires:", "")
            .replace("Business hours", "")
            .replace("of Operation", "")
            .replace(":  Mon", "Mon")
            .replace("Dealership hours of operation", "")
            .split("Tell us")[0]
            .split("Avisez-nous")[0]
            .split("See All")[0]
            .split("Service")[0]
            .strip()
        )
        try:
            hours = (
                translator.translate(hours, lang_tgt="en")
                .split("Service")[0]
                .replace("Opening hours", "")
                .replace("Business hours", "")
                .split("Notify us of your visit!")[0]
                .strip()
            )
        except:
            pass
        if city == "N.d.p, joliette":
            city = "Joliette"
            address = address + str(", N.D.P")

        sgw.write_row(
            SgRecord(
                locator_domain=base_url,
                page_url=page_url,
                location_name=name,
                street_address=address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code="CA",
                store_number=storeno,
                phone=phone,
                location_type="<MISSING>",
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours.strip(),
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
