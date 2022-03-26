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
    "tsec": "eJxtlMlug1YARX+lyjZKHjNYSiI9JmMw82S8Ax5mnrEZvr6p1FZddHWlq3OX93x5c5b+cUHfbyil0CkhyI+YYogP6pFlHwlNsR8kHScoxSmCwZm3P4Jsmsu++35r+jRu3n6+pC6d9mH57WCT91O5FO2PKLkZyoDAC8DSBJe2YoTKLv8C/wd/CeVQZJMYL/EPsU6i34gILxWo21CQgS8HqSpcMi6Yi2dF7od4j8envz9TidNtVxHmqnkaLQY4u7sZWmDaXq/T4xrBVrCvD/W6WWHYdrUsvLDYqPntUc6weWgVmkEEqTvb76VEKr2Or7S1sBMBLNUN/Y7WX4nm24AYiLPBCpKilYyGXzrjRcLiSTC5E8bVpLA05KZhqta9n9ANnW9qYwXXNZIT0jNaUn1nvGgZ4uGqZVfVoN89pqk3yue3ZGic5MUIZhzOmILp3UhRalxJwantOn0t3gmgulybX1kf9scmy+B9CbrJdB3XIS+ZRmO8YkVVAdLo3eh2ocFxXqFyC9fbeeAQtYnjmifj2pRB+hSd4cDLTYCnFzRpuoNS5Z+5mOXbO+ojvM3UvoWM6a9QbR9OAkhsuOKZBHtSjS1hp/1NwM6cd4WAILctQHNSvCLfbhriPL/amgdVWo592qXFvSNvw4vb6Fg+9dDhYe9iGfk+t9gZrFFjFyS0ypAj0BBYwtodKCdWsDtYreAnIBWUzfhbfZu7NS5wgWoWr3g0S4TR3GmB2mPt9YtNpXjHKXLjkqwqINOO2BbERQ0rVsZA6boHMSY5L5/cJmufARcRqcHAk4l0Y8alcqAJuEgUfDX3k9Ra82WSzNTJ6fZwMMUfQgYTEcbYNoZusvuksqupkl4w91cmQSMTwnF86CVDaGFUwdA2xukCGB8lxORdnBV54zCtFjKH4mlkJaFdiXlTcAMr6lJI1Q4D93NlpCsnDtzlfCCymQKaIQ780OvnSXLXQWhFx4/c/tJNmFNa4a3JgNUGe83bYaHd2PMzETtTMvGWPZjNvjOPa4rxmr6B5DgljYbRRl9fwXhnhpv24th9KM+4PsHq7oQ9TrS8wu92YVO7AiRyEvBspDCarpsLh9J1qnMTlm3CGntyzo+Uz8zmRLBUcZoumxMBmwo9SWi2F/awPFxXvOk3JXq53Zb09wEOsdoojdKgrnoSCs9gL6h0cjdRxsT9QpCKYomZ8N7W18OY1qXD5Ht2bMjOi1gu5sMUVs95EWGerHrs9mtVcpx+Y70p//7+Av+RxN/C0LIdNmU8/zRzkryyz2H6TMvHFH8uv0b7TJs4xf+Z/Yt+gb909/Mnbh2nhA==",
    "content-type": "application/json",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36",
    "sec-ch-ua-platform": '"Linux"',
    "accept": "*/*",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.bbva.es/general/oficinas/valencia/valencia/valencia-dr.-waksman/6507",
    "accept-language": "en-US,en;q=0.9",
    "cookie": 'BIGipServerpool_BBVANET_GLOBAL_SSL=3390679232.47873.0000; PD_STATEFUL_3a49a738-9f80-11e4-a39f-005056b6703c=%2Fgeneral; sgSegmento=tcm:924-36738-4; sg=tcm:924-125242-4; AMCVS_D906879D557EE0547F000101%40AdobeOrg=1; s_ecid=MCMID%7C67664485597827215681492018936442767806; s_cc=true; s000001=1231434506.29735.0000; akaalb_ALB_WWW_BBVA_ES_ASO=~op=WWW_BBVA_ES_DEFAULT:PR_www_bbva_es_TC1_NG|~rv=72~m=PR_www_bbva_es_TC1_NG:0|~os=733dde66eb673392daf02439bd6f3465~id=fc597b4c0069d4e87c879a48c660b673; check=true; atc=4; aceptarCookies={"version":5,"publicidad":true,"analitica":true,"personalizacion":true,"tecnica":true}; _gcl_au=1.1.55668256.1647950091; TLBS_B01=0000UE6MJIthIzrFI42itXLxZLT:1chiv3pp6; refInterno=https://www.bbva.es/general/oficinas/guadalajara/marchamalo/marchamalo/2951; s_sq=%5B%5BB%5D%5D; lastPageAEM=https://www.bbva.es/personas.html; AWSALB=zuMmVFELwRrbqfSCUgQrklujtm0kYCPk8oNQZHrwUItSXFGP+XBiZlvKZFdjC8W+Xf9T55y7IJ7j/yTt0jb2yfiMhdtYXNGOOYuF53QkxYncEuKwuv34DXhUsPId; AWSALBCORS=zuMmVFELwRrbqfSCUgQrklujtm0kYCPk8oNQZHrwUItSXFGP+XBiZlvKZFdjC8W+Xf9T55y7IJ7j/yTt0jb2yfiMhdtYXNGOOYuF53QkxYncEuKwuv34DXhUsPId; _abck=4D19A13673667B6670602274A54650DC~0~YAAQUEo5F8Bs37R/AQAAt5BlxAfEdEc0ucsfDwlm3hIzPGg5vGUUvhKpkMvBLTBJxUYsCjSFPj0WQWOrJaeVZgdEWce7jz8uQws9dPYtEROxDhXzHV6Nb9a9gZtSiTDxuLCfo0oLMQYXI0FHTlDuD0zp8Rx72adLpEC3araM0Q72ygks73w7meoaor8mPvJgQS5xDZB9XBeWYlQwYnq7urJmgZSnEcC5pfsOfsipjEk8nB4L3kYaFSXq8L5MuvF8lR3o/KmFogOdc0KlKD6gu78/qdChg/oU6Afzm5hGpUKi1KDMF1LmESjPxzK14gjH3pbAwRW5YrtMTYEKV57JshsTSJFOtIHn0I0lJKYnRLJHja5xGuyJRhHsJpQrTne1/cXcCmqZOV2jplmTUfc5DqsVuqM=~-1~-1~-1; bm_sz=4748869061E1CE3293505FE2B0DEA872~YAAQUEo5F8Js37R/AQAAt5BlxA9N6Bsv2QeCUIhp4sGAxxU8cHTi5NplYVGUGi6TSJ+0E+5q0I+OVnS5wM5opqiQ78Pri72qYDFUuEr4d45qCUn0JfmASP9t1SQICqBnaTOZ6LpWpW3s/szpMp++5owzcDQqMqej1PCjDb0Wn8l+HxDZsO7g56hD5eB1KLBnvaFkSmregz6rhhgEzafKm1PPJx421CQKcJkX9TPtWkVsIJCsrFg8i+ZnQ5yLqpU6RWPI+YYnOBSK0A/QE9agIrPEPl0fm4dNPLur/CKsZE0=~3490865~3486530; mboxEdgeCluster=38; ak_bmsc=48FFE2705F6C01C68B2F7A91ECDE79E5~000000000000000000000000000000~YAAQUEo5F+Rs37R/AQAAJ5hlxA/L7RrzTY/9lzE7NVCNGcPmxafXuZP/nSOHSfxdXaJyhqNPfsrSSLK1CwJCpIcnKwfeZXis7wlM9xTDxbaWN81BiSXBGUdSLTZVsfsiL9odTBSFSnb3emhdSDAAeK5ASJHhhg29QKkyRqVXhx+oHACE+Okx1WUkvm9XpczcYV76e7SMFPY6gChZbdOW8ysLvw0iILTLsGZJcOv65+2K6eNbEOULxnx2m9I+Xvm5W5MxcvfI6poFWn3Rqk9H5BuC4HgRn8vNOdoQjxxQiUx9yWlliWrKxnP27xoI7FMA7PG2ZrbNXTMjfHQ8uPlAvOZjaaR1CDw8QAphHznDLJ5hcOYWKaufQfL0JKqt5+4GA/o2bMSE5oIQjFSsbxeAAM2TC6UGM7QdjUi7OI1MAgzX8kLSVCckamq5GYjr590iWrjU2Wk0lMsgwkgL8DfYdC5wI8LFT61etMteQUfRxNEK+yKp263W; gpv_pn=escritorio%3Apublica%3Ageneral%3Aoficinas%3Avalencia%3Avalencia%3Avalencia-dr.-waksman%3A6507; gpv_url=https%3A%2F%2Fwww.bbva.es%2Fgeneral%2Foficinas%2Fvalencia%2Fvalencia%2Fvalencia-dr.-waksman%2F6507; gpv_pt=informacion; gpv_sl1=localizador%20de%20oficinas%20y%20cajeros; AMCV_D906879D557EE0547F000101%40AdobeOrg=-637568504%7CMCIDTS%7C19077%7CMCMID%7C67664485597827215681492018936442767806%7CMCAAMLH-1648872268%7C3%7CMCAAMB-1648872268%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1648274668s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.1.1; mbox=PC#03bc185b8c7142549b611c7779c48fd9.38_0#1711512275|session#db75e4344d744c659c03130594af8b4e#1648269327; s_nr=1648267475220-Repeat; utag_main=v_id:017f7c9254f70003653a8467e22d05068004506000b80$_sn:8$_se:3$_ss:0$_st:1648269275856$vapi_domain:bbva.es$ses_id:1648267467236%3Bexp-session$_pn:2%3Bexp-session; language=es; bm_sv=1EC6D0B80AD0D1BA94B213A6931E310E~qtlj1CFluKzvOu4S9cwZcF2ZoEPM3Glc9KtAxqQtZNuu/NvJUyOHqqiXRWwApvhd9Y1vLAbgWHZR15Lyrl0OMw1Q+OO23TGl4MUPCdPfBhK6u8u/KfwCy9GVjVkR8YZRfhIwW1Rsl96MPmUOTPbSzA==; headeralert_header_donacionucrania={"version":1,"saturation":9999,"counter":15}; _abck=4D19A13673667B6670602274A54650DC~-1~YAAQUEo5F5pE37R/AQAAbYlVxAdajvDvsEWF8YHq4doEns116oAhmzKYDCcov6XEghtVFypYEm1J22+CKkVngWzDVEJhznHZD6+vusbH3zEiElOgvQTbgdzbyk5TIlY1PeCIbKlxNbDMF6n4qvg6YLUbKUhX1qp583Hn4jf8B4FjGeqxru9q9I2JY0h6qQLlglPWZaGKhGVO/Li/ih+MK1i+f8Fhn55qXbQ66+FYmoDgA0BdIXbyanOv5zey4wNWOvMJrLnwBUzwH4Zs6o6F6EXMam3ttdq5Mz4N2vHpr54sDKcy1CiRiQq8IID7z0o19sa0dBK9fAFYWSH75EPUl3bP7HMA2lesxofmEblNgeTOEQYOhRXFQIET~0~-1~-1',
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
    data["location_name"] = location["bank"]["name"].strip()
    data["location_type"] = location["address"]["type"]["name"]
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
        log_stats_interval=1,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()