import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests
from sglogging import SgLogSetup

from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("chopard_com")

session = SgRequests()


def fetch_data(sgw: SgWriter):

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
        "accept": "application/json, text/javascript, */*; q=0.01",
    }

    # it will used in store data.
    locator_domain = "https://www.chopard.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    get_data_url = "https://www.chopard.com/intl/storelocator"
    r = session.get(get_data_url, headers=headers)

    soup = BeautifulSoup(r.text, "lxml")
    json_data = json.loads(
        soup.find("select", {"class": "country-field"})
        .find_previous("script")
        .text.replace("var preloadedStoreList =", "")
        .replace(";", "")
        .strip()
    )
    for x in json_data["stores"]:
        page_url = x["details_url"]
        store_number = x["store_code"]
        location_name = x["name"].capitalize()
        if x["address_2"] is None and x["address_3"] is None:
            raw_address = x["address_1"]
        elif x["address_2"] is not None and x["address_3"] is None:
            raw_address = x["address_1"] + " " + x["address_2"]
        elif (
            x["address_1"] is not None
            and x["address_2"] is not None
            and x["address_3"] is not None
        ):
            raw_address = x["address_1"] + " " + x["address_2"] + " " + x["address_3"]
        city = (
            x["city"]
            .replace(", MICHOACAN, MEXICO", "")
            .replace("()", "")
            .replace("- COLOMBIA", "")
            .strip()
        )
        try:
            zipp = x["zipcode"].replace(".", "").replace(",", "")
        except:
            zipp = ""

        if "St Julians" in zipp:
            zipp = city
            city = "St Julians"

        if zipp == "-" or zipp == "00000":
            zipp = ""

        latitude = x["lat"]
        longitude = x["lng"]
        if x["phone"] is not None:
            phone = x["phone"].replace("\u200e", "")
        else:
            phone = "<MISSING>"
        if len(phone) < 3:
            phone = ""

        country_code = x["country_id"]
        page_url = x["details_url"]

        raw_address = raw_address.replace("<", "").replace(">", "").strip()
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        state = parse_address_intl(city).state
        if not state:
            parse_address_intl(zipp).state
        try:
            city = city.replace(state, "").strip()
        except:
            pass
        try:
            zipp = zipp.replace(state, "").strip()
        except:
            pass

        if country_code == "AU":
            if not zipp.split()[0].isdigit():
                state = zipp.split()[0]
                zipp = zipp.split()[1]

        if city[-1:] == ",":
            city = city[:-1]
        city = city.replace("()", "").strip()

        if not street_address or len(street_address) < 5:
            street_address = raw_address

        r_loc = session.get(page_url, headers=headers)
        soup_loc = BeautifulSoup(r_loc.text, "lxml")
        col = (
            soup_loc.find("div", class_="columns")
            .find("div", class_="info-column")
            .find("div", class_="shop-details")
        )
        hours = col.find("p", class_="opening")
        if hours is not None:
            h = hours.nextSibling.nextSibling
            h_list = list(h.stripped_strings)
            hours_of_operation = (
                " ".join(h_list)
                .replace("\r\n", " ")
                .replace("REDUCED HOURS - Please call the Boutique", "")
                .replace("Reduced Hours", "")
                .replace("* Open during summer time *", "")
                .split("- Close")[0]
                .strip()
            )
        else:
            hours_of_operation = "<MISSING>"

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
