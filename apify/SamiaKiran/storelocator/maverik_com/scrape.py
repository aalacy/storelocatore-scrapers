import csv
import time
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("maverik_com")

session = SgRequests()
headers = {
"access-control-allow-origin":"*",
"cache-control":"no-cache, no-store, max-age=0, must-revalidate",
"content-encoding":"gzip",
"content-type":"application/json;charset=UTF-8",
"date":"Tue, 08 Dec 2020 15:07:32 GMT",
"expires":"0",
"pragma":"no-cache",
"server":"nginx/1.19.1",
"strict-transport-security":"max-age=31536000 ; includeSubDomains, max-age=157680000",
"vary":"Accept-Encoding, Origin, Access-Control-Request-Method, Access-Control-Request-Headers",
"x-cdn":"Incapsula",
"x-content-type-options":"nosniff, nosniff",
"x-frame-options":"DENY, SAMEORIGIN",
"x-iinfo":"14-23166273-23166274 NNNN CT(62 152 0) RT(1607440051131 0) q(0 0 2 0) r(8 8) U2",
"x-oneagent-js-injection":"true, true",
"x-xss-protection":"1; mode=block, 1; mode=block",  
"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
       data = []
       url = "https://gateway.maverik.com/ac-loc/location/all"
       loclist = session.get(url, headers=headers, verify=False).json()["locations"]
       print(len(loclist))



fetch_data()
