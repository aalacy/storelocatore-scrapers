import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('buick_ca')

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'authority': 'www.chevrolet.ca',
           'accept': 'application/json, text/plain, */*',
           'clientapplicationid': 'OCNATIVEAPP',
           'loginin': 'mytest016@outlook.com',
           'locale': 'en_CA'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    sids = []
    cities = ['Toronto','Montreal','Calgary','Ottawa','Edmonton','Mississauga','Winnipeg','Vancouver','Brampton','Hamilton','Quebec','Surrey','Laval','Halifax','London','Markham','Vaughan','Gatineau','Saskatoon','Longueuil','Kitchener','Burnaby','Windsor','Regina','Richmond','Richmond Hill','Oakville','Burlington','Greater Sudbury','Sherbrooke','Oshawa','Saguenay','Levis','Barrie','Abbotsford','Coquitlam','Trois Rivieres','St Catharines','Guelph','Cambridge','Whitby','Kelowna','Kingston','Ajax','Langley','Saanich','Terrebonne','Milton','St Johns','Thunder Bay','Waterloo','Delta','Chatham Kent','Red Deer','Strathcona County','Brantford','St Jean sur Richelieu','Cape Breton','Lethbridge','Clarington','Pickering','Nanaimo','Kamloops','Niagara Falls','North Vancouver','Victoria','Brossard','Repentigny','Newmarket','Chilliwack','Maple Ridge','Peterborough','Kawartha Lakes','Drummondville','St Jerome','Prince George','Sault Ste Marie','Moncton','Sarnia','Wood Buffalo','New Westminster','St John','Caledon','Granby','St Albert','Norfolk County','Medicine Hat','Grande Prairie','Airdrie','Halton Hills','Port Coquitlam','Fredericton','Blainville','St Hyacinthe','Aurora','North Vancouver','Welland','North Bay','Belleville','Mirabel','Shawinigan','Dollard Des Ormeaux','Brandon','Rimouski','Chateauguay','Mascouche','Cornwall','Victoriaville','Whitchurch Stouffville','Haldimand County','Georgina','St Eustache','Quinte West','West Vancouver','Rouyn Noranda','Timmins','Boucherville','Woodstock','Salaberry de Valleyfield','Vernon','St Thomas','Mission','Vaudreuil Dorion','Brant','Lakeshore','Innisfil','Charlottetown','Prince Albert','Langford','Bradford West Gwillimbury','Sorel Tracy','New Tecumseth','Spruce Grove','Moose Jaw','Penticton','Port Moody','West Kelowna','Campbell River','St Georges','Val dOr','Cote St Luc','Stratford','Pointe Claire','Orillia','Alma','Fort Erie','LaSalle','Leduc','Ste Julie','North Cowichan',
              'Dartmouth','Port Hope','Grimsby','Summerside','Edmundston','Middleton','Sussex','Digby','Saint John','St John','Scarborough',
              'Truro','Prince Rupert','Dawson Creek','St Amable','Les Iles de la Madeleine','Bathurst','Whistler','Brighton','Lloydminster (Part)','Gander','Sidney','Rothesay','Terrace','Summerland','Val des Monts','Estevan','Erin','Kincardine','Montmagny','North Saanich','Mackenzie County','Rawdon','Warman','La Tuque','Meaford','Weyburn','South Dundas','LIle Perrot','Williams Lake','Elliot Lake','Marieville','Cantley','Notre Dame de lIle Perrot','Coldstream','Carleton Place','Lambton Shores','Nelson','View Royal','Queens','Selkirk','Hawkesbury','St Felicien','St Sauveur','Ste Agathe des Monts','St Raymond','Sechelt','Whitecourt','South Huron','Roberval','Ste Julienne','Temiskaming Shores','Hinton','Quesnel','Morinville','Moncton','Grey Highlands','Stratford','Mont Tremblant','Martensville','Bois des Filion','Carignan','Brockton','Amherst','Lorraine','Blackfalds','Notre Dame des Prairies','Pont Rouge','Oromocto','Olds','Huron East','St Hippolyte','New Glasgow','Bromont','Penetanguishene','Qualicum Beach','Farnham','West Perth','Arnprior','Smiths Falls','Coaticook','Minto','Morden','Mono','Ladysmith','Bridgewater','Dauphin','Taber','Otterburn Park','South Bruce Peninsula','Edson','Stoneham et Tewkesbury','Kapuskasing','La Malbaie','Renfrew','Coaldale','Nicolet','Portugal Cove St Philips','Kitimat','Shelburne','Happy Valley Goose Bay']
              
    for city in cities:
        logger.info(city)
        url = 'https://www.buick.ca/OCRestServices/dealer/city/v1/buick/' + city + '?distance=200&maxResults=25'
        r = session.get(url, headers=headers)
        website = 'buick.ca'
        for line in r.iter_lines():
            line = str(line.decode('utf-8'))
            if '{"id":' in line:
                items = line.split('{"id":')
                for item in items:
                    if '"dealerName":"' in item:
                        name = item.split('"dealerName":"')[1].split('"')[0]
                        store = item.split(',')[0]
                        typ = '<MISSING>'
                        loc = '<MISSING>'
                        try:
                            loc = item.split('"dealerUrl":"')[1].split('"')[0]
                        except:
                            loc = '<MISSING>'
                        phone = item.split('"phone1":"')[1].split('"')[0]
                        add = item.split('{"addressLine1":"')[1].split('"')[0]
                        city = item.split('"cityName":"')[1].split('"')[0]
                        state = item.split('"countrySubdivisionCode":"')[1].split('"')[0]
                        zc = item.split(',"postalCode":"')[1].split('"')[0]
                        country = 'CA'
                        lat = item.split('"latitude":')[1].split(',')[0]
                        hours = ''
                        lng = item.split('"longitude":')[1].split('}')[0]
                        try:
                            days = item.split('"generalOpeningHour":[{')[1].split('}],"serviceOpeningHour":')[0].split('"openFrom":"')
                            for day in days:
                                if '"dayOfWeek":' in day:
                                    dname = day.split('"dayOfWeek":[')[1].split(']')[0]
                                    dname = dname.replace('1','Mon').replace('2','Tue').replace('3','Wed').replace('4','Thu').replace('5','Fri').replace('6','Sat').replace('7','Sun')
                                    hrs = dname + ': ' + day.split('"')[0] + '-' + day.split(',"openTo":"')[1].split('"')[0]
                                    if hours == '':
                                        hours = hrs
                                    else:
                                        hours = hours + '; ' + hrs
                        except:
                            hours = '<MISSING>'
                        if store not in sids:
                            sids.append(store)
                            logger.info(store)
                            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
