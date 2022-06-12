from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgpostal import parse_address_intl
from lxml import html
import json
import time
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("caffenero_com")
MISSING = "<MISSING>"

headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


# US and UK Store Locator URLs List

URL_US_UK_LOCATIONS = [
    "https://caffenero.com/uk/stores/",
    "https://caffenero.com/us/stores/",
]


def get_all_stores_data_for_us_uk():

    # This returns a list containing all the stores' data in the US and UK
    session = SgRequests()
    data_us_uk = []
    for countrynum, url_country in enumerate(URL_US_UK_LOCATIONS[0:]):
        r = session.get(url_country, headers=headers)
        time.sleep(30)
        tree = html.fromstring(r.text, "lxml")
        xpath_storesdata = '//script[@type="text/javascript"]/text()'
        data_raw = tree.xpath(xpath_storesdata)
        data_raw1 = "".join(data_raw)
        data_raw2 = data_raw1.split("storesData = ")[-1]
        data_raw3 = data_raw2.split(";")[0]
        data_json = json.loads(data_raw3)
        stores = data_json["stores"]
        logger.info(
            f"Number of stores count {countrynum} | {url_country}: {len(stores)}"
        )
        data_us_uk.extend(stores)
    return data_us_uk


data_list_us_uk = get_all_stores_data_for_us_uk()


def fetch_data_us_uk():

    # This crawls the data from the US and UK.
    session = SgRequests()
    s = set()
    for poinum, loc in enumerate(data_list_us_uk[0:]):
        locator_domain = ""
        location_name = loc["name"]
        store_address1 = loc["address"]
        store_address = (
            store_address1.replace("MA01890", "MA 01890")
            .replace("MA01742", "MA 01742")
            .replace("MA01890", "MA 01890")
        )

        pa = parse_address_intl(store_address)
        street_address = pa.street_address_1 or MISSING

        # Street addresses with only numbers updated followed by raw address
        if (
            street_address == "23"
            and store_address1
            == "Unit 210, 23 The Galleria, Meadowhall Shopping Centre, Sheffield, South Yorkshire, S9 1EP"
        ):
            street_address = street_address.replace(
                "23", "23 The Galleria, Meadowhall Shopping Centre"
            )
        if (
            street_address == "35"
            and store_address1
            == "35 Fairhill Shopping Centre, Ballymena, Antrim, BT43 6UF"
        ):
            street_address = street_address.replace("35", "35 Fairhill Shopping Centre")
        if (
            street_address == "18"
            and store_address1
            == "18  Wheelergate, Nottingham, Nottinghamshire, NG1 2NB"
        ):
            street_address = street_address.replace("18", "18 Wheelergate")
        if (
            street_address == "45"
            and store_address1 == "45 Whitechapel, Liverpool, Merseyside, L1 6DT"
        ):
            street_address = street_address.replace("45", "45 Whitechapel")

        city = pa.city or MISSING
        state = pa.state or MISSING
        if (
            state == "G2"
            and store_address1
            == "St Vincent Plaza, 319 St Vincent St, Glasgow, Glasgow City, G2 5LP"
        ):
            state = state.replace("G2", "<MISSING>")
        if (
            state == "L3"
            and store_address1
            == "c/o Blackwells, Crown Place, 200 Brownlow Hill, Liverpool, Merseyside, L3 5UE"
        ):
            state = state.replace("L3", "<MISSING>")
        if (
            state == "E20"
            and store_address1
            == "Westfield Stratford City, Monfichet Road, London, Greater London, E20 1EJ"
        ):
            state = state.replace("E20", "<MISSING>")

        # Country Code
        country_code = loc["country_code"]

        if country_code == "gb":
            try:
                zip_postal = store_address.split(",")[-1].lstrip().rstrip().strip()
            except:
                zip_postal = MISSING
        else:
            zip_postal = pa.postcode or MISSING

        country_code = country_code.upper() if country_code else MISSING

        # Locator Domain
        if country_code == "US":
            locator_domain = "caffenero.com" + "/" + country_code.lower()
        if country_code == "GB":
            locator_domain = "caffenero.com" + "/" + "uk"
        store_number = loc["store_id"] or MISSING
        location_type = MISSING
        latitude = loc["latitude"] or MISSING
        longitude = loc["longitude"] or MISSING
        page_url = "https://caffenero.com" + loc["permalink"]
        logger.info(f"Pulling data for {poinum}: {page_url}")

        # We need to crawl each store followed by corresponding page URL becuase
        # hours of operation and phone data are not available in store locator data
        r_loc = session.get(page_url, headers=headers, timeout=180)
        tree_loc = html.fromstring(r_loc.text, "lxml")
        phone = tree_loc.xpath('//td/a[contains(@href, "tel")]/text()')
        phone = "".join(phone)
        phone = phone if phone else MISSING
        hoo_raw = tree_loc.xpath('//div[@class="timings-info"]//text()')
        hoo_raw = [" ".join(i.split()) for i in hoo_raw]
        hoo_raw = [i for i in hoo_raw if i]
        hoo_raw = (
            " ".join(hoo_raw)
            .replace(
                " Open for takeaway. Dining in is dependent on local tier restrictions. Please check with the store.",
                "",
            )
            .replace("Opening Hours", "")
        )
        hoo_raw = (
            hoo_raw.replace(" Tuesday", ", Tuesday")
            .replace(" Wednesday", ", Wednesday")
            .replace(" Thursday", ", Thursday")
            .replace(" Friday", ", Friday")
            .replace(" Saturday", ", Saturday")
            .replace(" Sunday", ", Sunday")
            .lstrip()
        )
        if hoo_raw:
            if "TEMPORARILY CLOSED" in hoo_raw:
                hours_of_operation = "Templorarily Closed"
            else:
                hours_of_operation = hoo_raw
        else:
            hours_of_operation = MISSING

        raw_address = store_address1 if store_address1 else MISSING
        if store_number in s:
            continue
        s.add(store_number)
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


# Outside of US and UK Countries Store Locator List
URL_OUTSIDE_OF_US_UK_LOCATIONS = [
    "https://caffenero.com/cy/stores/",
    "https://caffenero.com/ie/stores/",
    "https://greencaffenero.pl/en/stores/",
    "https://caffenero.com/ae/stores/",
    "https://caffenero.com/tr/en/stores/",
    "https://caffenero.com/se/sv/stores/",
]


def get_all_stores_data_outside_of_us_uk():
    # This returns a list containing all the stores' data for AE,
    # CY, IE, PL, TR and SE
    session = SgRequests()
    data_outside_of_us_uk = []
    for countrynum, url_country in enumerate(URL_OUTSIDE_OF_US_UK_LOCATIONS[0:]):
        r = session.get(url_country, headers=headers)
        time.sleep(30)
        tree = html.fromstring(r.text, "lxml")
        xpath_storesdata = '//script[@type="text/javascript"]/text()'
        data_raw = tree.xpath(xpath_storesdata)
        data_raw1 = "".join(data_raw)
        data_raw2 = data_raw1.split("storesData = ")[-1]
        data_raw3 = data_raw2.split(";")[0]
        data_json = json.loads(data_raw3)
        stores = data_json["stores"]
        logger.info(
            f"Number of stores count for {countrynum} | {url_country}: {len(stores)}"
        )
        data_outside_of_us_uk.extend(stores)
    return data_outside_of_us_uk


data_list_outside_us_uk = get_all_stores_data_outside_of_us_uk()


def fetch_data_outside_of_us_uk():

    # This scrapes the data from the countries such as ( United Arab Emirates, Cyprus,
    # Ireland, Poland, Turkey, and Sweden )

    session = SgRequests()
    s = set()
    for poinum, loc in enumerate(data_list_outside_us_uk[0:]):
        location_name = loc["name"]
        store_address1 = loc["address"]
        store_address1 = store_address1.strip()
        store_address = (
            store_address1.replace("MA01890", "MA 01890")
            .replace("MA01742", "MA 01742")
            .replace("MA01890", "MA 01890")
        )

        pa = parse_address_intl(store_address)
        street_address = pa.street_address_1 or MISSING

        # If not replaced, parsed street addresses by sgpostal are found to be 20 and 45
        # So, both street addresses are updated

        if (
            street_address == "20"
            and store_address1
            == "20 Grigori Afxentiou and Charalambou Mou, ABC Business Center, Paphos,"
        ):
            street_address = street_address.replace(
                "20", "20 Grigori Afxentiou and Charalambou Mou"
            )
        if (
            street_address == "45"
            and store_address1
            == "45 Promaxon Eleftherias, Agios Athanasios, Limassol, 4103"
        ):
            street_address = street_address.replace("45", "45 Promaxon Eleftherias")

        city = pa.city or MISSING
        state = pa.state or MISSING
        country_code = loc["country_code"]
        if country_code == "gb":
            try:
                zip_postal = store_address.split(",")[-1].lstrip().rstrip().strip()
            except:
                zip_postal = MISSING
        else:
            zip_postal = pa.postcode or MISSING

        country_code = country_code.upper() if country_code else MISSING

        # Domain are set followed by country code
        # All other countries have sub-domain followed by their country
        if country_code == "US":
            locator_domain = "caffenero.com" + "/" + country_code.lower()
        if country_code == "GB":
            locator_domain = "caffenero.com" + "/" + "uk"
        if country_code == "AE":
            locator_domain = "caffenero.com" + "/" + country_code.lower()
        if country_code == "CY":
            locator_domain = "caffenero.com" + "/" + country_code.lower()
        if country_code == "IE":
            locator_domain = "caffenero.com" + "/" + country_code.lower()
        if country_code == "PL":
            locator_domain = "greencaffenero.pl" + "/" + country_code.lower()
        if country_code == "SE":
            locator_domain = "caffenero.com" + "/" + country_code.lower()
        if country_code == "TR":
            locator_domain = "caffenero.com" + "/" + country_code.lower()

        store_number = loc["store_id"] or MISSING
        location_type = MISSING
        latitude = loc["latitude"] or MISSING
        longitude = loc["longitude"] or MISSING

        # Parent domain is found to be caffenero.com for all countries
        # except Poland, that's why while forming page_url, caffenero.com is
        # replaced with greencaffenero.pl so that page_url works as expected
        page_url = "https://caffenero.com" + loc["permalink"]
        if country_code == "PL":
            page_url = page_url.replace(
                "https://caffenero.com", "https://greencaffenero.pl"
            )
        else:
            page_url = page_url

        logger.info(f"Pulling data for {poinum}: {page_url}")

        # We need to crawl each store followed by corresponding page URL becuase
        # hours of operation and phone data are not available in store locator data
        r_loc = session.get(page_url, headers=headers, timeout=180)
        tree_loc = html.fromstring(r_loc.text, "lxml")
        phone = tree_loc.xpath('//td/a[contains(@href, "tel")]/text()')
        phone = "".join(phone)
        phone = phone if phone else MISSING
        hoo_raw = tree_loc.xpath('//div[@class="timings-info"]//text()')
        hoo_raw = [" ".join(i.split()) for i in hoo_raw]
        hoo_raw = [i for i in hoo_raw if i]
        hoo_raw = (
            " ".join(hoo_raw)
            .replace(
                " Open for takeaway. Dining in is dependent on local tier restrictions. Please check with the store.",
                "",
            )
            .replace("Opening Hours", "")
        )
        hoo_raw = (
            hoo_raw.replace(" Tuesday", ", Tuesday")
            .replace(" Wednesday", ", Wednesday")
            .replace(" Thursday", ", Thursday")
            .replace(" Friday", ", Friday")
            .replace(" Saturday", ", Saturday")
            .replace(" Sunday", ", Sunday")
            .lstrip()
        )
        if hoo_raw:
            if "TEMPORARILY CLOSED" in hoo_raw:
                hours_of_operation = "Templorarily Closed"
            else:
                hours_of_operation = hoo_raw
        else:
            hours_of_operation = MISSING

        raw_address = store_address1 if store_address1 else MISSING
        if store_number in s:
            continue
        s.add(store_number)
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
    logger.info("Started")
    count = 0
    with SgWriter() as writer:
        results_us_uk = list(fetch_data_us_uk())
        results_outside_us_uk = list(fetch_data_outside_of_us_uk())
        results_us_uk.extend(results_outside_us_uk)
        for rec in results_us_uk:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
