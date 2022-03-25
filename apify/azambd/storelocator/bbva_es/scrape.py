from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog

session = SgRequests()

MISSING = "<MISSING>"
DOMAIN = "bbva.es"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

headers = {
    "authority": "www.bbva.es",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    "tsec": "eJxtlEmLg1gAhP/K0FfpdkmMBtIN+tyNGuMWvenzxbjvRv310wMzwxzmWlRRFBTfxR0R/ENNvz/OBHlmT5D+fKbH5PN4PjOf7OlJfTJUfGKo5IBgQn384aNhzNvm+6NqYVx9/FzEBg5bN/1qXJW1Qz696h9BdFCKcMAD/KYDh77FaZo32QX/P/MF5N0LDUI8xT/UexC8SkjJXOEMmwMS7kk+1ICKWH98zcVh24Uo7mdvm6HIGrajgLGoZrMmcNZuHqbuW7bbGnT/Drka2Nendl1vjuJ19DxpkxiBCJxVYus2Rr21CTeuAS0sqiDiGO4+jFlKTHvS+ukV++HQy2CYVli4HaJE2VPTvUY1JHRnFp4h2QwCwM3ksWYPxwIHAHO3t6zgrnND4Jg+ZnSnZL32/g7dULA3EbDLC7+5O0fn9c6tmzPnpJ16FR4lTUFV7SGrdjdg+KrwgShz3T1d3MluTW8syLWIRapfB5mvxWcdLeFwqmo8lCNHPND3VDAPjPjupanfcZtMrUMcafeMV/AckePbaY3q3NNbxNTDMck5/bqZOOY8DXKN6Z12U0x/od+Cp6tImkvRc8AEbu9GjhF2N0UiXG9DtMrxZuPAwlf0BcdOt0f/8BjtXMev32mMTVHUacS31sjg6JtHyScN4dEY3jkPw+q576jreZ/SjesRMDxcwOxjd2wg5eQk5drUE3ajyuMNXsmS3VhjnfKaj+7r0kcnp9zHgFToK7qv9uYczGDHXQtxlKgwrKHmmBamXglq+VpLb3DPUIQZZHKf5saX8ox+S2/VoHPGg7VyFZdAPcVVOOuYj6mjB8ujZ86K0NXHWDQf26QnS7hgfjkbThIr4UEZCojBgXiTdgKfGr+M2K32j7R4OjTIyTu2vZf8Cbs5RG4d8q4YNdOIJ9mXR0qstTTTZ0qxrP79wgrd1MPhiH7/VTttPJEBsSPMCpjyec7kMpm7kkivxoyxfADNl6uOcSmLz+5RY2swGQCkXFQnVDRpB77NCD/HC87yC9HD+Gag+PKhbwt6W6NaqychrvjwELIiN2p3QdHwHL5jvyaXltgwgS1Tqr65PgdEBnDzMVsZgzbjvTFDHRJAPMIzUGjfpe2JUP01qh0nb1guoidgSlmfoo4z0nFxLEQXqiixpdQrbra/1iLN5YUSxJ7k1BiZBH5bOtaljAZMmyjxjq3WeTtESIgl8j2tjdEXfjd25UxrvArD7XrFKHlrmD4BMGBcrMMXVAhQG3P7+/uC/wcSfwNDRxtX5fH4U41JsqCvbviC+XOIv6Zfon3BKobkP7F/rRf8L9z9/Anl0KmG",
    "content-type": "application/json",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36",
    "sec-ch-ua-platform": '"Linux"',
    "accept": "*/*",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.bbva.es/general/oficinas/la-coruna/carino/carino/5861",
    "accept-language": "en-US,en;q=0.9",
    "cookie": 'BIGipServerpool_BBVANET_GLOBAL_SSL=3390679232.47873.0000; PD_STATEFUL_3a49a738-9f80-11e4-a39f-005056b6703c=%2Fgeneral; sgSegmento=tcm:924-36738-4; sg=tcm:924-125242-4; AMCVS_D906879D557EE0547F000101%40AdobeOrg=1; s_ecid=MCMID%7C67664485597827215681492018936442767806; s_cc=true; s000001=1231434506.29735.0000; akaalb_ALB_WWW_BBVA_ES_ASO=~op=WWW_BBVA_ES_DEFAULT:PR_www_bbva_es_TC1_NG|~rv=72~m=PR_www_bbva_es_TC1_NG:0|~os=733dde66eb673392daf02439bd6f3465~id=fc597b4c0069d4e87c879a48c660b673; check=true; atc=4; aceptarCookies={"version":5,"publicidad":true,"analitica":true,"personalizacion":true,"tecnica":true}; _gcl_au=1.1.55668256.1647950091; TLBS_B01=0000UE6MJIthIzrFI42itXLxZLT:1chiv3pp6; refInterno=https://www.bbva.es/general/oficinas/guadalajara/marchamalo/marchamalo/2951; s_sq=%5B%5BB%5D%5D; _abck=4D19A13673667B6670602274A54650DC~0~YAAQUEo5FzVv2rR/AQAAXjCbwQdDP9iQVAu7tK+zvFNjG8fBt+hEogq2lPp8M9aFh8yRQTHD16cmPQvpPJUh95e38q0Ez/FLO2QplMjpwc/lywrvHKd1ZCDU1fcyiEK7fseTtJ9VuqTFiVSkAWqsobkgkrx7C5ape9s2e0w26oCJWwJFUpFR/bRKEDKXt5Cxv9Xk0Stv0J6WBWVgJHTfAw4wOwIg3Sii37dPyhfV5eLExYwIJW8UG/6kH6dSRc7knPdWwSGGOmtLxawSFPBDK5EI9XbQKQOfT9oUeKvEYia5x9dYOyoLJCCVrnHi4fMkOa/KleZYNwsRRdsnYB7tGlpWi1Iaw8dmqKWy8dJiF4ubGQUkOUCHog8jxWW/eD5WrE93GbIx0qn8RThNnGHCCBPWRVM=~-1~-1~-1; bm_sz=E584E8139AE5BAC724DD694A58718EBC~YAAQUEo5FzZv2rR/AQAAXjCbwQ/VTWGy2Q6aLxudjQckFbHsSECMC6DJWEoNnR6nqEySFcoVQwLYar13b3obvDrgLLWXXaMYLW/JaUWiE9pjfRP/n5uhnaUe/zADQAwFY9dkGzprCb4jbb8vLZH6FjOoUHYPXR59ToRNG71IdFH92dYXLIfVWSwLlClNSFkxMgC+pDtYvgRMP4deeS6ItW4uss+S88IU90IZNrnVuVzCShvn9fxnt34ItC8AUEa5UGFwzhutDytKMNMoVdgEXuZNEbpvMpHD4J+MltoUg78=~3163193~3752754; lastPageAEM=https://www.bbva.es/personas.html; AWSALB=zuMmVFELwRrbqfSCUgQrklujtm0kYCPk8oNQZHrwUItSXFGP+XBiZlvKZFdjC8W+Xf9T55y7IJ7j/yTt0jb2yfiMhdtYXNGOOYuF53QkxYncEuKwuv34DXhUsPId; AWSALBCORS=zuMmVFELwRrbqfSCUgQrklujtm0kYCPk8oNQZHrwUItSXFGP+XBiZlvKZFdjC8W+Xf9T55y7IJ7j/yTt0jb2yfiMhdtYXNGOOYuF53QkxYncEuKwuv34DXhUsPId; ak_bmsc=83405B8D4553CD556AE05F19D5052491~000000000000000000000000000000~YAAQUEo5F2yF3LR/AQAA9V8vwg8fb7bDqZfRVbJBy/X+JgKdaRhigWI1viYprAKv2ikKxg9OCMLNAh5bjRAJ6Bwuht8ohiAyVMp/IfAnjbIrC0JRC3a0qaeLvfmEfWocE5Yxco5V0KEKBQPWpkZsdTxt06697OZNUmfSGHrznbL1YCE6HSYGc7sDarIvwK0c4knr4xeA5Jlvh5wE1bHx6tU00BfaLQ5aD4x3Km/A76fUL1Sj7K2sl+B3fryXi1gPbkBnejKeAxn7wlQIGKIvSe9TsVmiv8hOcQ7NFV0VLF3PoLaI+pxnOV5LhCHT8g8/BqaScXG3eOBpBUIIX2897eHwGr95PtUz32NZjoUlhCAPX/vxR9vtYLRY1rOL76LJJYEhCd7kTw==; mbox=PC#03bc185b8c7142549b611c7779c48fd9.38_0#1711475161|session#40f956c46df045e49ce84dcc45d06295#1648232220; mboxEdgeCluster=38; headeralert_header_donacionucrania={"version":1,"saturation":9999,"counter":10}; gpv_url=https%3A%2F%2Fwww.bbva.es%2Fgeneral%2Foficinas%2Fla-coruna%2Fcarino%2Fcarino%2F5861; language=es; AMCV_D906879D557EE0547F000101%40AdobeOrg=-637568504%7CMCIDTS%7C19077%7CMCMID%7C67664485597827215681492018936442767806%7CMCAAMLH-1648835162%7C3%7CMCAAMB-1648835162%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1648237562s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.1.1; utag_main=v_id:017f7c9254f70003653a8467e22d05068004506000b80$_sn:7$_se:2$_ss:0$_st:1648232163561$vapi_domain:bbva.es$ses_id:1648230360346%3Bexp-session$_pn:1%3Bexp-session; s_nr=1648230363570-Repeat; gpv_pn=escritorio%3Apublica%3Ageneral%3Aoficinas%3Ala-coruna%3Acarino%3Acarino%3A5861; gpv_pt=informacion; gpv_sl1=localizador%20de%20oficinas%20y%20cajeros; bm_sv=5597B712C5AED765B88A033142329C0A~qtlj1CFluKzvOu4S9cwZcPc30nAidbuEfB3HvTLhcZiDHAtl8sAPKdYvVv0asYaoInfLUXu1UeQKf58k4s2qSYCyymQ51dS3WRcbLhyoHaoWCh8VVa8QaZJbwbpwjyUByq/er8AfVfEl+OdBeuSabA==; _abck=4D19A13673667B6670602274A54650DC~-1~YAAQUEo5Fz+H3LR/AQAAVskvwgc+g9bjUm1ix+hsTZksBsZwURPed4Kig8XHtIs+r7yvnCRzkmFgFvhkrm3u8GXMw+SMbZpAdQTZx3fn2xFtSR/f97ZmEzb71oEH2UUJsuAVtNTfgeq/TGuNlcBa7p+yVD3FV9FRDRqOXIOPQTLIWtJbQirrd7Rdh5BapunGQZI8m6B/Zp6prdXdhRq2/GEzcvOYGBdCLTAFOmssP+DWvXCv7MJpGpaRNfw/gBiWvBbHVJ8vWE+F6r1+M1Qdrpzgy/rse8i5jvFGngn44UP0NhQZe7RnEklMKs27GUfWSpUGaASN36FnwPyNjCaghjp3lvh3Qo+W7QMxVaioqBUxdAukCI1W9/iJgZl8Q6IWM4Uf03gSxkvY/xMLrJOxKrIQhd0=~0~-1~-1; bm_sv=5597B712C5AED765B88A033142329C0A~qtlj1CFluKzvOu4S9cwZcPc30nAidbuEfB3HvTLhcZiDHAtl8sAPKdYvVv0asYaoInfLUXu1UeQKf58k4s2qSYCyymQ51dS3WRcbLhyoHapFZ8fZr9xdqrsrIgyldzNx1jPS4mHXqxYbr6i3/W5EdA==',
}


def get_stores(sitemap_url):
    """
    Get all branches from sitemap and removed duplicates based on store_number
    """
    response = session.get(sitemap_url)
    soup = bs(response.text, "lxml")
    locations = soup.select("loc")
    stores = []
    for location in locations:
        page_url = location.text
        store_id = page_url.split("/")[-1]
        if store_id.isnumeric() is False:
            continue

        stores.append(
            {
                "page_url": page_url,
                "store_id": store_id,
            }
        )

    return stores


def get_api(store_id):
    while len(store_id) != 4 and len(store_id) < 4:
        store_id = "0" + store_id

    url = f"https://www.bbva.es/ASO/branches/V01/ES0182{store_id}"
    logger.info(f"URL: {url}")
    querystring = {"$fields": "indicators,closingDate,address,schedules"}
    response = session.get(url, params=querystring, headers=headers)
    logger.info(f"Response: {response}")
    try:
        if len(response.json()["items"]) == 1:
            location = response.json()["items"][0]
        else:
            location = response.json()["items"][1]
    except Exception as e:
        logger.info(f"Failed: {response.status_code} , ERR: {e}")
        pass

    return location


def parse_json(location, page_url):
    data = {}
    data["locator_domain"] = "bbva.es"
    data["store_number"] = location["id"].strip()
    data["page_url"] = page_url
    data["location_name"] = location["bank"]["name"].strip()
    data["location_type"] = location["address"]["type"]["name"]
    data["street_address"] = location["address"]["name"].strip()
    data["city"] = location["address"]["city"]
    data["province"] = location["address"]["geographicGroup"][-2]["name"].strip()
    data["country_code"] = location["address"]["geographicGroup"][0]["code"].strip()
    data["zip_postal"] = location["address"]["zipCode"]
    data["phone"] = location["contactsInformation"][0]["name"]
    data["latitude"] = location["address"]["location"].split(",")[1]
    data["longitude"] = location["address"]["location"].split(",")[0]

    schedule = location["schedules"][0]
    ooh = []
    for sch, day in zip(
        schedule["days"],
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    ):
        if sch == "1":
            ooh.append(
                day
                + ": "
                + schedule["fromDate"].split("T")[1][:8]
                + " - "
                + schedule["toDate"].split("T")[1][:8]
            )
        elif sch == "0":
            ooh.append(day + ": Closed")
    ooh = ", ".join(ooh)

    data["hours_of_operation"] = ooh
    data["raw_address"] = ", ".join(
        [
            data["street_address"],
            data["city"],
            data["province"],
            data["country_code"],
            data["zip_postal"],
        ]
    )

    return data


def fetch_data():
    stores = get_stores("https://www.bbva.es/sitemap-oficinas.xml")
    logger.info(f"Total Stores ID: {len(stores)}")
    for store in stores:
        page_url = store["page_url"]
        logger.info(f" Page UEL: {page_url}, and StoreID: {store['store_id']}")
        location = get_api(store["store_id"])
        i = parse_json(location, page_url)
        yield i


def scrape():
    logger.info(f"Start Crawling {DOMAIN} ...")
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(DOMAIN),
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
        location_name=sp.MappingField(mapping=["location_name"]),
        latitude=sp.MappingField(mapping=["latitude"]),
        longitude=sp.MappingField(mapping=["longitude"]),
        street_address=sp.MappingField(mapping=["street_address"], is_required=False),
        city=sp.MappingField(mapping=["city"], is_required=False),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MappingField(mapping=["zip_postal"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"], is_required=False),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["store_number"], part_of_record_identity=True
        ),
        hours_of_operation=sp.MappingField(
            mapping=["hours_of_operation"], is_required=False
        ),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=1,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
