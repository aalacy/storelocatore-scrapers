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
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "cookie": 's_ecid=MCMID%7C67664485597827215681492018936442767806; atc=4; aceptarCookies={"version":5,"publicidad":true,"analitica":true,"personalizacion":true,"tecnica":true}; _gcl_au=1.1.55668256.1647950091; check=true; AMCVS_D906879D557EE0547F000101%40AdobeOrg=1; s000001=1281766154.29735.0000; akaalb_ALB_WWW_BBVA_ES_ASO=~op=WWW_BBVA_ES_DEFAULT:PR_www_bbva_es_TC1_NG|~rv=68~m=PR_www_bbva_es_TC1_NG:0|~os=733dde66eb673392daf02439bd6f3465~id=1f427330d4acf30613dc3ce3e22fccfa; s_cc=true; lastPageAEM=https://www.bbva.es/personas.html; _abck=8289A29B3705BE985A97CEBB60B092D4~0~YAAQhTkgFxos9ASAAQAACyn/HAc1X5IV2VAL9+py7q2fwjVlcSfARgsKFOcoZ68I4uR01jq4Dwwu3VVsF6NQ7goRqEQorLdX4zVjP+PEuv8ajQQUYG8BauA4PVRqyEbm35eqxZ2G5OLC+Rt0BGUbRSJbp9zQ9+h9XIIY7/sEobsPIM/P3Lf4Ku+VX2aT87cEKzzKPLRZ3Prep7vMXLR4qdeAQbvnWT6LAea+zWdgmJH4q3KFF35YQ2zlvt2+ow22EDSGijK0QS/Bhp9UFmGtfXRaPIisQ6U3uJ0k1Ziypu9VYGKAkWs5bp5kfeNdXDvSFhe3fMaZvRMEySL3HU0zwWYcLSC4PpB5uW9VUVeK6TY6MFIJA7dijm4bCOSNy30DRU6NOq3ucAFLungMOKxVzr5mNzE=~-1~-1~-1; bm_sz=04A5F08435D7E47FC365314B6868EDFE~YAAQhTkgFxws9ASAAQAACyn/HA9kTomTlaVugBuh6vhy1Am2LiVUdlpg0CgwMJbH/jL9IoN0ly7RdewhHGD1tEdks6A7A8rjyYL3NLGy9joyOFTlgnakIr6gmXa7b+qKZyqMHuhWNmU00ydTf4XV00GcgdtLQv5ru4QJ8kYIBrJb1h7WyUrwIfuS/zl0bcsMTWhQvK2lV+v02xN7b8lF86sXc0qIlfjPxH62WyRfygLbdZDcLydxTMuvm1wIyqFGzhzx8jYUaVXezxEQp1CsbhzxAXkHORbLsKWOTyY/mJQ=~3359285~4277556; AMCV_D906879D557EE0547F000101%40AdobeOrg=-637568504%7CMCIDTS%7C19095%7CMCMID%7C67664485597827215681492018936442767806%7CMCAAMLH-1650358729%7C3%7CMCAAMB-1650358729%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1649761129s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.1.1; AWSALB=QkO6edRU4hVO7ccBrLYYidl4HlPxx7nSVTBiJyAB0CiTK9tz7j4RvX6sYouFeiselhr0eRUosWD96tNjJ3WfGBxtUNXuy5e4msmoxDnBzpNwsCKVPuL3aECspcKd; AWSALBCORS=QkO6edRU4hVO7ccBrLYYidl4HlPxx7nSVTBiJyAB0CiTK9tz7j4RvX6sYouFeiselhr0eRUosWD96tNjJ3WfGBxtUNXuy5e4msmoxDnBzpNwsCKVPuL3aECspcKd; utag_main=v_id:017f7c9254f70003653a8467e22d05068004506000b80$_sn:17$_se:1$_ss:1$_st:1649766545719$vapi_domain:bbva.es$ses_id:1649764745719%3Bexp-session$_pn:1%3Bexp-session; mbox=PC#03bc185b8c7142549b611c7779c48fd9.38_0#1713009546|session#1e410ae78bc042faab073ea081dac39b#1649766606; mboxEdgeCluster=38; ak_bmsc=3B386F3D3F032471FFFF93831FF32E76~000000000000000000000000000000~YAAQBWU+F4ujRwOAAQAARUakHQ9TEP20uu2LnmJrsxYEPUuepAFzl5dUskcsGUOU0b9UafEXDhtxlk4oicp721baI34XvE48r9B65wX5gQUjOO6XtW2FwRvjORkirsBXshFg59QBo0CRRQHA5JyvPxgIoNy5dlr1cm6UTZJXhAtgrrGiwvkbA8cXF4eRr1kAR9QPC48eLeT6t9Fd9Nim8ecQ/gOGnEUXUqd5DS51xnnpCW/hWW8xOJd1qGJXsuXZYhTazdTqPRh6nFi5vOpPBJTuiTp/LAXcw+CtHDRKGR3s4BUfz9ekgpU0FkSp5oajjzs77jWJMI543Qd8YSmEdn0tZu/NMOEFyaCEpjC2u1gMJsCZwnnBTZ1ZH5eVkfEWsnTtRbwYxqXH39NL/rOOYSYb0I4WiNri2g2nYUmDaTBHG5JitLpGfdHnQHd0smCgUd0goPgf26gihvHlaEemjVadtfvUu18Ag08+; headeralert_header_donacionucrania={"version":1,"saturation":9999,"counter":47}; s_nr=1649764747146-Repeat; gpv_pn=change%3Apublica%3Ageneral%3Aoficinas%3Avalencia%3Avalencia%3Avalencia-pl.-san-agustin%3A6502; gpv_url=https%3A%2F%2Fwww.bbva.es%2Fgeneral%2Foficinas%2Fvalencia%2Fvalencia%2Fvalencia-pl.-san-agustin%2F6502; gpv_pt=informacion; gpv_sl1=localizador%20de%20oficinas%20y%20cajeros; bm_sv=7F2248150D8EF335C2AF0E4891550D52~vyxg7OBlLo0D/By4OCX/w2YPXwWvIy1f5mP7JdPV2Bn70s2vBeoEoMJXSNxvR9wou7q9uWUYiPtje9L9POx8LHG1lsZgmZ0wmABB1aOWyEhZVsfHO3MhkRyQ62HasIPypEuSufqs5s7YgK/ZUiWyVg==; language=es; _abck=8289A29B3705BE985A97CEBB60B092D4~-1~YAAQBWU+FwMlRgOAAQAAuGofHQdl6rj/3ZWct29KwPyOjcZlJO8hggKauSoe0s0NEE7CSCzfSalbRvqcOPesNzCPi4boLR8QUIuXMmHE2YWzL0v+vkNTfy887ZYDN8j+ZLJsI3ifbxvI/0nQWrG/z1SXUxvbtAHFfMdX53udmrjd6ltoEpjVQexz86LFoul7qPlT7fGnccWx89c0vE4D4bg1QjgwnSnSAcIVoakgABCc1JK4k6Y2J4AuHeNSUFBJtv9CEvlUMg1M+svCZol84zIJvQ3M3n6b0xw/zVxfkEgCoRiCa7qDCtbbYqEWV7Y5gGf3Sl4vtsZnZ2eGGzed+rcHsIcTk0FJERoTxKBrkrNEKjIUkqo/xY5OGJEd67oe4rNiB0uP9VdRb979fSfjtZ4SOec=~0~-1~-1',
    "referer": "https://www.bbva.es/general/oficinas/valencia/valencia/valencia-pl.-san-agustin/6502",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "tsec": "eJxtlDdvw2YARP9K4JWw2RsgG2CVKPZeto9VLGIXRfLXxwGSIEOmAw7vlhvexVuK7A8l//5AWTQHWIF8lgxCfRJUVn4yaIp8kigJ8iwjU5oGH38ExbzUQ//90Q0Z6D5+LlKfzce4/nZcVw1zvT6eP6LkFnkBC7wAW6rgkhbI87qvLvD/wRehHh/FLIIV/GDvWfQ7MUfrG6fbnCDDvhxkd0EpmGB5vBr8OMUETC//eGUSo9vuTVia7mU8EZix+8hQA9P2Bp2c3jH3FGytvGu7lZXBRpBMNC9vvli3UMeg4zQ3M3xIqX6bxgZniKxatk5yoZBWWdXNruowLTyxncTW2i4RGxJDLLdutsjDUSyPdcRnAw3jKclH7jUY3beyqD660quQzvKag+jW5ZyGad4GChsEOKeDV1c/LSNbl1o4RcOfkZci5eFhPIHQb68FCKR/pzI/cMX6lfEgbCsEeKvL4zTKWTRbq2Y/tkUU5NOt0wwPMzG8aAPMAI2APz3yjbkIERh27ror2JWaJWyV81hPqI9dA+viv3aYtLlISUVk41MpZjB2zEiFk+9VUmiLlghKN7/pY4gcPgJmEKLgGSRH0uZ7pQt5Y6exSK9UPW9ek018CQzEJB+DFZkqDe2P26mYOOHPFfEKdwyPgvbNo4kMSg5rfGRU9+76egoGG3e6bHmRyGacw9HdkKM8nLm3QGtnMUdqdXxq11VnIMhbeUlMOYEaQnEYs7cTN2EYCzan14FynP7z6kDluu1ciHrTpGO6LSwZyFp/8LY9ubpQrsoKbm8Mqk54r8tvTIOXR7K3FlvivbweUwNLqFvLys2eHK73NdN6Y0J7ek3pOzS0yLjsqI8o8BRjS2dqfhj6UO3QQD24+XhDmENKV4q5I+YtqRtS3NWuzUJkdK/d1peLf0bJWd90f7qKcKqNE84kRi6tkG4AaeCceCf9DV6YFRfRRGesLTPmjD8a+bn1OoWavaCNrrrWYGnOYNscOw/ifYd4/s2GVwqs0aRNXUAQ8AbjWDWTSaXZexI+fuO5OsehpQjjSSQwh1cCxXZLywizyNDNpnUgYFTZj/eIHOKGrmm/eVNHvPSVOw5uy0whmOAYOq7BlJpHlXvKul+proT2VDnvWMcKZ8TeQqnG75aTYMixh1R+q5YhZtE2Xh+0u9ueXoGZv5LV1EWnl4d2yT4cqCGv+KrM951P5Dsj4H2f2sOYHlidFSmEXpsqGNwnoXnKAiXueYQOc3exqvr+vsD/kcTfwlCLg+t+//npljTdiq9x/srqcgZf66/RvrIOZOg/s3/RC/yX7n7+BFdJrHU=",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
}


def get_stores(sitemap_url):
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
    data["location_name"] = (
        "Oficinas y Cajeros BBVA en "
        + (location["address"]["city"]).capitalize()
        + " — "
        + (location["address"]["name"]).capitalize()
    )
    data["location_type"] = "Oficinas y Cajeros BBVA"
    data["street_address"] = location["address"]["name"].strip()
    data["city"] = location["address"]["city"]
    data["state"] = location["address"]["geographicGroup"][-2]["name"].strip()
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
            data["state"],
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
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
