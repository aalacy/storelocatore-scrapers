import re

from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

log = sglog.SgLogSetup().get_logger(logger_name="sothebysrealty.com")


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]

    found_poi = []
    locator_domain = "sothebysrealty.com"

    for state in states:
        log.info("Getting data for State: " + state)
        page_next = True
        base_link = (
            "https://www.sothebysrealty.com/eng/offices/" + state.lower() + "-usa/30-pp"
        )

        while page_next:
            req = session.get(base_link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            items = base.find_all("li", {"id": re.compile(r"Entity_180.+")})

            for item in items:
                try:
                    link = "https://www.sothebysrealty.com" + item.a["href"]
                    if link in found_poi:
                        continue
                    found_poi.append(link)
                except:
                    continue

                location_name = item.find(
                    class_="Entities-card__entity-name"
                ).text.strip()
                street_address = (
                    item.find(class_="Entities-card__address")
                    .text.replace("  ", " ")
                    .strip()
                )
                city_line = (
                    item.find_all(class_="Entities-card__address")[1]
                    .text.split("United")[0]
                    .split(",")
                )
                city = city_line[0].strip()
                state = city_line[-1].strip().split()[0].strip()
                zip_code = city_line[-1].strip().split()[1].strip()
                try:
                    phone = item.find(class_="h6").text.replace("O.", "").strip()
                except:
                    phone = "<MISSING>"
                country_code = "US"
                store_number = "<MISSING>"
                location_type = "<MISSING>"
                hours_of_operation = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"

                req = session.get(link, headers=headers)
                if req.status_code != 200:
                    req = session.get(link, headers=headers)

                if req.status_code == 200:
                    page_base = BeautifulSoup(req.text, "lxml")
                    try:
                        map_str = page_base.find(
                            class_="OfficeHero__content-item OfficeHero__content-item--directions"
                        ).a["href"]

                        geo = re.findall(
                            r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", map_str
                        )[0].split(",")
                        latitude = geo[0]
                        longitude = geo[1]
                    except:
                        pass

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

            # Check for next page
            try:
                base_link = (
                    "https://www.sothebysrealty.com"
                    + base.find(class_="Entities-search__pagination").find(
                        "a", attrs={"aria-label": "Next"}
                    )["href"]
                )
                if base_link == "https://www.sothebysrealty.com#":
                    page_next = False
            except:
                page_next = False


with SgWriter(
    SgRecordDeduper(
        SgRecordID(
            {
                SgRecord.Headers.LOCATION_NAME,
                SgRecord.Headers.STREET_ADDRESS,
            }
        )
    )
) as writer:
    fetch_data(writer)
