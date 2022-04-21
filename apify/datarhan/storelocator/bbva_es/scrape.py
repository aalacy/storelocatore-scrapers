# -*- coding: utf-8 -*-
import json
from lxml import etree
from time import sleep
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()

    start_url = "https://www.bbva.es/en/general/localizador-oficinas-cajeros/index.jsp"
    domain = "bbva.es"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    hdr = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "cookie": 'check=true; atc=1; AMCVS_D906879D557EE0547F000101%40AdobeOrg=1; aemOrigin=live; s_ecid=MCMID%7C80331019266710234502620218857489829221; AMCV_D906879D557EE0547F000101%40AdobeOrg=-637568504%7CMCIDTS%7C19059%7CMCMID%7C80331019266710234502620218857489829221%7CMCAAMLH-1647259080%7C6%7CMCAAMB-1647259080%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1646661481s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.1.1; mboxEdgeCluster=37; gpv_pn=escritorio%3Apublica%3Ageneral%3Aoficinas%3Acadiz%3Acadiz%3Acadiz-ana-de-viya%2C-3%3A3226; gpv_url=https%3A%2F%2Fwww.bbva.es%2Fen%2Fgeneral%2Foficinas%2Fcadiz%2Fcadiz%2Fcadiz-ana-de-viya%2C-3%2F3226; gpv_pt=informacion; gpv_sl1=localizador%20de%20oficinas%20y%20cajeros; s_cc=true; s000001=1248211722.29735.0000; akaalb_ALB_WWW_BBVA_ES_ASO=~op=WWW_BBVA_ES_DEFAULT:PR_www_bbva_es_TC1_NG|~rv=34~m=PR_www_bbva_es_TC1_NG:0|~os=733dde66eb673392daf02439bd6f3465~id=0c5c8f7c26d8f2b2d9c7309ca1c83eb8; aceptarCookies={"version":5,"publicidad":true,"analitica":true,"personalizacion":true,"tecnica":true}; s_sq=%5B%5BB%5D%5D; _gcl_au=1.1.772000692.1646654503; lastPageAEM=https://www.bbva.es/personas.html; ak_bmsc=D67C3B757BDC237F124181440E3CE318~000000000000000000000000000000~YAAQfo4UAu8mh1F/AQAAcIJTZA+ekoyCPvowAkiEFRJISHsbS6pI3C66q9hzmJ3MnPC1CbqiHiELmUV/g2RZfQrRpCj40t2EterVghNDPJD5+akkNfqdfWFroArzqQZtSCzZWL3eKHMWxgI5Ywz/51V1IKLzznOATR2kUVEOEHEpmcV84jZPMqmBIlTfxpTftFmpIU6iRQdxr8fHqx+piNPs6AcLi5AbOh2yle0dEHX3TLCumi+OxlZL0A2Ku24A1u4hEEn+bAdSXPKtHQBlJZxwdMYvnBzDaGa8gSp7TbVOyaLgeVhMWjoIXr3m1om6UV06UB1DRaBAacMAIFIc02Cywn/XcjjV581SbbC1ES+BoQFyOhQ=; bm_mi=8713B14876DC5B6EE945FA20409266CB~GH593eC7d3aMe5y7ABb/de2T5KgNHqNevlEgwA7qLsvMF9sPgEWxyyyuj6H0sl66fOwCPJvEu4flul4CjCnTb84qANGHpkmyRqnYgaPHaR48n5MNCEtiSmIvaxsWJUbTcBcBJYng6sdUKJiZ2CoqC6txLKjnXKx63VS1l6Cq9OsRgPGSFWfZTtClXT4QSSuk4QptCkA6kUnEoWHeSX1nSguYTpAFq2MeVBpkX+PiQpqAe6R0J/XpD8aNo7cF+uwnRYK4sStH1CVGeGW1isZGTvpG/3V5hd9GSsBv6HfjwO4QU3m7WU7scMpmO85yD8a3; mbox=session#d1685e94e5344d3d8481e333a862ceaa#1646656141|PC#d1685e94e5344d3d8481e333a862ceaa.37_0#1709900470; _abck=921BAFA347845363060756300579110E~-1~YAAQh8URAol4Olp/AQAA/4hTZAfsyzgZQt1K+xqf0ar/OdJUo9j/caPkq/Z20W6Hxvq3d3QtW/RA33KQVrRPTrWBRIdfNaS44nnHgfoGWcLLgKhpythpOQAxEm+qHknlya+umQYMKI9rCc30KlnTWkGx4MX1sSMXqZDB72K6AYoa+u8/ISwKTn+t82OoI618UgHiwF9wCc5r14YZzA02FF5VXLfYAqljGCQlgFefhIsfAug5SIIMobwpQMleAu33REEotFwa6wRXUr5QogYJ7+I7G73qxOSWUYKXHCX45/uLOu2SB6CuTf45UjZbdH8+iAiVfVvHXYH39gcApjX1pO1FHVu5Q2cJR24FUMC2rZRmArcfXa4zxJU=~-1~-1~-1; bm_sz=04EFED7F9D143B74E322B6BF74BEBFDC~YAAQh8URAoh4Olp/AQAA/4hTZA9vVwXdTGc1kSHn8HKNuQ7wzMfEAq8nzwo/LnoysS5dwKnZ4LmCyhQurOdZhJklTZf1cvai2BWa5g2V57jElilcGl1o2M6LSJuyLIOtCe0uYP8t/fJjL7GT0+osdZKjxf417ivai1TRrDczwSPvFBQDNbFUMyrS6zWx; s_nr=1646655670922-Repeat; language=en; utag_main=v_id:017f643e547500b12bbc7c4b0af005079004d07100838$_sn:1$_se:6$_ss:0$_st:1646657471774$ses_id:1646654280823%3Bexp-session$_pn:3%3Bexp-session$vapi_domain:bbva.es; bm_sv=97335CF6F761FC7A1241D16A6FCA0585~mYStj/LfDu2bOMd6fuvt5at9X+kvCsEc8YVgN1n7/e4xaVLg1ewW/7YPpNZdZL2J+ucXvJMrNrVB/kRpBYMLomtv/opmh3bwDgASPbM4j0JoPwh37YewGwbMsYhV6wzS7Tux9qRopkUfmFbO0amXTw==',
        "pragma": "no-cache",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "tsec": "eJxt1EePq1YABeC/8jRbNAMXUyXPSHRjmjFwMd5E9F5MMeXX50VKoiyyPTpneb6zO6XxLzX5/sgAniYsSXySYUx8EiDFP1mQpZ8YDpKIOoUhGTMfv2A6TmXffX+AP7CPn7PUxeM+zL8Trsn7sZyL9keUnDRJUYEX0JsmOOQtTJKyy8/o/5XPQjkU6SiGc/iDr6PoNWICygtn2Jwgo54M46ugpgyciqU67Yf4DF+Lty+xxBi2cxGmqlnMFkMZu3uYGrRstzfI1xpwrWDr2VXfbsGsaW8OcEwNYOSfAg09XdH5QQ/6beHtB9OlBoSbt9Fr2Knoe2BfPC2aFn1ZA5QVG3E5rfAiU1cz1/QGoiTnA5Yc0A1TufphLosnCnnkKr5D5nvMk8zcS0Q/9vmGz1bsDasFcUyb8oAdrZqwzE1fls7Szbt9yt/zjqnIaRD7q4zc2nft7gcRsCCFlUPzul5B13m7MjMNXdeHajCnmnR6qpaiO1oqgzEoujp3Cnqx9gAT3vpzuHJRWz2fekFwae5oXHCSFf4BhO2WmCuGZbrrPS2AWeoN2GFfEe5eIJMVbzsz9EfQtu263cfZV2Oz9wrnlehN1ImTfJ/UsELGXLaBIzaVKc3Ym+/JPCR8rWbbI96wq+PMJ74M9Gy4vJQuIAjKYPyXJtA8cror6EtU4hreFqqpA0wpG1Wvm9VgGk1lMV6NZL6iOYcgSpRsna2CENR7LlF2K8YFHXW2tJswou499rY4tzXiNhIDwTeDTQJ+7lLJTMZJF25Izc/a9UXc7dlQO7s0iunR7ineqiyX+0KPrzLmEEPLLPNqZqYZAErHYeRIrdSVBSfrQeODaYyYBO9nGnhkBIRKpvad8h0xrnjHcMSJ24KeKyKLUHfHrXD3cmxPddYinc/F+5GggwxXZXop7SsvcO/xLB/uKhpv4+D9CykgqTULfq3TCbWHzcqsyHUYlff9nqQD6b8YeejGDD1i7IXhkYIcaU0/42nR3FhOoHAZkgF0el1Snv2onhLs3J30r0kC5DJ15hSA22NAlkzSCQlhDZM2sO7GB/KoO41nU3KOhoeW5lnlBxeRBqLvq04IqXSinQfXqifHSrnMYNXf/4xgpeYKlW32cIGsyEi3ywFXVndy8e2RhmwU9tWDFjJkkbk24+oXa18GCjq2cqz3r+QuPB5WifSKrlkLR5UHDhsNWSq+FrJAH/28QKpmqifkxnW5oiajCzvO1LmjoIctE/ulqrRjyvPv7zP6HyT+BkNLd64pw+mnmaLonX4N41dcZmP4Nf/27Ctuwhj8M/u3ekb/wu7nT66hqZE=",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.109 Safari/537.36",
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_cities = dom.xpath('//div[@class="datos"]/ul/li/a/@href')
    for url in all_cities:
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        all_subs = dom.xpath('//div[@class="datos"]/ul/li/a/@href')
        for url in all_subs:
            response = session.get(urljoin(start_url, url))
            if response.status_code != 200:
                continue
            dom = etree.HTML(response.text)
            all_locations = dom.xpath('//div[@class="datos-finales"]/ul/li/a/@href')
            for url in all_locations:
                page_url = urljoin(start_url, url)
                with SgFirefox() as driver:
                    driver.get(page_url)
                    sleep(3)
                    try:
                        driver.find_element_by_xpath(
                            '//button[contains(text(), "Accept")]'
                        ).click()
                    except Exception:
                        pass
                    sleep(2)
                    loc_dom = etree.HTML(driver.page_source)
                poi = loc_dom.xpath(
                    '//script[contains(text(), "PostalAddress")]/text()'
                )
                while not poi:
                    with SgFirefox() as driver:
                        driver.get(page_url)
                        sleep(3)
                        try:
                            driver.find_element_by_xpath(
                                '//button[contains(text(), "Accept")]'
                            ).click()
                            sleep(2)
                        except Exception:
                            continue
                        loc_dom = etree.HTML(driver.page_source)
                        poi = loc_dom.xpath(
                            '//script[contains(text(), "PostalAddress")]/text()'
                        )

                poi = json.loads(poi[0])
                hoo = (
                    poi["openingHours"]
                    .replace("from", "from ")
                    .replace("to", " to ")
                    .replace("Closed", " Closed")
                )
                store_number = poi["name"].split()[-1]
                while len(store_number) < 4:
                    store_number = "0" + store_number
                poi_data_url = f"https://www.bbva.es/ASO/branches/V01/ES0182{store_number}?$fields=indicators,closingDate,address,schedules"
                try:
                    poi_data = session.get(poi_data_url, headers=hdr).json()
                    geo = poi_data["items"][0]["address"]["location"].split(",")
                except Exception:
                    geo = ["", ""]

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=poi["name"],
                    street_address=poi["address"]["streetAddress"],
                    city=poi["address"]["addressLocality"],
                    state=poi["address"]["addressRegion"],
                    zip_postal=poi["address"]["postalCode"],
                    country_code="",
                    store_number=store_number,
                    phone=poi["telephone"],
                    location_type="",
                    latitude=geo[1],
                    longitude=geo[0],
                    hours_of_operation=hoo,
                )

                yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
