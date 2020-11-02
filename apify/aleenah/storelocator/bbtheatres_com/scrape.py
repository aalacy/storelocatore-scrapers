import csv
from sgrequests import SgRequests
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bbtheatres_com')




def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()
all=[]
def fetch_data():
    # Your scraper here

    res=session.get("https://www.bbtheatres.com/theatres/") # not using because phone is not available in itt
    #logger.info(res.text)
    #logger.info(re.findall(r'"CinemaList":(\[.*\]),"experiences"',res.text.replace('\\',''),re.DOTALL)[0])
    jso = json.loads(re.findall(r'"CinemaList":(\[.*\]),"experiences"',res.text.replace('\\',''))[0])
    logger.info(len(jso))

    for js in jso:
        zip = js["CinemaInfo"]["ZipCode"]
        if zip == "":
            zip="<MISSING>"
        phone = js["CinemaInfo"]["Phone"]
        if phone == "":
            phone="<MISSING>"
        lat = js["CinemaInfo"]["Latitude"]
        if lat == "":
            lat="<MISSING>"
        long = js["CinemaInfo"]["Longitude"]
        if long == "":
            long="<MISSING>"
        all.append([
            "https://www.bbtheatres.com/theatres/",
            js["Name"],
            (js["CinemaInfo"]["Address1"]+" "+js["CinemaInfo"]["Address2"]).strip().replace('u0026 ',''),
            js["CinemaInfo"]["City"],
            js["CinemaInfo"]["StateCode"],
            zip,
            'US',
            js["Id"],  # store #
            phone,  # phone
            "<MISSING>",  # type
            lat,  # lat
            long,  # long
            "<MISSING>",  # timing
            "https://www.bbtheatres.com/theatres/"])

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

