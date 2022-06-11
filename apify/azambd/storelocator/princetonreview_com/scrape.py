from lxml import html
import time

from sgpostal.sgpostal import parse_address_intl
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

website = "https://www.princetonreview.com"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(url):
    return session.get(url, headers=headers)


def fix_string(str_list):
    values = []
    for string in str_list:
        string = string.replace("\r", " ").replace("\t", " ").replace("\n", " ").strip()
        string = " ".join(string.split())
        if len(string) > 0:
            values.append(string)
    if len(values) == 0:
        return MISSING
    return " ".join(values)


def get_address(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode

            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"Address is missing, {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def get_country_code(head):
    codes = fix_string(
        head.xpath(".//text()")
        + head.xpath(".//p/text()")
        + head.xpath(".//span/text()")
    )
    c_name = codes.split("(")[0].strip()
    code = c_name.upper()
    stateName = codes.replace(c_name, "").replace("(", "").replace(")", "").strip()

    if "U . A . E ." in code:
        return code.replace(" ", "").replace(".", ""), c_name, stateName
    elif "AZERBAIJAN" in code:
        return "AZERBAIJAN", c_name, stateName

    return code, c_name, stateName


def stringify_children(nodes):
    values = []
    for node in nodes:
        values.append(" ".join(node.itertext()))
    if len(values) == 0:
        return MISSING
    return " ".join(values)


def fetch_stores():
    stores = []
    response = request_with_retries(f"{website}/locations")
    body = html.fromstring(response.text, "lxml")
    cities = body.xpath(
        '//a[contains(@class, "list-group-item") and not(contains(@class, "no-location"))]/@href'
    )
    log.debug(f"total cities {len(cities)}")

    storeUrls = []
    for cityUrl in cities:
        response = request_with_retries(f"{website}{cityUrl}")
        body = html.fromstring(response.text, "lxml")
        storeUrls = storeUrls + body.xpath('//a[contains(@class, "explore btn")]/@href')

    log.debug(f"total storeUrls {len(storeUrls)}")

    for page_url in storeUrls:
        page_url = f"{website}{page_url.strip()}"

        response = request_with_retries(page_url)
        body = html.fromstring(response.text, "lxml")
        location_name = body.xpath("//h1/text()")[0]
        mainDiv = body.xpath('//div[contains(@class, "row location")]')[0]
        address = fix_string(
            mainDiv.xpath(".//address/a[contains(@href, 'google')]/text()")
        )
        phone = (
            fix_string(mainDiv.xpath(".//address/text()"))
            .replace("The Princeton Review", "")
            .strip()
        )
        hoo = fix_string(mainDiv.xpath(".//address/p/text()"))
        country_code = "US"

        if "/ca/" in page_url:
            country_code = "CA"
        elif "/puerto-rico/" in page_url:
            country_code = "PR"

        stores.append(
            {
                "location_name": location_name,
                "page_url": page_url,
                "country_code": country_code,
                "phone": phone,
                "raw_address": address,
                "hoo": hoo,
            }
        )

    page_url = f"{website}/international/locations"
    response = request_with_retries(page_url)
    body = html.fromstring(response.text, "lxml")
    trs = body.xpath("//tr[@itemprop='Organization']")

    intl_countries = 0
    intl_stores = 0

    # special case raja garden
    rajaGarden = True
    for tr in trs:
        intl_countries = intl_countries + 1
        country_code, c_name, state_name = get_country_code(tr.xpath(".//th")[0])

        subOrg = tr.xpath(".//div[@itemprop='subOrganization']")
        if len(subOrg) == 0:
            countryTrs = [tr]
        else:
            countryTrs = subOrg

        for countryTr in countryTrs:
            location_name = fix_string([stringify_children(countryTr.xpath(".//h3"))])
            full_address = fix_string(
                [stringify_children(countryTr.xpath(".//address"))]
            )

            phonePaths = countryTr.xpath(".//*[@itemprop='telephone']")

            if len(phonePaths) > 1:
                phonePaths = [phonePaths[0]]
            phone = fix_string([stringify_children(phonePaths)])

            address = (
                full_address.replace("Opening Soon in ", "").replace("!", "").strip()
            )

            if phone == MISSING and "Tel:" in address:
                phone = address.split("Tel:")[1].strip().split()[0]
                address = address.split("Tel:")[0].strip()

            if "Opening Soon in" not in full_address and location_name == MISSING:
                parts = full_address.split(" " + c_name + " ")
                if len(parts) > 1:
                    location_name = parts[0].strip()
                    address = address.replace(
                        location_name + " " + c_name + " ", ""
                    ).strip()

                elif len(state_name) > 0:
                    parts = full_address.split(" " + state_name)
                    if len(parts) > 1 and (len(parts[0]) < len(parts[1])):
                        location_name = parts[0].strip()
                        address = address.replace(
                            location_name + " " + state_name, ""
                        ).strip()
                if location_name[len(location_name) - 1] == ",":
                    location_name = location_name[:-1]

            if (
                len(stores) > 0
                and "Raja Garden" in stores[len(stores) - 1]["location_name"]
                and rajaGarden
            ):
                stores[len(stores) - 1]["phone"] = phone
                stores[len(stores) - 1]["raw_address"] = address
                rajaGarden = False
                continue

            if address == MISSING and "Raja Garden" not in location_name:
                address_part = countryTr.xpath(
                    ".//span[@itemprop='postalCode']"
                ) + countryTr.xpath(".//span[@class='workaround-p']")
                if len(address_part) == 0:
                    address_part = [countryTr.xpath(".//p")[0]]
                address = fix_string([stringify_children(address_part)])

            if len(countryTr.xpath(".//address")) > 1:
                location_name = fix_string(
                    [stringify_children([countryTr.xpath(".//h3")[0]])]
                )
                address = fix_string(
                    [stringify_children([countryTr.xpath(".//address")[0]])]
                )
                phone = fix_string(
                    [
                        stringify_children(
                            [countryTr.xpath(".//*[@itemprop='telephone']")[0]]
                        )
                    ]
                )
                intl_stores = intl_stores + 1
                stores.append(
                    {
                        "location_name": location_name,
                        "page_url": page_url,
                        "country_code": country_code,
                        "phone": phone,
                        "raw_address": address,
                        "hoo": MISSING,
                    }
                )

                location_name = fix_string(
                    [stringify_children([countryTr.xpath(".//h3")[1]])]
                )
                address = fix_string(
                    [stringify_children([countryTr.xpath(".//address")[1]])]
                )
                phone = fix_string(
                    [
                        stringify_children(
                            [countryTr.xpath(".//*[@itemprop='telephone']")[1]]
                        )
                    ]
                )
                intl_stores = intl_stores + 1
                stores.append(
                    {
                        "location_name": location_name,
                        "page_url": page_url,
                        "country_code": country_code,
                        "phone": phone,
                        "raw_address": address,
                        "hoo": MISSING,
                    }
                )

            else:
                intl_stores = intl_stores + 1
                stores.append(
                    {
                        "location_name": location_name,
                        "page_url": page_url,
                        "country_code": country_code,
                        "phone": phone,
                        "raw_address": address,
                        "hoo": MISSING,
                    }
                )

    log.debug(
        f"From {intl_countries} international countries, total stores {intl_stores}"
    )
    return stores


def fetch_data():
    stores = fetch_stores()
    log.info(f"Total stores = {len(stores)}")
    for store in stores:
        store_number = MISSING
        location_type = MISSING
        latitude = MISSING
        longitude = MISSING

        page_url = store["page_url"]
        location_name = store["location_name"]
        raw_address = store["raw_address"]
        street_address, city, state, zip_postal = get_address(raw_address)
        if street_address is MISSING:
            continue
        country_code = store["country_code"]
        phone = store["phone"]
        hours_of_operation = store["hoo"]

        yield SgRecord(
            locator_domain=website,
            store_number=store_number,
            page_url=page_url,
            location_name=location_name,
            location_type=location_type,
            street_address=street_address,
            city=city,
            zip_postal=zip_postal,
            state=state,
            country_code=country_code,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    result = fetch_data()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
