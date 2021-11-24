from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgrequests import SgRequests
from lxml import html
import re
import ssl


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

MISSING = SgRecord.MISSING
DOMAIN = "marksandspencer.com/ae"
LOCATION_URL_AE = "https://www.marksandspencer.com/ae/stores"
logger = SgLogSetup().get_logger("marksandspencer_com__ae")

headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}


def get_api_endpoint_url_for_all_countries():
    with SgRequests() as s_country:
        r_country = s_country.get(LOCATION_URL_AE, headers=headers)
        sel_country = html.fromstring(r_country.text, "lxml")
        sl_xpath = '//select[option[contains(text(), "Select Country")]]/option/@value'
        country_list = sel_country.xpath(sl_xpath)
        country_list = [i for i in country_list if "0" not in i]
        api_endpoint_url_list = []
        for country_name in country_list:
            api_endpoint_url = f"https://www.marksandspencer.com/on/demandware.store/Sites-mandslondon-Site/en_EN/Stores-FindStores?showMap=true&selectedStoreCountry={country_name}"
            api_endpoint_url_list.append(api_endpoint_url)
    return api_endpoint_url_list


def fetch_data():
    API_ENDPOINT_URL_LIST = get_api_endpoint_url_for_all_countries()
    with SgRequests() as session:
        for cnum, url in enumerate(API_ENDPOINT_URL_LIST[0:]):
            logger.info(f"[{cnum}] Pulling the data from: {url}")
            data_per_country = session.get(url, headers=headers).json()
            country_name = url.split("=")[-1]
            for itemnum, d in enumerate(data_per_country["stores"]):
                locator_domain = "marksandspencer.com"
                page_url = url
                location_name = d["name"]
                location_name = location_name if location_name else MISSING
                logger.info(
                    f"[{country_name}][{itemnum}] Location Name: {location_name}"
                )

                # Action Item # 1: create a somewhat “custom” location name -
                # which we’ll then pass through to production.
                # Append "M&S" to the front of the location_names -
                # [if "M&S" or "Mark & Spencer" are not already included].
                # if the name contains TEMPORARY CLOSED, -
                # truncate this portion (since we don’t want the name to change when it’s no longer temporarily closed).

                if "<MISSING>" not in location_name:
                    if (
                        "M&S".lower() in location_name.lower()
                        or "Mark & Spencer".lower() in location_name.lower()
                    ):
                        location_name = location_name
                    else:
                        location_name = "M&S " + location_name

                location_name = location_name.replace("TEMPORARY CLOSED", "").replace(
                    "Temporary Closed", ""
                )
                location_name = location_name.replace(" - Temporarily Closed", "")

                # There may be some location_names that say SIMPLY FOO or SIMPLY F (it’s like this on the site).
                # This creates two patterns or rules to find "SIMPLY FOO" or "SIMPLY F" replaced
                # with "SIMPLY FOOD".

                pattern1_simply_foo = r"\bSIMPLY\sFOO\b"
                simply_foo_found = re.findall(pattern1_simply_foo, location_name)
                if simply_foo_found:
                    location_name = location_name.replace("SIMPLY FOO", "SIMPLY FOOD")
                else:
                    location_name = location_name

                pattern2_simply_f = r"\bSIMPLY\sF\b"
                simply_f_found = re.findall(pattern2_simply_f, location_name)
                if simply_f_found:
                    location_name = location_name.replace("SIMPLY F", "SIMPLY FOOD")
                else:
                    location_name = location_name
                street_address = ""
                address1 = d["address1"].rstrip(",").strip()
                address2 = d["address2"]
                if address1 and address2:
                    street_address = address1 + ", " + address2
                elif address1 and not address2:
                    street_address = address1
                elif not address1 and not address2:
                    street_address = MISSING
                else:
                    street_address = MISSING
                street_address = street_address.rstrip(",")
                logger.info(
                    f"[{country_name}][{itemnum}] Street Address: {street_address}"
                )

                city = d["city"]
                city = city if city else MISSING
                try:
                    state = d["stateCode"]
                except KeyError:
                    state = MISSING

                zip_postal = d["postalCode"]
                zip_postal = zip_postal if zip_postal else MISSING

                country_code = d["countryCode"]
                country_code = country_code if country_code else MISSING

                store_number = d["ID"]
                store_number = store_number if store_number else MISSING
                phone = ""
                if "phone" in d:
                    p = d["phone"].strip()
                    p = " ".join(p.split())
                    p1 = p.split("/")[0].strip()
                    phone = p1.split(",")[0].strip()

                else:
                    phone = MISSING

                location_type = MISSING
                location_type = location_type if location_type else MISSING

                latitude = d["latitude"]
                latitude = latitude if latitude else MISSING

                longitude = d["longitude"]
                longitude = longitude if longitude else MISSING
                hours_of_operation = ""
                try:

                    if "storeHours" in d:
                        hoo = d["storeHours"]
                        sel_hoo = html.fromstring(hoo, "lxml")
                        mon = sel_hoo.xpath(
                            '//span[contains(@class, "store-open-hours store-monday")]/text()'
                        )
                        tue = sel_hoo.xpath(
                            '//span[contains(@class, "store-open-hours store-tuesday")]/text()'
                        )
                        wed = sel_hoo.xpath(
                            '//span[contains(@class, "store-open-hours store-wednesday")]/text()'
                        )
                        thu = sel_hoo.xpath(
                            '//span[contains(@class, "store-open-hours store-thursday")]/text()'
                        )
                        fri = sel_hoo.xpath(
                            '//span[contains(@class, "store-open-hours store-friday")]/text()'
                        )
                        sat = sel_hoo.xpath(
                            '//span[contains(@class, "store-open-hours store-saturday")]/text()'
                        )
                        sun = sel_hoo.xpath(
                            '//span[contains(@class, "store-open-hours store-sunday")]/text()'
                        )
                        week_days = [
                            ("Mon", mon),
                            ("Tue", tue),
                            ("Wed", wed),
                            ("Thu", thu),
                            ("Fri", fri),
                            ("Sat", sat),
                            ("Sun", sun),
                        ]
                        week_days_list = []
                        for dnum, i in enumerate(week_days):
                            j = i[0] + " " + "".join(i[1]).strip()
                            week_days_list.append(j)
                        week_days_list = "; ".join(week_days_list)
                        hours_of_operation = week_days_list
                    else:
                        hours_of_operation = MISSING
                except:
                    hours_of_operation = MISSING
                raw_address = SgRecord.MISSING
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
