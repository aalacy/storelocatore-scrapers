from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("carrabbas.com")


def fetch_data(sgw: SgWriter):

    base_link = "https://locations.carrabbas.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link + "index.html", headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    main_links = []
    final_links = []

    main_items = base.find_all(class_="Directory-listLink")
    for main_item in main_items:
        main_link = base_link + main_item["href"]
        count = main_item["data-count"].replace("(", "").replace(")", "").strip()
        if count == "1":
            final_links.append(main_link)
        else:
            main_links.append(main_link)

    for main_link in main_links:
        logger.info(main_link)
        req = session.get(main_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        next_items = base.find_all(class_="Directory-listLink")
        if next_items:
            for next_item in next_items:
                next_link = base_link + next_item["href"]
                count = (
                    next_item["data-count"].replace("(", "").replace(")", "").strip()
                )

                if count == "1":
                    final_links.append(next_link)
                else:
                    next_req = session.get(next_link, headers=headers)
                    next_base = BeautifulSoup(next_req.text, "lxml")

                    final_items = next_base.find_all(class_="Teaser-titleLink")
                    for final_item in final_items:
                        final_link = (base_link + final_item["href"]).replace("../", "")
                        final_links.append(final_link)
        else:
            final_items = base.find_all(class_="Teaser-titleLink")
            for final_item in final_items:
                final_link = (base_link + final_item["href"]).replace("../", "")
                final_links.append(final_link)

    total_links = len(final_links)
    logger.info("Processing %s links .." % (total_links))
    for final_link in final_links:
        final_req = session.get(final_link, headers=headers)
        item = BeautifulSoup(final_req.text, "lxml")

        locator_domain = "carrabbas.com"

        try:
            location_name = item.find(id="location-name").text.strip()
            got_loc = True
            if "COMING SOON" in location_name.upper():
                continue
        except:
            got_loc = False

        if got_loc:
            street_address = item.find(class_="c-address-street-1").text.strip()
            try:
                street_address = (
                    street_address
                    + " "
                    + item.find(class_="c-address-street-2").text.strip()
                )
                street_address = street_address.strip()
            except:
                pass

            city = item.find(class_="c-address-city").text.strip()
            state = item.find(class_="c-address-state").text.strip()
            zip_code = item.find(class_="c-address-postal-code").text.strip()

            try:
                phone = item.find("div", attrs={"itemprop": "telephone"}).text.strip()
                if not phone:
                    phone = "<MISSING>"
            except:
                phone = "<MISSING>"
        else:
            final_link = final_link[: final_link.rfind("/")]
            final_req = session.get(final_link, headers=headers)
            base = BeautifulSoup(final_req.text, "lxml")
            location_name = base.find(class_="Teaser-title").text.strip()
            street_address = base.find(class_="c-address-street-1").text.strip()
            try:
                street_address = (
                    street_address
                    + " "
                    + base.find(class_="c-address-street-2").text.strip()
                )
                street_address = street_address.strip()
            except:
                pass

            city = base.find(class_="c-address-city").text.strip()
            state = base.find(class_="c-address-state").text.strip()
            zip_code = base.find(class_="c-address-postal-code").text.strip()

            try:
                phone = base.find(class_="Phone-link").text.strip()
                if not phone:
                    phone = "<MISSING>"
            except:
                phone = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        try:
            latitude = item.find("meta", attrs={"itemprop": "latitude"})["content"]
            longitude = item.find("meta", attrs={"itemprop": "longitude"})["content"]
        except:
            latitude = ""
            longitude = ""

        try:
            hours_of_operation = " ".join(
                list(item.find(class_="c-hours-details").tbody.stripped_strings)
            )
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"
        except:
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
