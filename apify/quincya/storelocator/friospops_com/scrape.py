from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("friospops_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://friospops.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="entry-title")

    final_links = []
    for item in items:
        final_links.append(item.a["href"])

    for final_link in final_links:
        if "/mobile" in final_link:
            continue

        logger.info(final_link)

        req = session.get(final_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        locator_domain = "friospops.com"
        location_name = "Frios Gourmet Pops - " + base.find_all(
            class_="elementor-text-editor elementor-clearfix"
        )[0].text.replace("\t", "").replace("\n", "")
        try:
            raw_address = (
                base.find_all(class_="elementor-text-editor elementor-clearfix")[2]
                .p.text.strip()
                .split("\n")
            )
        except:
            raw_address = (
                base.find_all(class_="elementor-text-editor elementor-clearfix")[3]
                .text.strip()
                .split("\n")
            )

        try:
            if not raw_address.strip():
                continue
        except:
            pass

        location_type = "<MISSING>"

        if len(raw_address) == 1 and ", Suite" in raw_address[0]:
            raw_address = raw_address[0].replace(", Suite", " Suite").split(",")
            street_address = raw_address[0].strip()
            city = raw_address[1].strip()
            state = raw_address[-1].split()[0].strip()
            zip_code = raw_address[-1][-6:].strip()

        elif raw_address != "Historic Downtown McKinney":
            if "coming soon" in str(raw_address).lower():
                continue
            try:
                street_address = raw_address[-3].strip() + " " + raw_address[-2].strip()
            except:
                try:
                    street_address = raw_address[-2].strip()
                except:
                    street_address = "<MISSING>"

            city_line = raw_address[-1].split(",")
            city = city_line[0].strip()
            zip_code = city_line[-1][-6:].strip()
            if zip_code.isnumeric():
                state = city_line[1].split()[0].strip()
            else:
                try:
                    state = city_line[1].strip()
                    zip_code = "<MISSING>"
                except:
                    try:
                        street_address = raw_address[0].strip()
                        city_line = raw_address[1].split(",")
                        city = city_line[0].strip()
                        state = city_line[1].split()[0].strip()
                        zip_code = city_line[-1][-6:].strip()
                    except:
                        city = location_name.split("in ")[-1].split(",")[0]
                        try:
                            state = location_name.split("in ")[-1].split(",")[1].strip()
                        except:
                            state = "<MISSING>"
        else:
            street_address = "Historic Downtown"
            city = "McKinney"
            state = "TX"
            zip_code = "<MISSING>"

        if (
            "come to you" in street_address
            and "Charlotte, NC"
            in base.find_all(class_="elementor-text-editor elementor-clearfix")[
                1
            ].p.text
        ):
            street_address = "<MISSING>"
            city = "Charlotte"
            state = "NC"
            zip_code = "<MISSING>"
        if "fun van" in street_address.lower():
            street_address = "<MISSING>"

        if "569 1st St" in street_address:
            zip_code = "35007"

        if "241 W Main" in street_address:
            street_address = "241 W Main St."
        if (
            "The Frios Mobile" in street_address
            or "Frios Cart" in street_address
            or "we come to you" in base.text.lower()
        ):
            street_address = "<MISSING>"
            location_type = "The Frios Mobile"

        street_address = street_address.replace(
            "TBD", "<MISSING>".replace("Frios Cart", "<MISSING>")
        )
        country_code = "US"
        store_number = "<MISSING>"
        phone = base.find_all(class_="elementor-text-editor elementor-clearfix")[
            3
        ].text.strip()
        if "-" not in phone:
            phone = base.find_all(class_="elementor-text-editor elementor-clearfix")[
                4
            ].text.strip()
        if "-" not in phone:
            phone = base.find_all(class_="elementor-text-editor elementor-clearfix")[
                5
            ].text.strip()
        if "-" not in phone:
            phone = "<MISSING>"

        hours = base.find_all(class_="elementor-text-editor elementor-clearfix")[4:15]
        hours_of_operation = "<MISSING>"
        for row in hours:
            if "day:" in row.text.lower():
                hours_of_operation = (
                    row.text.replace("*Poppy Hour", "").replace("\n", " ").strip()
                )
        hours_of_operation = (
            hours_of_operation.replace("–", "-").split("(Deliver")[0].strip()
        )

        if hours_of_operation.count("Varies") > 4:
            hours_of_operation = "<MISSING>"

        if hours_of_operation.count("TBD") > 4:
            hours_of_operation = "<MISSING>"

        if "TBD" in phone.upper():
            phone = "<MISSING>"
        if city.lower() == "city":
            city = location_name.split("in")[-1].strip()
            state = "<MISSING>"
        if not zip_code.isdigit():
            zip_code = "<MISSING>"
        if "Keller, Texas" in location_name:
            street_address = street_address.replace("Keller", "").strip()
            city = "Keller"
        if "Lake Conroe" in city:
            city = "Montgomery"
            state = "TX"
        if "Pflugerville" in city:
            state = "TX"
        if "Pop cart!" in street_address:
            street_address = "<MISSING>"
            location_type = "The Frios Mobile"
        if "University" in city:
            state = ""
            street_address = " ".join(city.split()[:-1]).strip()
        if "Frios Sweet" in street_address:
            street_address = "<MISSING>"
            location_type = "The Frios Mobile"

        if street_address != "<MISSING>":
            location_type = "The Frios Location"

        if not state or len(state) > 20 or "Love" in state:
            city = (
                base.find_all(class_="elementor-heading-title elementor-size-default")[
                    1
                ]
                .text.replace("-", ",")
                .split(",")[0]
                .strip()
            )
            state = (
                base.find_all(class_="elementor-heading-title elementor-size-default")[
                    1
                ]
                .text.replace("-", ",")
                .split(",")[1]
                .strip()
            )

        if city == "City":
            city = ""
            state = ""

        if city == "Northeast Georgia":
            city = ""
            state = "Georgia"
        if "Columbia, South Carolina" in location_name:
            city = "Columbia"
            state = "South Carolina"
        if "Rock Hill" in location_name:
            city = "Rock Hill"
            state = "SC"

        latitude = "<MISSING>"
        longitude = "<MISSING>"

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
