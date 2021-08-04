from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from lxml import html
import re


logger = SgLogSetup().get_logger("smart_com__gb__en")

headers_dealer_locator = {
    "Referer": "https://www.mercedes-benz.co.uk/",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}

LOCATION_DEALER_URL = "https://www.mercedes-benz.co.uk/passengercars/mercedes-benz-cars/dealer-locator.html"


def get_api_key():
    session_js = SgRequests()
    r_js = session_js.get(LOCATION_DEALER_URL, headers=headers_dealer_locator)
    xpath_2 = '//iframe[@data-nn-pluginid="dlc"]/@data-nn-config-url'
    sel_apikey = html.fromstring(r_js.text, "lxml")
    raw_plugin_dlc_file_url = sel_apikey.xpath(xpath_2)
    logger.info(f"Plugin DLC File Name: {raw_plugin_dlc_file_url}")
    raw_plugin_dlc_file_url = "".join(raw_plugin_dlc_file_url)

    dealerlocator_payload_pluginJSUrl = session_js.get(raw_plugin_dlc_file_url).json()[
        "pluginJSUrl"
    ]
    response_pjsurl = session_js.get(dealerlocator_payload_pluginJSUrl)
    apikey_pjsurl = re.findall(r"apiKey:(.*)whiteList", response_pjsurl.text)
    apikey = "".join(apikey_pjsurl).split('"')[1]
    if apikey:
        return apikey
    else:
        raise Exception("Please check the dlc plugin URL to make sure it exists!!")


apikey = get_api_key()
headers_with_apikey = {}
headers_with_apikey["x-apikey"] = apikey
headers_with_apikey[
    "User-agent"
] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
headers_with_apikey["Referer"] = "https://www.mercedes-benz.co.uk/"

logger.info(f"APIKEY based headers: {headers_with_apikey}")


def determine_brand(k):
    brands = []
    for i in k["brands"]:
        brands.append(
            str(i["brand"]["name"]) + str("(" + str(i["brand"]["code"]) + ")")
        )
    logger.info(" brands: %s" % brands)
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


def fetch_data():
    resultsList = (
        "https://api.corpinter.net/dlc/dms/v2/dealers/search?marketCode=GB&fields="
    )
    session = SgRequests()
    results = session.get(resultsList, headers=headers_with_apikey).json()
    for i in results["results"]:
        company_id = i["baseInfo"]["externalId"]
        url = "https://api.corpinter.net/dlc/dms/v2/dealers/search?marketCode=GB&fields=*&whiteList="
        data_per_dealer_json = session.get(
            url + company_id, headers=headers_with_apikey
        ).json()
        for d in data_per_dealer_json["results"]:
            locator_domain = "smart.com/gb/en"
            page_url_slug = d["baseInfo"]["externalId"]
            if page_url_slug:
                page_url = f"https://www.smart.com/gb/en/dealer/{page_url_slug}"
            else:
                page_url = SgRecord.MISSING
            location_name = d["baseInfo"]["name1"] or SgRecord.MISSING
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
            street_address = l or SgRecord.MISSING
            city = d["address"]["city"] or SgRecord.MISSING
            if "region" in d["address"]["region"]:
                state1 = d["address"]["region"]["region"]
            else:
                state1 = ""

            if "subRegion" in d["address"]["region"]:
                state2 = d["address"]["region"]["subRegion"]
            else:
                state2 = ""

            if state1 and state2:
                state = state1 + ": " + state2
            elif state1 and not state2:
                state = state1
            elif state2 and not state1:
                state = state2
            else:
                state = SgRecord.MISSING

            zipcode = d["address"]["zipcode"] or SgRecord.MISSING

            country_code = d["address"]["country"] or SgRecord.MISSING
            store_number = d["baseInfo"]["externalId"] or SgRecord.MISSING

            if "phone" in d["contact"]:
                phone = d["contact"]["phone"]
                if phone:
                    if "+44" == phone:
                        phone = SgRecord.MISSING
                    else:
                        phone = phone
                else:
                    phone = SgRecord.MISSING
            else:
                phone = SgRecord.MISSING

            if "brands" in d:
                location_type = determine_brand(d)
            else:
                location_type = SgRecord.MISSING
            if "latitude" in d["address"]:
                latitude = d["address"]["latitude"]
            else:
                latitude = SgRecord.MISSING

            if "longitude" in d["address"]:
                longitude = d["address"]["longitude"]
            else:
                longitude = SgRecord.MISSING

            hours_of_operation = determine_hours(d, "SMT", "SALES")
            raw_address = SgRecord.MISSING
            yield SgRecord(
                locator_domain=locator_domain,
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


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
