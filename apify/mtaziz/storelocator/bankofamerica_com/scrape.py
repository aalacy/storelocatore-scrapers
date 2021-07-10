from sgzip.static import static_zipcode_list, SearchableCountries
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("bankofamerica_com")
MISSING = "<MISSING>"
DOMAIN = "https://www.bankofamerica.com/"
headers_authority_simple = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}


# Cralwer tested 200, 100, and 50 radius
# that returns samenumber of items
zips = static_zipcode_list(radius=200, country_code=SearchableCountries.USA)
session = SgRequests()


def get_phone(data):
    phone_list = []
    maplist = data["maplist"]
    maplist_ph = maplist.split('"local_phone":"')
    for p in maplist_ph[1:]:
        phone = p.split('"')[0]
        if phone:
            phone_list.append(phone)
        else:
            phone_list.append("<MISSING>")
    return phone_list


def get_branch_atm_hoo(branch_hours, atm_hrs):

    sep = " - "
    loctype = atm_hrs["location_type"]
    if loctype == "Branch" and "days" in branch_hours:
        fri = branch_hours["days"]["Friday"]
        if isinstance(fri, list):
            frioc = fri[0]["open"] + sep + fri[0]["close"]
        else:
            frioc = fri

        sat = branch_hours["days"]["Saturday"]
        if isinstance(sat, list):
            satoc = sat[0]["open"] + sep + sat[0]["close"]
        else:
            satoc = sat

        sun = branch_hours["days"]["Sunday"]
        if isinstance(sun, list):
            sunoc = sun[0]["open"] + sep + sun[0]["close"]
        else:
            sunoc = sun

        mon = branch_hours["days"]["Monday"]
        if isinstance(mon, list):
            monoc = mon[0]["open"] + sep + mon[0]["close"]
        else:
            monoc = mon

        tue = branch_hours["days"]["Tuesday"]
        if isinstance(tue, list):
            tueoc = tue[0]["open"] + sep + tue[0]["close"]
        else:
            tueoc = tue

        wed = branch_hours["days"]["Wednesday"]
        if isinstance(wed, list):
            wedoc = wed[0]["open"] + sep + wed[0]["close"]
        else:
            wedoc = wed

        thu = branch_hours["days"]["Thursday"]
        if isinstance(thu, list):
            thuoc = thu[0]["open"] + sep + thu[0]["close"]
        else:
            thuoc = thu

        branch_hoo = "Monday {}; Tuesday {}; Wednesday {}; Thursday {}; Friday {}; Saturday {}; Sunday {}"
        branch_hoo = branch_hoo.format(
            monoc,
            tueoc,
            wedoc,
            thuoc,
            frioc,
            satoc,
            sunoc,
        )
        return branch_hoo
    else:
        return atm_hrs["atm_hours"]


def get_branch_atm_hrs_and_loctype(data):
    maplist = data["maplist"]
    maplist1 = maplist.split('<div class="tlsmap_list">')[-1]
    maplist2 = maplist1.split(",</div>")[0]
    maplist3 = (
        maplist2.replace("\\n", "")
        .replace("\\r", "")
        .replace("\\", "")
        .strip()
        .lstrip()
        .rstrip()
        .replace("\\u0022", "")
    )
    hours_phone_loctype = maplist3.split('"hours_sets:primary":')
    logger.info(f"number of items: {len(hours_phone_loctype)}")
    branch_atm_hrs_and_loctype = []
    for idx, hours_sets_primary in enumerate(hours_phone_loctype[1:]):
        branch_hours = (
            hours_sets_primary.split('"hours_sets:drive_up_hours": "')[0]
            .strip()
            .rstrip(",")
            .rstrip('"')
            .lstrip('"')
        )
        branch_hours_json = json.loads(branch_hours)
        fcs1 = hours_sets_primary.split('"financial_center_services":')[1]
        fcs2 = '{"financial_center_services":' + fcs1
        spobj1 = fcs2.split('"specialties_object":')[0]
        spobj2 = spobj1.strip().rstrip(",") + "}"
        atm_hours_json = json.loads(spobj2)
        branch_atm_hrs = get_branch_atm_hoo(branch_hours_json, atm_hours_json)
        location_type_branch_atm = atm_hours_json["location_type"]
        branch_atm_hrs_and_loctype.append((branch_atm_hrs, location_type_branch_atm))
    return branch_atm_hrs_and_loctype


def fetch_data():
    # If Radius  is greater than 1000 it does not work, meaning the URL does not work
    # We must keep the radius at 1000 or less than 1000 miles
    # 'level' must be equal to 1000 or less than 1000
    start_url = "https://maps.bankofamerica.com/api/getAsyncLocations?template=search&radius=1000&limit=1000&level=search&search="
    s = set()
    for idx, zipcode in enumerate(zips):
        url = f"{start_url}{zipcode}"
        logger.info(f"Pulling the data from at: {idx} | {zipcode}| {url} ")
        data = session.get(url, headers=headers_authority_simple).json()
        data_markers = data["markers"]

        # Phone Number
        plist = get_phone(data)

        # Branch, Office and ATM Hours of Operations and location type
        branch_office_atm_hrs_and_loctype = get_branch_atm_hrs_and_loctype(data)
        if data_markers:
            logger.info(f"Number of stores found: {len(data_markers)}")
            for idx1, markers in enumerate(data_markers):
                info_raw = markers["info"]
                info_raw1 = info_raw.replace('<div class="tlsmap_popup">', "").replace(
                    "</div>", ""
                )
                info_json = json.loads(info_raw1)

                locator_domain = DOMAIN
                page_url = info_json["url"]
                if info_json["address_1"]:
                    street_address = info_json["address_1"]
                    if info_json["address_2"]:
                        street_address = street_address + ", " + info_json["address_2"]
                    else:
                        street_address = street_address
                else:
                    street_address = MISSING
                location_name = info_json["location_name"]
                location_name = location_name if location_name else MISSING
                city = info_json["city"]
                city = city if city else MISSING
                state = info_json["region"]
                state = state if state else MISSING
                zip_postal = info_json["post_code"]
                zip_postal = zip_postal if zip_postal else MISSING
                country_code = "US"
                store_number = info_json["lid"]
                store_number = store_number if store_number else MISSING
                # Making sure there is no duplicates
                if store_number in s:
                    continue
                s.add(store_number)

                # Phone Number
                phone = plist[idx1]
                location_type = branch_office_atm_hrs_and_loctype[idx1][1]
                location_type = location_type if location_type else MISSING
                latitude = info_json["lat"]
                latitude = latitude if latitude else MISSING
                longitude = info_json["lng"]
                longitude = longitude if longitude else MISSING

                # Hours of operation
                hours_of_operation = branch_office_atm_hrs_and_loctype[idx1][0]
                if "Limited" in hours_of_operation:
                    hours_of_operation = "<MISSING>"
                raw_address = "<MISSING>"

                yield SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_address,
                )


def scrape():
    logger.info(" Scraping Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
