from lxml import html
import time
import json
from sglogging import sglog
from sgrequests import SgRequests, ProxySettings
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import os

os.environ["PROXY_PASSWORD"] = "apify_proxy_4j1h689adHSx69RtQ9p5ZbfmGA3kw12p0N2q"
session = SgRequests(proxy_escalation_order=ProxySettings.TEST_PROXY_ESCALATION_ORDER)
# session = SgRequests()
website = "ralphlauren.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

start_urls = [
    "https://www.ralphlauren.com/findstores?dwfrm_storelocator_country=US&dwfrm_storelocator_findbycountry=Search&findByValue=CountrySearch",
    "https://www.ralphlauren.com/findstores?dwfrm_storelocator_country=CA&dwfrm_storelocator_findbycountry=Search&findByValue=CountrySearch",
    "https://www.ralphlauren.com/findstores?dwfrm_storelocator_country=GB&dwfrm_storelocator_findbycountry=Search&findByValue=CountrySearch",
]

headers = {
    "authority": "www.ralphlauren.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en;q=0.9",
    "cookie": 'dwanonymous_55b6a3b329e729876c1d594e39f4ac4e=ab6AU1Use5Gr80zltO4pKzqi0L; mt.v=5.827585820.1643803146976; pzcookie="{\\"pz_id\\":\\"\\",\\"EP_RID\\":\\"\\",\\"gender\\":0}"; headerDefault=1; _mibhv=anon-1643803158441-9071657268_8245; _scid=cb262d45-283c-4020-b19e-26edd0583dec; modalLoad=1; kndctr_F18502BE5329FB670A490D4C_AdobeOrg_consent=general%3Din; dwpersonalization_55b6a3b329e729876c1d594e39f4ac4e=3546b728c8166d5fdf6a0753f920220302110000000; kndctr_F18502BE5329FB670A490D4C_AdobeOrg_identity=CiY1OTg1MjI2MTgzMzI5NTg5Nzc1MTg5OTQ2MTA5MTY2OTYxMzQ1N1IPCMXYi9brLxgBKgRJUkwx8AGfgrm68S8%3D; _pxhd=8D2dmqRbFDe44u6HQsE5vF/xV0A-gV1bPW-zZM6uCL/wX9rJlm25AGijmw-bBenRpgPUeIU6IXiSlDuJaf4wAQ==:FY1TvKbJLJ1c4uAS08w56rN82uKZmhWAQGS3Q6rOjnoO8hvfE8PK83-t-kyjp09Y34j1mMtoA0JL2G0m0YWjrgju4LWoUkP9848ds0YKzkg=; cqcid=ab6AU1Use5Gr80zltO4pKzqi0L; cquid=||; __cq_dnt=0; dw_dnt=0; AMCVS_F18502BE5329FB670A490D4C%40AdobeOrg=1; s_ecid=MCMID%7C59852261833295897751899461091669613457; rmStore=atm:mop; ftr_ncd=6; s_cc=true; _tt_enable_cookie=1; _ttp=510db8ab-6720-4ac1-8940-2bf417f394fa; dw=1; dw_cookies_accepted=1; _fbp=fb.1.1652192131333.897600786; _cs_c=0; _gcl_au=1.1.425680880.1652192132; _gid=GA1.2.1545192978.1652192132; crl8.fpcuid=fefa0493-f120-48fa-9e16-5c1ea3d7df4f; __cq_uuid=abPqTtivLCF1s2zFN0iyfPtrvK; __cq_seg=0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00; _pin_unauth=dWlkPU1HSmxORGRtWlRndE9HRm1OUzAwTXpZeUxXSTNOR1l0WVdObFltTXdNR0l3T1RZMg; _sctr=1|1652119200000; pxcts=76c6e1dd-d08c-11ec-a230-6650594d7375; _pxvid=a2dd3896-d06b-11ec-affc-524542537053; _clck=16qvl7e|1|f1d|0; _4c_=jVNtb5swEP4rFR%2FyqYBfMOBIqErSalrXru2y7msEthNQCEa2Cc2q%2FvfZeWm6JaqWD%2BTuueeOe467V68vReMNYUwQSgChBIL00luKjfaGrx5r3XPtHp2qvaFXGtPqYRj2fR%2BovG7LOu%2BUaAImV6F36THJhWVBGkAYQAuY39bFMbBmqyTvmJmZTes4vSguNF%2FaABfriolZX3FTumSC4yNaimpRGgsnNHJoqxwlwAmxXl81XPbHTEzjI%2FqeSbbo4%2FWjtV0j01K2bdUsxvlij0xKwZayM3t3tTSLmZadYq5RCxRK9lq4N09KJVfiAgInTtoZeXdV071YR4m5UGpL%2BmxIc9ucNlIJfcX7uVrNtk4tWW7%2FZ7zSJm%2BYeG4qk62qwRmKFrli5Texye7AFN6Cc5xV%2FnKolOGzjDo3lem4yM4GZbPYR5nsGqM2E%2BmcVtqa9c7utHiscyauhcmrWo84t5J0Ns9rLc7VdLqLza55u13ZdGsNHDze%2FMrrTmRW0w6109SVcbP%2FZ3r7gM3%2FO2bxh%2FufP2bjm9Hk4fuHL6BXwqiK6ZPPUIRah62s5YdALU2n3ZaGMLyd%2BihAKMD%2B3WQahTohGEKEAEAIwfRq9DTO4GBV8YzQ1F5ODFOMESUpTRICU0qjGAIK45jGEEckGYyebjK3Mu3a7ak13FxqJ3Hb%2FZfR7Pnr9Xb5QZySBCIcuJOEFEGMDvLuJ1vO%2F73Se7v0XnaHjUkcRwAQYu%2FR2CtOnWd%2FlqEqvr9wDxaAxQJzn2OM%2FSjh0E%2FntPAR4gxHOKcFdI1va8YARDHCFABqi6yrQw2QR5BzBP0kKaAfzaPEL%2FII%2BHPGGeGgwBwl3ntfKEHA1kB03xdMD2219b4iPJLTKLZkgg%2Fk6F1Euz5hO8mOHZ1K3h2zL5pP0k4m9fb2Bw%3D%3D; _ga_5K6QZYC3ZW=GS1.1.1652270245.2.1.1652270596.0; ftr_blst_1h=1652274812651; mt.sc=%7B%22i%22%3A1652278553812%2C%22d%22%3A%5B%5D%7D; mt.mbsh=%7B%22fs%22%3A1652278554495%7D; dwac_102c95db27e6f188d36d6303ba=A-w_6AkJSdgNfIO3t3d4WvglwHEV19V8FgQ%3D|dw-only|||USD|false|US%2FEastern|true; sid=A-w_6AkJSdgNfIO3t3d4WvglwHEV19V8FgQ; dwsid=vUcH7qHfAyoau_BXwkcJjUaO-He9AZ-OAcNwFngkbTAdkiZlAf5NLv5VXPxpb4czuIU9wOvDNRs8y8ouJPU9bQ==; AMCV_F18502BE5329FB670A490D4C%40AdobeOrg=-2121179033%7CMCIDTS%7C19123%7CMCMID%7C59852261833295897751899461091669613457%7CMCAAMLH-1652883357%7C3%7CMCAAMB-1652883357%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1652285757s%7CNONE%7CMCAID%7CNONE%7CMCSYNCSOP%7C411-19130%7CvVersion%7C5.3.0; outbrain_cid_fetch=true; pageNameDuplicate=about%3Astorelocator; forterToken=f8c194210dd04192839e4dd2f5578b20_1652278627297__UDF43_6; _uetsid=a6c2c1b0d06b11ec89d609c3ad671579; _uetvid=8cd2e320841f11ec8d93c9fac21e0d01; OptanonConsent=isIABGlobal=false&datestamp=Wed+May+11+2022+20%3A17%3A12+GMT%2B0600+(Bangladesh+Standard+Time)&version=5.11.0&landingPath=NotLandingPage&groups=C0005%3A0%2CC0002%3A0%2CC0004%3A0%2CBG5%3A0%2CC0003%3A1%2CC0001%3A1&hosts=&AwaitingReconsent=false; _cs_id=a639eec2-3db6-aa49-ebfa-3d3d34ae51bd.1652192132.8.1652278632.1652278518.1.1686356132008; _ga_MHJQ8DE280=GS1.1.1652278553.6.1.1652278631.54; _ga=GA1.2.1506857123.1652192132; _gat_gtag_UA_106096199_1=1; _px3=8cadf6d713c21b13e060aaa307f882904e235129057a05ff8e2b476a95d4bbf8:ktMJnlat+r2aaqM66by4kykX0dj2K/MlrwpJweDD8Y6JxbU2Dy4gJyd+3hR+DfhIp5yMgu7dKZCnpnuFDleTdA==:1000:9lLsloLt3LCt/2g6kwWGv3aNakHpxbAmQN7tVxxt6+vRWp87L2RVX3nVekJRm7LajQ0tH9UtLNN4azqm+1gCnhKKHkoqHSqtY7e5EmKRso+ZTHqXEW3oYmP4pk0uFQZEMMWgqgY16y9tyff/M072swZRDRk9xQDAnxeVPr/gUi9FyA8VPwzk5q4kB4cKZrTi/w7HndNmyxzZNHiEtwyaEQ==; _cs_s=5.0.0.1652280433512; _clsk=1s75621|1652278634448|18|0|h.clarity.ms/collect; s_sq=poloralphlaurenlotusprod%3D%2526c.%2526a.%2526activitymap.%2526page%253Dabout%25253Astorelocator%2526link%253DSEARCH%2526region%253Ddwfrm_storelocator_int%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Dabout%25253Astorelocator%2526pidt%253D1%2526oid%253DSearch%2526oidt%253D3%2526ot%253DSUBMIT; RT="z=1&dm=ralphlauren.com&si=96e3bcb7-d61b-43cb-9e6e-150470cf1598&ss=l31nznhx&sl=3&tt=doq&bcn=%2F%2F684d0d48.akstat.io%2F&ld=1oer&ul=1rtd"; mt.v=5.827585820.1643803146976; __cq_dnt=0; dw_dnt=0; pzcookie="{\\"pz_id\\":\\"\\",\\"EP_RID\\":\\"\\",\\"gender\\":0}"',
    "referer": "https://www.ralphlauren.com/stores",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
}


MISSING = SgRecord.MISSING


def get_var_name(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def get_JSON_object_variable(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = get_var_name(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
    if value is None:
        return MISSING
    value = str(value).replace("null", "").replace("None", "").strip()
    if len(value) == 0:
        return MISSING
    return value


def fetch_stores(start_url):
    response = session.get(start_url, headers=headers)
    log.info(f"{start_url} >> Response : {response}")
    body = html.fromstring(response.text, "lxml")
    data = body.xpath('//*[contains(@data-storejson, "[")]/@data-storejson')[0]
    stores = json.loads(data)
    jsons = body.xpath('//script[contains(@type, "application/ld+json")]/text()')
    dataJSON = []
    for jsonData in jsons:
        if '"openingHours"' in jsonData:
            dataJSON = json.loads(jsonData)
            dataJSON = dataJSON["store"]
            break

    for store in stores:
        store["location_name"] = MISSING
        store["street_address"] = MISSING
        store["hoo"] = MISSING
        store["country_code"] = "US"

        if "latitude" not in store:
            continue
        for data in dataJSON:
            if data["telephone"] == "":
                data_phone = "None"
            else:
                data_phone = data["telephone"]
            if (
                "latitude" in data["geo"]
                and f"{data_phone}" == f'{store["phone"]}'
                and f'{data["geo"]["latitude"]} {data["geo"]["longitude"]}'
                == f'{store["latitude"]} {store["longitude"]}'
            ):
                store["location_name"] = data["name"]
                store["street_address"] = data["address"]["streetAddress"]
                store["country_code"] = data["address"]["addressCountry"]
                ooh = []
                if (
                    data["openingHours"] == "LOCATION CLOSED"
                    or data["openingHours"] == "Coming Soon"
                    or data["openingHours"] == ""
                    or data["openingHours"]
                    == "By appointment only. | Solo su appuntamento."
                ):
                    store[
                        "hoo"
                    ] = "Monday: Closed, Tuesday: Closed, Wednesday: Closed, Thursday: Closed, Friday: Closed, Saturday: Closed, Sunday: Closed"

                elif "Opening mid-June" in data["openingHours"]:
                    store["hoo"] = "Opening mid-June"
                elif "Opening mid-May" in data["openingHours"]:
                    store["hoo"] = "Opening mid-May"
                elif "MON" in data["openingHours"]:
                    store["hoo"] = (
                        data["openingHours"]
                        .replace("<br>\n", ", ")
                        .replace("<br/>\n", ", ")
                        .replace("<br/>", "")
                    )
                else:
                    weeks_dict = json.loads(data["openingHours"])

                    for day in [
                        "monday",
                        "tuesday",
                        "wednesday",
                        "thursday",
                        "friday",
                        "saturday",
                        "sunday",
                    ]:
                        if "isClosed" in weeks_dict[day]:
                            ooh.append(day.title() + ": Closed")
                        else:
                            ooh.append(
                                day.title()
                                + ": "
                                + weeks_dict[day]["openIntervals"][0]["start"]
                                + "-"
                                + weeks_dict[day]["openIntervals"][0]["end"]
                            )

                    store["hoo"] = ", ".join(ooh)

    return stores


def fetch_data():
    for start_url in start_urls:
        stores = fetch_stores(start_url)
        log.info(f"Total stores = {len(stores)}")
        for store in stores:
            location_type = MISSING

            store_number = get_JSON_object_variable(store, "id")
            page_url = (
                f"https://www.ralphlauren.com/Stores-Details?StoreID={store_number}"
            )
            location_name = get_JSON_object_variable(store, "location_name")
            location_name = location_name.split("-")[0].strip()
            street_address = get_JSON_object_variable(store, "street_address")
            city = get_JSON_object_variable(store, "city")
            zip_postal = get_JSON_object_variable(store, "postalCode")
            street_address = street_address.replace(f",{zip_postal}", "")
            state = get_JSON_object_variable(store, "stateCode")
            country_code = get_JSON_object_variable(store, "countryCode")
            phone = get_JSON_object_variable(store, "phone")
            latitude = get_JSON_object_variable(store, "latitude")
            longitude = get_JSON_object_variable(store, "longitude")

            hours_of_operation = get_JSON_object_variable(store, "hoo")
            hours_of_operation = (
                hours_of_operation.replace("<br/>\n", " ")
                .replace("<br/>", " ")
                .replace("<br>", " ")
                .replace("\n", " ")
                .replace("<br/", " ")
                .strip()
            )

            raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
                MISSING, ""
            )
            raw_address = " ".join(raw_address.split())
            raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
            if raw_address[len(raw_address) - 1] == ",":
                raw_address = raw_address[:-1]

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
                raw_address=raw_address,
            )
    return []


def scrape():
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    count = 0

    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
            count = count + 1
    end = time.time()
    log.info(f"Total Rows Added= {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
