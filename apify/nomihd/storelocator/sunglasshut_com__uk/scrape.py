# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list
import json

website = "sunglasshut.com/uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        temp_list = []  # ignoring duplicates
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)

        log.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    # Your scraper here
    search = static_coordinate_list(
        radius=100, country_code=SearchableCountries.BRITAIN
    )
    cookies = {
        "mt.v": "2.1199326358.1625606035051",
        "ftr_ncd": "6",
        "SGPF": "CT-2",
        "__wid": "944770122",
        "s_ecid": "MCMID%7C31837677145346142053689448579183674801",
        "AMCV_125138B3527845350A490D4C%40AdobeOrg": "-1303530583%7CMCIDTS%7C18815%7CMCMID%7C31837677145346142053689448579183674801%7CMCAAMLH-1626210868%7C3%7CMCAAMB-1626210868%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1625613268s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C3.3.0",
        "CONSENTMGR": "consent:true%7Cts:1625606174885",
        "_gcl_au": "1.1.1391656191.1625606179",
        "_cs_c": "1",
        "__utma": "110589831.1910400054.1625606180.1625606180.1625606180.1",
        "__utmz": "110589831.1625606180.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)",
        "_scid": "93faa443-c868-4e37-9e0d-970bb308e1b9",
        "_pin_unauth": "dWlkPU5EaG1NelUzT0RFdE1XRmpPUzAwT1RBeUxXSTJaV1V0TmpaaFpEVmhNV1V4TlRReQ",
        "_fbp": "fb.1.1625606184218.1575229277",
        "_sctr": "1|1625598000000",
        "_ga": "GA1.2.1910400054.1625606180",
        "_uetvid": "68564130de9f11eb8f62c3b56bf6d995",
        "_derived_epik": "dj0yJnU9cjFkMU5ZcUN4RTBfaW9ScDl4eTZ6N0FGOHhhdFRLTmImbj1aRU1IXzBETzQ2d1hyVmxTXzNBQ053Jm09ZiZ0PUFBQUFBR0RreUQ0JnJtPWYmcnQ9QUFBQUFHRGt5RDQ",
        "__CT_Data": "gpv=2&ckp=tld&dm=sunglasshut.com&apv_283_www06=2&cpv_283_www06=2",
        "MGX_UC": "JTdCJTIyTUdYX1AlMjIlM0ElN0IlMjJ2JTIyJTNBJTIyNjZkOTAyY2QtYWQxZC00MzRhLThmNTgtN2ExOTFmZjVkN2RjJTIyJTJDJTIyZSUyMiUzQTE2MjYxMzE4MDU2ODclN0QlMkMlMjJNR1hfUFglMjIlM0ElN0IlMjJ2JTIyJTNBJTIyYmZjMjMzN2MtZDVhYi00ODM1LThlMjgtZjM2YTA2NzBlODEyJTIyJTJDJTIycyUyMiUzQXRydWUlMkMlMjJlJTIyJTNBMTYyNTYwODAwNzIwNyU3RCUyQyUyMk1HWF9DSUQlMjIlM0ElN0IlMjJ2JTIyJTNBJTIyMzRmNzRhNDAtODYwNC00YTc4LWE0YmYtMmRkNDg5YWY2Y2YzJTIyJTJDJTIyZSUyMiUzQTE2MjYxMzE4MDU2OTUlN0QlMkMlMjJNR1hfVlMlMjIlM0ElN0IlMjJ2JTIyJTNBMiUyQyUyMnMlMjIlM0F0cnVlJTJDJTIyZSUyMiUzQTE2MjU2MDgwMDcyMDclN0QlMkMlMjJNR1hfRUlEJTIyJTNBJTdCJTIydiUyMiUzQSUyMm5zX3NlZ18wMDAlMjIlMkMlMjJzJTIyJTNBdHJ1ZSUyQyUyMmUlMjIlM0ExNjI1NjA4MDA3MjA3JTdEJTdE",
        "_cs_id": "e03e1136-2649-ac71-cc8c-52ffd8d75e88.1625606183.4.1625667616.1625667616.1.1659770183309.Lax.0",
        "JSESSIONID": "0000Wt7e67AwzWv5k49LAkPc_XS:1c7qtp224",
        "WC_SESSION_ESTABLISHED": "true",
        "WC_PERSISTENT": "KJ6b3Z6RJa4FaFzeIN2vMQaJDtOm2dYqr9qcaeJROHQ%3D%3B2021-07-08+19%3A46%3A48.064_1625606194763-977669_11352_-1002%2C-24%2CGBP_10152_1451692081%2C-1%2CUSD_11352",
        "WC_AUTHENTICATION_-1002": "-1002%2C5mduE4auFesN87pDyNccBg3A3LZom4jI7UYlAbvrvHg%3D",
        "WC_ACTIVEPOINTER": "-24%2C11352",
        "WC_USERACTIVITY_-1002": "-1002%2C11352%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C905770320%2CbKpi%2F4kGorVf6nhm2TS5syRG%2BayWvxIyMZ8iYMo2z3p%2BFlB%2BxVJCr6wkwY3%2BjLnM6Bkjy0%2BPk%2B%2ButdIfK41INZFreaaoZ6Xid7MeXNMSIcCw1Kv4i1VIFWGMLlSXXkoO6Tc8qqM0RrvsU%2FtboMP16h8OyrAJarH62K7CdGt%2BpX49Me%2BXBQlpNqPhZTCRTGtpSDrPjUw1RxyUX5XZcMLXTPMeeExBI59ROV3WnnvlW%2Fox8N5VSP69a8TykeYIlcLc",
        "WC_GENERIC_ACTIVITYDATA": "[9803492648%3Atrue%3Afalse%3A0%3AG2ErV1O%2BVbrGsB508GqsVlXwdyyybtT0lY6m%2BNjRcB8%3D][com.ibm.commerce.context.ExternalCartContext|null][com.ibm.commerce.context.entitlement.EntitlementContext|4000000000000001004%264000000000000001004%26null%26-2000%26null%26null%26null][com.ibm.commerce.store.facade.server.context.StoreGeoCodeContext|null%26null%26null%26null%26null%26null][com.ibm.commerce.catalog.businesscontext.CatalogContext|20603%26null%26false%26false%26false][CTXSETNAME|Store][com.ibm.commerce.context.base.BaseContext|11352%26-1002%26-1002%26-1][com.ibm.commerce.context.audit.AuditContext|1625606194763-977669][com.ibm.commerce.context.experiment.ExperimentContext|null][com.sgh.commerce.findinstore.context.FindInStoreDefaultStoreContext|null][com.ibm.commerce.giftcenter.context.GiftCenterContext|null%26null%26null][com.ibm.commerce.context.globalization.GlobalizationContext|-24%26GBP%26-24%26GBP]",
        "TS011f624f": "015966d292cf05a0a8cab3e399bade438ddae43a3508e8a34acbb4f795b9f69fce89e49e30acb03ed1aef018ecdc8cb0453b626a7857d92822735a6a33abaaff8a8bca4f96c3d74124238b0113a8bf842acb5b3b82e4bae81895f101cf960bd46aa94e504e8a23937482e95b3b31e30ae2d44a6e0d63706d4dad5dc40995f061340ddce43950f1b0ab5e4a043edf0046e80387912245cb872c66d2996668eede1251b2f66a",
        "aka-zp": "",
        "cookiePolicy": "true",
        "rxVisitor": "16257736131288GOR2UNKJIRKANGNALK0EF3AFJJJTFJL",
        "dtSa": "-",
        "dtLatC": "250",
        "rxvt": "1625775413301|1625773613135",
        "sgh-desktop-facet-state-search": "",
        "sgh-desktop-facet-state-plp": "categoryid:undefined|gender:true|brands:partial|polarized:true|price:true|frame-shape:partial|color:true|face-shape:false|fit:false|materials:false|lens-treatment:false",
        "bm_sv": "BBA179B35BD32374E0F0ECBF464F1822~7bnyAw/+c2v2CvWdIeAtBMIrA0Z7IstX7I1fZPQP0mNEF+4bJmoh+gCb9V4MoLWU3d1Uvkr56BYPmbMBklcEHhFG8gMl9j4bACh8FKRSeu3xrJeBHhO421FgQqGLOVk2VKTu2eV2t/tpyc/ZZS/YnBxrbWRexe+dWqxs2WXWkFg=",
        "ak_bmsc": "35B6880B1A0F6FF9F5AFB55432D102DA~000000000000000000000000000000~YAAQxfAoF1y8VoN6AQAAGaaohwzqq23SpT7s/Icnn9L7zDKCWkvQGYKGpNoOpT31mx6BF9CaC/m4fcUskBWw96l8GGo2PqVZx0yqe3jS9zKThUiZQdeq4bZHU20/bJTAUyoKWYI4AcmB1kqnVbgaDBn3asFFD47baGTK06CSJMa/+/i0ewbmxO/cvIB+5dlXlM3ZKAL+/nPetjJAvF/xgTicZ1G/hLFXpgtNxDmaO7jvsKWHLZh3Qgk1NRt4fuaKVLgdrKhqpz098XfHd4kYVJ/T5rzm5CLQ43f2zdEeGz4LtdmZeb+98Iiuoa7vdEfLNZc2pFULhjIzn2qGxXxhWkE1AoD+X0ftpk3PbXLAyflj/fHvGYLj6iMTAmSeTVb6G2Pr3ZCmMLGDN7ZMQYWhL6pP+pvYGrIs0eo907VMXCubrKHz+XdSuWbLrH+9HFQsQ09LbwQgA/AOXZO8V8q/YoQ2aZXYkFE1IIoBE6nByevWRFrRldPaqq3337kJURI=",
        "forterToken": "7b4921495dba4f748ff56c7b8965abee_1625773613721__UDF43_6",
    }

    headers = {
        "authority": "www.sunglasshut.com",
        "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        "accept": "application/json, text/plain, */*",
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.sunglasshut.com/uk/sunglasses/store-locations/map?location=London%2C%20UK",
        "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    }

    store_id_list = []
    for lat, long in search:
        log.info(f"{(lat, long)}")

        params = (
            ("latitude", lat),
            ("longitude", long),
            ("radius", "2000"),
        )

        stores_req = session.get(
            "https://www.sunglasshut.com/AjaxSGHFindPhysicalStoreLocations",
            headers=headers,
            params=params,
            cookies=cookies,
        )

        stores = json.loads(stores_req.text)["locationDetails"]
        for store in stores:
            if store["countryCode"] == "GB":
                page_url = "<MISSING>"
                locator_domain = website
                location_name = store["displayAddress"]
                if location_name == "":
                    location_name = "<MISSING>"

                street_address = store["address"]

                city = store["city"]
                state = "<MISSING>"
                zip = store["zip"]
                country_code = store["countryCode"]

                if country_code == "" or country_code is None:
                    country_code = "<MISSING>"

                if street_address == "" or street_address is None:
                    street_address = "<MISSING>"

                if city == "" or city is None:
                    city = "<MISSING>"

                if state == "" or state is None:
                    state = "<MISSING>"

                if zip == "" or zip is None:
                    zip = "<MISSING>"

                phone = store["phone"]
                location_type = "<MISSING>"

                store_number = store["id"]
                if store_number in store_id_list:
                    continue
                store_id_list.append(store_number)
                hours = store["hours"]
                hours_list = []
                for hour in hours:
                    day = hour["day"]
                    time = ""
                    if len(hour["open"]) <= 0 and len(hour["close"]) <= 0:
                        time = "Closed"
                    else:
                        time = hour["open"] + "-" + hour["close"]

                    hours_list.append(day + ":" + time)

                hours_of_operation = (
                    "; ".join(hours_list)
                    .strip()
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", "-")
                    .strip()
                )

                latitude = store["latitude"]
                longitude = store["longitude"]
                if latitude == "" or latitude == "0.00000":
                    latitude = "<MISSING>"
                if longitude == "" or longitude == "0.00000":
                    longitude = "<MISSING>"

                if hours_of_operation == "":
                    hours_of_operation = "<MISSING>"
                if phone == "":
                    phone = "<MISSING>"

                curr_list = [
                    locator_domain,
                    page_url,
                    location_name,
                    street_address,
                    city,
                    state,
                    zip,
                    country_code,
                    store_number,
                    phone,
                    location_type,
                    latitude,
                    longitude,
                    hours_of_operation,
                ]
                yield curr_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
