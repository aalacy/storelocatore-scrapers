from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt
import tenacity
from lxml import html


logger = SgLogSetup().get_logger("mercedes-benz_co_uk")
DOMAIN = "mercedes-benz.co.uk"
LOCATION_DEALER_URL = "https://www.mercedes-amg.com/en/vehicles/dealer.html"
COUNTRY_LOCATION_URL = "https://www.mercedes-amg.com/en/vehicles/dealer.html"
MISSING = SgRecord.MISSING
MAX_WORKERS = 10
headers_int = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}

headers_dealer_locator = {
    "Referer": "https://www.mercedes-amg.com/",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response(urlnum, url, headers_):
    with SgRequests(timeout_config=300) as http:
        logger.info(f"[{urlnum}] Pulling the data from: {url}")
        r = http.get(url, headers=headers_)
        if r.status_code == 200:
            logger.info(f"HTTP Status Code: {r.status_code}")
            return r
        raise Exception(f"{urlnum} : {url} >> Temporary Error: {r.status_code}")


def get_api_key():
    r_js = get_response(0, LOCATION_DEALER_URL, headers_dealer_locator)
    xpath_2 = '//section[contains(@class,"amg-component amg-m-dealer-locator")]/@data-amg-props-apikey'
    sel_apikey = html.fromstring(r_js.text, "lxml")
    raw_plugin_dlc_file_url = sel_apikey.xpath(xpath_2)
    apikey = "".join(raw_plugin_dlc_file_url)
    try:
        if apikey:
            return apikey
    except Exception as e:
        logger.rinfo(f"Fix this issue {e}")


def get_api_based_headers():
    headers_with_apikey = {}
    apikey = get_api_key()
    headers_with_apikey["x-apikey"] = apikey
    headers_with_apikey[
        "User-agent"
    ] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
    headers_with_apikey["Referer"] = "https://www.mercedes-amg.com/"
    logger.info(f"APIKEY based headers: {headers_with_apikey}")
    return headers_with_apikey


def determine_brand(k):
    brands = []
    for i in k["brands"]:
        brands.append(
            str(i["brand"]["name"]) + str("(" + str(i["brand"]["code"]) + ")")
        )
    logger.info("Brands: %s" % brands)
    return ", ".join(brands)


def determine_hours(k, brand, which):
    hours = SgRecord.MISSING
    h = []
    if which != "LITERALLYANYTHING" and which != "SUPERLITERALLYANYTHING":
        try:
            for i in k["functions"]:
                if (
                    i["brandCode"] == brand
                    and i["activityCode"] == which
                    and len(h) == 0
                ):
                    try:
                        for j in list(i["openingHours"]):
                            if i["openingHours"][j]["open"]:
                                h.append(
                                    str(j)
                                    + ": "
                                    + str(
                                        i["openingHours"][j]["timePeriods"][0]["from"]
                                    )
                                    + "-"
                                    + str(i["openingHours"][j]["timePeriods"][0]["to"])
                                )
                            else:
                                h.append(str(j) + ": Closed")
                    except Exception:
                        continue
            if len(h) == 0:
                hours = determine_hours(k, brand, "LITERALLYANYTHING")
            else:
                return "; ".join(h)
        except Exception:
            return hours

    if which == "LITERALLYANYTHING":
        for i in k["functions"]:
            if i["brandCode"] == brand and len(h) == 0:
                try:
                    for j in list(i["openingHours"]):
                        if i["openingHours"][j]["open"]:
                            h.append(
                                str(j)
                                + ": "
                                + str(i["openingHours"][j]["timePeriods"][0]["from"])
                                + "-"
                                + str(i["openingHours"][j]["timePeriods"][0]["to"])
                            )
                        else:
                            h.append(str(j) + ": Closed")
                except Exception:
                    continue
        if len(h) == 0:
            hours = determine_hours(k, brand, "SUPERLITERALLYANYTHING")
        else:
            return "; ".join(h)

    if which == "SUPERLITERALLYANYTHING":
        for i in k["functions"]:
            if hours == SgRecord.MISSING and len(h) == 0:
                try:
                    for j in list(i["openingHours"]):
                        if i["openingHours"][j]["open"]:
                            h.append(
                                str(j)
                                + ": "
                                + str(i["openingHours"][j]["timePeriods"][0]["from"])
                                + "-"
                                + str(i["openingHours"][j]["timePeriods"][0]["to"])
                            )
                        else:
                            h.append(str(j) + ": Closed")
                except Exception:
                    continue
        if len(h) == 0:
            return hours
        else:
            return "; ".join(h)

    return hours


def fix_comma(x):
    h = []
    try:
        x = x.split(",")
        for i in x:
            st = i.strip()
            if len(st) >= 1:
                h.append(st)
        h = ", ".join(h)
    except Exception:
        h = x

    return h


def get_country_code_list():
    try:
        r = SgRequests().get("https://www.mercedes-amg.com/en/vehicles/dealer.html")
        sel_cl = html.fromstring(r.text, "lxml")
        locales_xpath = '//section[contains(@class, "amg-component amg-m-dealer-locator")]/@data-amg-props-locales'
        language_country_wise = sel_cl.xpath(locales_xpath)
        en_country_list = []
        for i in language_country_wise[0].split(","):
            j = "".join(i.split()).replace('"', "").replace('"', "")
            en_country_list.append(j)
        en_country_list = [i.replace("[", "").replace("]", "") for i in en_country_list]
        en_country_list_1 = [i.split("_")[-1] for i in en_country_list]
        en_country_list_1_deduped = list(set(en_country_list_1))
        en_country_list_1_deduped_sorted = sorted(en_country_list_1_deduped)

        return en_country_list_1_deduped_sorted
    except Exception as e:
        logger.info(f"Please fix {e} regarding getting country list")


def fetch_records(idx, store_url_tuple, headers_apikey, sgw: SgWriter):
    api_endpoint_url = store_url_tuple[0]
    try:
        r_data_per_dealer = get_response(idx, api_endpoint_url, headers_apikey)
        logger.info(f"[{idx}] Pulling the data from {api_endpoint_url}")
        data_per_dealer_json = r_data_per_dealer.json()
        for d in data_per_dealer_json["results"]:
            location_name = ""
            try:
                if "brands" in d:
                    brands = d["brands"]
                    for b in brands:
                        if "businessName" in b:
                            location_name = b["businessName"]
                        else:
                            location_name = d["baseInfo"]["name1"]
                else:
                    location_name = d["baseInfo"]["name1"]
            except:
                location_name = MISSING

            sa = d["address"]
            if "line1" in sa:
                l1 = sa["line1"]
            else:
                l1 = ""
            if "line2" in sa:
                l2 = sa["line2"]
            else:
                l2 = ""
            l = l1 + ", " + l2
            l = fix_comma(l)
            street_address = l or MISSING
            city = d["address"]["city"] or MISSING

            # State
            state = None
            state1 = None
            state2 = None
            if "region" in d["address"]["region"]:
                state1 = d["address"]["region"]["region"]
            else:
                state1 = ""

            if "subRegion" in d["address"]["region"]:
                state2 = d["address"]["region"]["subRegion"]
            else:
                state2 = ""

            if state1:
                state = state1
            else:
                if state2:
                    state = state2
                else:
                    state = MISSING

            # Country Code
            country_code = d["address"]["country"] or MISSING
            zipcode = d["address"]["zipcode"] or MISSING
            if MISSING not in country_code:
                if "US" in country_code and MISSING not in zipcode:
                    state = zipcode.split(" ")[0].strip()
                    zipcode = zipcode.split(" ")[1].strip()

            store_number = d["baseInfo"]["externalId"] or MISSING

            page_url = (
                f"https://www.smart.mercedes-benz.com/gb/en/dealer/{str(store_number)}"
            )
            if "phone" in d["contact"]:
                phone = d["contact"]["phone"]
                if phone:
                    if "+44" == phone:
                        phone = MISSING
                    else:
                        phone = phone
                else:
                    phone = MISSING
            else:
                phone = MISSING

            if "brands" in d:
                location_type = determine_brand(d)
            else:
                location_type = MISSING
            if "latitude" in d["address"]:
                latitude = d["address"]["latitude"]
            else:
                latitude = MISSING

            if "longitude" in d["address"]:
                longitude = d["address"]["longitude"]
            else:
                longitude = MISSING

            hours_of_operation = determine_hours(d, "SMT", "SALES")
            if "CLOSED" in location_name:
                location_name = location_name.replace("CLOSED", "").strip()
                hours_of_operation = "Closed"
            if (
                "WEDNESDAY: Closed; MONDAY: Closed; THURSDAY: Closed; SUNDAY: Closed; TUESDAY: Closed; FRIDAY: Closed; SATURDAY: Closed"
                in hours_of_operation
            ):
                hours_of_operation = MISSING

            logger.info(f"Locname: {location_name}")
            raw_address = MISSING

            item = SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipcode,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )
            sgw.write_row(item)
    except Exception as e:
        logger.info(f"Please fix FetchRecordsError: << {e} >> | {api_endpoint_url}")


def get_api_endpoint_url_based_on_dealer(headers_ak):
    all_countries = get_country_code_list()
    api_endpoint_url_list = []
    for idx, cc in enumerate(all_countries[0:]):
        if "GB" in cc:
            logger.info(f"Pulling the data for {cc}")
            api_results_list_url = f"https://api.corpinter.net/dlc/dms/v2/dealers/search?marketCode={cc}&fields="
            logger.info("")
            r1 = get_response(idx, api_results_list_url, headers_ak)
            results = r1.json()
            for i in results["results"]:
                company_id = i["baseInfo"]["externalId"]
                api_endpoint_url = f"https://api.corpinter.net/dlc/dms/v2/dealers/search?marketCode={cc}&fields=*&whiteList={company_id}"
                api_endpoint_url_list.append((api_endpoint_url, cc))
    return api_endpoint_url_list


def fetch_data(sgw: SgWriter):
    headers_with_apikey = get_api_based_headers()
    api_endpoint_urls = get_api_endpoint_url_based_on_dealer(headers_with_apikey)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_gb = [
            executor.submit(fetch_records, idx, api_url, headers_with_apikey, sgw)
            for idx, api_url in enumerate(api_endpoint_urls[0:])
        ]
        tasks.extend(task_gb)
        for future in as_completed(tasks):
            future.result()


def scrape():
    logger.info("Started")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
