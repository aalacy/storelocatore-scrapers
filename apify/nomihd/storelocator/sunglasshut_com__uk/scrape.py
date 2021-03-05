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
    loc_list = []
    search = static_coordinate_list(
        radius=100, country_code=SearchableCountries.BRITAIN
    )
    cookies = {
        "mt.v": "2.765874924.1612788200341",
        "rxVisitor": "1612788202644TAUC0BOSNAQRTRQ9RN1E7SDQDSIATT4I",
        "ftr_ncd": "6",
        "sgh-desktop-facet-state-search": "",
        "tealium_data_session_timeStamp": "1612788206482",
        "userToken": "undefined",
        "AMCVS_125138B3527845350A490D4C%40AdobeOrg": "1",
        "s_ecid": "MCMID%7C31837677145346142053689448579183674801",
        "s_cc": "true",
        "dtCookie": "v_4_srv_2_sn_552PDSCGB5458UPTRJQEOVUBVQ702JEP_app-3Ab359c07662f0b428_0_ol_0_perc_100000_mul_1",
        "CONSENTMGR": "consent:true%7Cts:1612788210096",
        "_scid": "2e7e007d-1be5-4c30-9f88-b35b9318763e",
        "__utmc": "110589831",
        "__utmz": "110589831.1612788211.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)",
        "WC_SESSION_ESTABLISHED": "true",
        "SGPF": "3yVu5U0V1JDyx1r21C4VKtbi7OcadUCSnItYd8dOZNMA9sAh7EhH6zw",
        "_cs_c": "1",
        "_gcl_au": "1.1.205447344.1612788226",
        "_CT_RS_": "Recording",
        "WRUIDAWS": "3157488901570697",
        "smc_uid": "1612788231161927",
        "smc_tag": "eyJpZCI6Njc4LCJuYW1lIjoic3VuZ2xhc3NodXQuY29tIn0=",
        "smc_refresh": "13169",
        "smc_sesn": "1",
        "smc_not": "default",
        "metroCode": "0",
        "COUNTRY": "PK",
        "COUNTRY_REDIRECT": "true",
        "CATALOG_ASSORTMENT": "SGH",
        "_ga": "GA1.2.458204620.1612788211",
        "tealium_data_tags_adobeAnalytics_trafficSourceCid_lastFirst": "yext_header",
        "cookiePolicy": "true",
        "WC_AUTHENTICATION_1448415594": "1448415594%2CXlhe7UOXgaMTEu8PTNKSmx%2BmrXY9WOTQSfB3%2BqAMdw8%3D",
        "WC_USERACTIVITY_1448415594": "1448415594%2C10154%2Cnull%2Cnull%2C1612814297309%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C2140635307%2CNvKaMk3lqg0l%2BEpqKLmMqZC78KIqt4ZpvSZcFuF4lstJfOCpEft%2F6gJDhBbw0kaWZjPjXOuWcs%2Bve5z451wU5MyQ5EmYluXPq%2BhDTnVJVJcSc8VqpahXRin9AiKboDdK7WX8%2BX%2Fz76qUfMRms6cZGPn4Je5qHw4wHFBCP5fC67%2FwbxGK3aPqjPb0zo89%2Bw%2B50qSE86aiQHeRloKaRJwcGO9evZJrCK3zUR6Hb2cA9IMno1UAvUQVFc4m8QW%2B7qBTKXrjx9S0aPguyGGyLp%2FgnQ%3D%3D",
        "WC_AUTHENTICATION_-1002": "-1002%2C5mduE4auFesN87pDyNccBg3A3LZom4jI7UYlAbvrvHg%3D",
        "WC_USERACTIVITY_-1002": "-1002%2C10152%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C2140635307%2ClOiauND2AUi5bAkzrY0sroA1WcwKZSdUBG3%2F2xMtCdIUEd5v1cLz3mjtru%2B1aT7iYoUb1v5ThVHrrY6fMEpVFu%2FoBI9YdyI6Mt%2FZey92j01q0PC2d9sMFswVGTuqBGdqLfLC1wepYuNh3xaNnqaX0P47lz9zwzXvC%2BuZhAheNP8zGFZ8mEZlPOEzLQFh65fwMjB72cT2RQhfU42GpqilHRzKGeTRP1nme0OfQhBMc0aJMgSmmoWM%2BvfEKJWaQt3A",
        "WC_GENERIC_ACTIVITYDATA": "[9287112477%3Atrue%3Afalse%3A0%3AWhUilObFz7Qpitz%2BLHUTjdX9%2Fv7klunKvoPWFd1J66w%3D][com.ibm.commerce.context.ExternalCartContext|null][com.ibm.commerce.context.entitlement.EntitlementContext|4000000000000000011%264000000000000000011%26null%26-2000%26null%26null%26null][com.ibm.commerce.store.facade.server.context.StoreGeoCodeContext|null%26null%26null%26null%26null%26null][com.ibm.commerce.catalog.businesscontext.CatalogContext|20602%26null%26false%26false%26false][CTXSETNAME|Store][com.ibm.commerce.context.base.BaseContext|10152%26-1002%26-1002%26-1][com.ibm.commerce.context.audit.AuditContext|1612788197221-654745][com.ibm.commerce.context.experiment.ExperimentContext|null][com.sgh.commerce.findinstore.context.FindInStoreDefaultStoreContext|null][com.ibm.commerce.giftcenter.context.GiftCenterContext|null%26null%26null][com.ibm.commerce.context.globalization.GlobalizationContext|-1%26USD%26-1%26USD]",
        "BVBRANDID": "e4520975-41c8-4088-8159-4a1205dafe36",
        "_pin_unauth": "dWlkPU5EaG1NelUzT0RFdE1XRmpPUzAwT1RBeUxXSTJaV1V0TmpaaFpEVmhNV1V4TlRReQ",
        "_derived_epik": "dj0yJnU9ZmFoc3lOa1U0QU0wXzd6R3Uwa29NRmRGTUstbWktU2Qmbj1vQVE3M2lyUzkwMzg0VFpVbUVfa3dBJm09ZiZ0PUFBQUFBR0FuNnlZJnJtPWYmcnQ9QUFBQUFHQW42eVk",
        "MGX_UC": "JTdCJTIyTUdYX1AlMjIlM0ElN0IlMjJ2JTIyJTNBJTIyNTc4NDkyYTMtZDdjZC00NzY2LTk5MWUtNzZkYzM4MzZiZTljJTIyJTJDJTIyZSUyMiUzQTE2MTM3NTQ0MzgwMTIlN0QlMkMlMjJNR1hfVSUyMiUzQSU3QiUyMnYlMjIlM0ElMjJmY2RkODRlZi03ZmU3LTRmNDMtYTdkOC0yMzc2ZDVmYTAwMDklMjIlMkMlMjJlJTIyJTNBMTYxMzc1NDQzODAyMCU3RCUyQyUyMk1HWF9QWCUyMiUzQSU3QiUyMnYlMjIlM0ElMjJjMjgwMGZmMi1lNGJmLTQ2ZTMtODVkYy03ZDE5ZWI2MGQyMDMlMjIlMkMlMjJzJTIyJTNBdHJ1ZSUyQyUyMmUlMjIlM0ExNjEzMjMwNjM4NzcyJTdEJTJDJTIyTUdYX0NJRCUyMiUzQSU3QiUyMnYlMjIlM0ElMjJmYTEyOWJkOC0yZTNiLTQ1NzYtOGViYS03MDM1YjQyMzRjYjYlMjIlMkMlMjJlJTIyJTNBMTYxMzc1NDQzODAyOCU3RCUyQyUyMk1HWF9WUyUyMiUzQSU3QiUyMnYlMjIlM0E0JTJDJTIycyUyMiUzQXRydWUlMkMlMjJlJTIyJTNBMTYxMzIzMDYzODc3MiU3RCUyQyUyMk1HWF9FSUQlMjIlM0ElN0IlMjJ2JTIyJTNBJTIybnNfc2VnXzAwMCUyMiUyQyUyMnMlMjIlM0F0cnVlJTJDJTIyZSUyMiUzQTE2MTMyMzA2Mzg3NzIlN0QlN0Q=",
        "WC_ACTIVEPOINTER": "-24%2C11352",
        "dtSa": "-",
        "dtLatC": "546",
        "ak_bmsc": "D858AF29E673997CA745F64F1340EB4BADDED2D5B2530000951034604939F73C~plkWyrfKY32Ncv41iGsgLLaHXCIkudcFFPbekbkSrOQwIPDQN6xg/B3K1Xy6MyRGkHENrFJ7QI9D+qfsMNzj6zJQCfcHterWjSQERlohMNFywnjsZ3VuDh0C4yg+xhYvnj1zNkbAiUItVTPyphd5a3/UgpVd7EOAq/co5wSVEUOwT0pGG3LujgceVuyNu8ipS1sypyim9CH2MmsAgbGhWnIV06OfWzyjabgMgMfkD6HVRaLKgrDZZcpLJ+WzmSZq5K",
        "AMCV_125138B3527845350A490D4C%40AdobeOrg": "-1303530583%7CMCIDTS%7C18681%7CMCMID%7C31837677145346142053689448579183674801%7CMCAAMLH-1614629670%7C6%7CMCAAMB-1614629670%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1614032070s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C3.3.0",
        "__utma": "110589831.458204620.1612788211.1613501291.1614024871.8",
        "WC_PERSISTENT": "M7hIAynwUQLlwJI8qQy%2BiVfnsQOZy9czwarpUlRm9zM%3D%3B2021-02-22+20%3A14%3A52.08_1612788197221-654745_11352_1448633648%2C-24%2CGBP_10154_1448415594%2C-25%2CCAD_10152_-1002%2C-1%2CUSD_11352",
        "WC_AUTHENTICATION_1448633648": "1448633648%2CFzhIrD5nYaDVrIi8ViGfInZtWuE870lLqC%2By5OOYUJw%3D",
        "WC_USERACTIVITY_1448633648": "1448633648%2C11352%2Cnull%2Cnull%2C1614024892083%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C2140635307%2C12LzZHwr43%2BHQltpKJ7VriJQCupRJ2bCwnUS%2Fbam%2BQPSJNV%2BZtEanOyiraGPJI5w2e%2F0Q03IEoqX262Kw2MsTdWXReDn8YkXwB50WDl%2FPo1QcQiYcofqqXjBluQ3VUhrlM30gWJpCzR30d156Dos0KhjaggKoM3ea9XYyQrDPP0vTh0CjaEHnsfvk8lnFZoPu8sn2HFBwPEsrXOI2RQ8AtAsxHXJI6TjA2cV%2F0lSDG3znJaBOQDWvG80%2BnuPu2eR8g9hYHFmsm3fRIY9RfV%2BXQ%3D%3D",
        "JSESSIONID": "0000BP1gmUT9tks3UF46LUrFZPt:1c7qtq78c",
        "aka-zp": "",
        "rxvt": "1614030615186|1614028815186",
        "_cs_mk": "0.9789336553336017_1614028836995",
        "_sctr": "1|1614020400000",
        "aka-cc": "GB",
        "aka-ct": "LONDON",
        "TS011f624f": "015966d2927d8dd021d5f5e59611ddee716f3d23536cf2b882af54aaa6d91b13eef2aa2d6062fd5c23bc4b8b7b2a3557c668aa87e49316bf15787f9e7e240a35edce5b09384c92802fbf8c1cc45f127fa2dd7d82ec52c057c99de6438530a0d523ffa07ded6c4db13cfa3c17473ae702ccbc5a752291624f5a40fe3924ceabf2653b333d0649eb82caa459b5f94933d69bf7b63fd2e50e04fde30aca509b0af7887b3094c4ee158f9cebb72217f014c5268e054eb2417221d10e7950ea51c8b2f45306033ca9689a2bb3695f073a5f485477ad5e955dd3a2e9983ad7a52859c6dc3e54df471ff15064276c2ad4dcc8f9e7de06a2ebd621cdab811e54601b983cd0014a6f0f64ad1b0f5e1ad9120b73325d514d614f2f968da6debab9539572847f042b8b1dc2a8c158ccf3bd29e8123081b809ac02caa47abc7f4ba2e6109221fc4e9c2f208a3b6ace1d098ba96c6c00f56bc66a4a2d82b4f0ade9b3f71b4409431b1a9e96183f1fc9f47a632044a6eb7af654b0a1ab559ab2666bc06e4883ba907d10e4d8ed54cda5769fd06223a7dec692f728397aeed82d602c21468097945ac4eb8d28045aa1f8faeb0e32e9dd7308266498eb4f5c65b2265f3dc0b6a0002b1ff4509d41b2b543bfa7a7640343d0ab04af53b341a6d327346174ae9ddf27c60d0d0625bf0c352361c5cae08211340279ad4b651f4ca15764ec8bafea8d8091e90a270551a7fe7bfc50a4aea57b0474278094454974ea78d68d7f269fb199272598549f",
        "s_sq": "%5B%5BB%5D%5D",
        "__utmt": "1",
        "_cs_cvars": "%7B%221%22%3A%5B%22Page%20Type%22%2C%22Clp%22%5D%2C%222%22%3A%5B%22Page%20Name%22%2C%22%3AClp%22%5D%2C%223%22%3A%5B%22Page%20Section%201%22%2C%22Home%22%5D%2C%224%22%3A%5B%22Action%22%2C%22GB%3AEN%3AD%3A%3AClp%20%22%5D%2C%228%22%3A%5B%22User%20Login%20Status%22%2C%22Guest%22%5D%7D",
        "_cs_id": "f413445d-a8fc-ab37-e274-a45cad2ecd76.1612788228.16.1614029439.1614027186.1.1646952228991.Lax.0",
        "_cs_s": "6.1",
        "__CT_Data": "gpv=32&ckp=tld&dm=sunglasshut.com&apv_358_www06=31&cpv_358_www06=31&rpv_358_www06=9&apv_283_www06=4&cpv_283_www06=4&rpv_283_www06=4",
        "smc_spv": "29",
        "smc_tpv": "29",
        "smct_session": '{"s":1612788234140,"l":1614029450255,"lt":1614029450259,"t":42356,"p":1692}',
        "sgh-desktop-facet-state-plp": "categoryid:undefined|gender:true|brands:partial|polarized:true|price:true|frame-shape:partial|color:true|face-shape:false|fit:false|materials:false|lens-treatment:false",
        "bm_sv": "67E971D66C7F4C964CBBAA4345EFA5DB~KAVwIzeqNad0+ewiXbK+8P2bOht0X/m5LJj0aBmh/eMx3L76IFBbOa7C7z61FWWjw+plNIwBh8RISgC/wuqVYWACq4QneVOODkJEm0WPm72bO2MyXf4ua2w22mG8kR9+NHjCnDhFlp7HhH2DG4AA1jGQJp23wwuIFdKNlKD1Fio=",
        "__utmb": "110589831.6.10.1614024890",
        "_uetsid": "934b0270754a11eb850c3fcb8d8eef30",
        "_uetvid": "48eb4b906a0b11ebbceb7d2b2533b84e",
        "forterToken": "ef237a866745434883cb62b601ec1bf0_1614029454535__UDF43_6",
    }

    headers = {
        "Connection": "keep-alive",
        "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        "Accept": "application/json, text/plain, */*",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.sunglasshut.com/uk/sunglasses/store-locations/map?location=Manchester%2C%20UK",
        "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
    }

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
                hours = store["hours"]
                hours_list = []
                for hour in hours:
                    day = hour["day"]
                    time = ""
                    if len(hour["open"]) > 0 and len(hour["close"]) > 0:
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
                if latitude == "":
                    latitude = "<MISSING>"
                if longitude == "":
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
                loc_list.append(curr_list)
        #         break
        # break

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
