import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "jimmysegg_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.jimmysegg.com"
MISSING = SgRecord.MISSING


def get_data(temp):
    location_name = temp[0]
    log.info(location_name)
    if "Monday" in temp[-2] or "May & Hefner" in location_name:
        raw_address = " ".join(temp[1:-3])
        hours_of_operation = temp[-2] + " " + temp[-1]
        phone = temp[-3]
    else:
        raw_address = " ".join(temp[1:-2])
        hours_of_operation = temp[-1]
        phone = temp[-2]
    if "MENU" in raw_address:
        raw_address.split("MENU")[0]
    address = raw_address.replace(",", " ")
    address = usaddress.parse(address)
    i = 0
    street_address = ""
    city = ""
    state = ""
    zip_postal = ""
    while i < len(address):
        temp = address[i]
        if (
            temp[1].find("Address") != -1
            or temp[1].find("Street") != -1
            or temp[1].find("Recipient") != -1
            or temp[1].find("Occupancy") != -1
            or temp[1].find("BuildingName") != -1
            or temp[1].find("USPSBoxType") != -1
            or temp[1].find("USPSBoxID") != -1
        ):
            street_address = street_address + " " + temp[0]
        if temp[1].find("PlaceName") != -1:
            city = city + " " + temp[0]
        if temp[1].find("StateName") != -1:
            state = state + " " + temp[0]
        if temp[1].find("ZipCode") != -1:
            zip_postal = zip_postal + " " + temp[0]
        i += 1
    state = state.replace("Location", "")
    if "Falls" in state:
        state = location_name.split(",")[1]
    country_code = "US"
    return (
        location_name,
        raw_address,
        street_address,
        city,
        state,
        zip_postal,
        country_code,
        phone,
        hours_of_operation,
    )


def fetch_data():
    if True:
        url = "https://www.jimmysegg.com/online-ordering/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "wolf-row-inner"})[-1]
        loclist = str(loclist).split("ORDER")[:-1]
        for loc in loclist:
            temp_var_1 = (
                BeautifulSoup(loc, "html.parser")
                .get_text(separator="|", strip=True)
                .split("|")
            )
            if "PICKUP OR DELIVERY" in temp_var_1[0] or "NOW" in temp_var_1[0]:
                del temp_var_1[0]
            if "MENU" in temp_var_1[0]:
                del temp_var_1[0]
            if temp_var_1[0].isupper():
                del temp_var_1[0]
            if len(temp_var_1) > 10:
                loclist_2 = loc.split("MENU")
                for loc_2 in loclist_2:
                    temp_var_2 = (
                        BeautifulSoup(loc_2, "html.parser")
                        .get_text(separator="|", strip=True)
                        .split("|")
                    )
                    if (
                        "PICKUP OR DELIVERY" in temp_var_2[0]
                        or "JOIN THE WAITLIST" in temp_var_2[0]
                        or "POSTMATES" in temp_var_2[0]
                        or "GRUBHUB" in temp_var_2[0]
                    ):
                        del temp_var_2[0]
                    if not temp_var_2:
                        continue
                    (
                        location_name,
                        raw_address,
                        street_address,
                        city,
                        state,
                        zip_postal,
                        country_code,
                        phone,
                        hours_of_operation,
                    ) = get_data(temp_var_2)
                    yield SgRecord(
                        locator_domain=DOMAIN,
                        page_url=url,
                        location_name=location_name,
                        street_address=street_address.strip(),
                        city=city.strip(),
                        state=state.strip(),
                        zip_postal=zip_postal.strip(),
                        country_code=country_code,
                        store_number=MISSING,
                        phone=phone.strip(),
                        location_type=MISSING,
                        latitude=MISSING,
                        longitude=MISSING,
                        hours_of_operation=hours_of_operation,
                        raw_address=raw_address,
                    )
                continue
            (
                location_name,
                raw_address,
                street_address,
                city,
                state,
                zip_postal,
                country_code,
                phone,
                hours_of_operation,
            ) = get_data(temp_var_1)
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


def scrape():
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
