from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("massmutual_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://financialprofessionals.massmutual.com/us"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    all_links = []
    found_poi = []

    states = base.find(class_="list-unstyled search-by-state-list").find_all("a")
    locator_domain = "massmutual.com"

    for state in states:
        logger.info("Getting links for State: " + state.text)
        state_link = "https://financialprofessionals.massmutual.com" + state["href"]

        try:
            req = session.get(state_link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
        except:
            logger.info("Retrying ..")
            session = SgRequests()
            req = session.get(state_link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

        cities = base.find(class_="list-unstyled search-by-city-list").find_all("a")
        for city in cities:
            city_link = "https://financialprofessionals.massmutual.com" + city["href"]

            try:
                req = session.get(city_link, headers=headers)
                base = BeautifulSoup(req.text, "lxml")
            except:
                logger.info("Retrying ..")
                session = SgRequests()
                req = session.get(city_link, headers=headers)
                base = BeautifulSoup(req.text, "lxml")

            city_data = base.find_all(class_="media-body row")
            for row in city_data:
                link = (
                    "https://financialprofessionals.massmutual.com"
                    + row.find(class_="media-title").a["href"]
                )
                name = row.find(class_="media-title").text
                raw_address = list(row.address.stripped_strings)
                street_address = raw_address[0].strip().replace("  ", " ")
                city_line = raw_address[-1].strip().split(",")
                city = city_line[0].strip()
                state = city_line[-1].strip().split()[0].strip()
                zip_code = city_line[-1].strip().split()[1].strip()
                try:
                    loc_type = row.find(class_="media-subtitle").text
                except:
                    loc_type = "<MISSING>"
                phone = (
                    row.find(class_="sr-only")
                    .find_previous("a")
                    .text.replace("phone", "")
                )

                if link not in all_links:
                    all_links.append(
                        [
                            link,
                            name,
                            street_address,
                            city,
                            state,
                            zip_code,
                            loc_type,
                            phone,
                            city_link,
                        ]
                    )

    logger.info("Processing " + str(len(all_links)) + " potential links ..")
    for row in all_links:
        link = row[0]
        try:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
        except:
            logger.info("Retrying ..")
            session = SgRequests()
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

        got_page = True
        try:
            location_name = base.find(class_="es-agency-name").text.strip()
        except:
            got_page = False

        country_code = "US"
        store_number = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        if got_page:
            street_address = base.find(class_="es-street-address").text.strip()

            loc_str = location_name + "_" + street_address
            if loc_str in found_poi:
                continue
            found_poi.append(loc_str)

            city = base.find(class_="es-address-locality").text.strip()
            state = base.find(class_="es-address-region").text.strip().upper()
            zip_code = (
                base.find(class_="es-postal-code")
                .text.replace("050301", "05301")
                .strip()
            )
            if len(zip_code) == 4:
                zip_code = "0" + zip_code
            try:
                location_type = base.find(class_="title es-office-type").text.strip()
            except:
                location_type = row[6]
            phone = base.find(class_="es-telephone").text.strip()
            if not phone:
                if row[6]:
                    phone = row[6]
                else:
                    phone = "<MISSING>"
            lat = float(base.find(class_="es-street-address")["data-geo"].split(",")[0])
            lon = float(base.find(class_="es-street-address")["data-geo"].split(",")[1])

            latitude = format(lat, ".4f")
            longitude = format(lon, ".4f")
            if latitude == "0.0000":
                latitude = ""
                longitude = ""
        else:
            link = row[-1]
            location_name = row[1]
            street_address = row[2]
            city = row[3]
            state = row[4]
            zip_code = row[5]
            loc_type = row[6]
            phone = row[7]

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
