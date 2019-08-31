const Apify = require('apify');
const axios = require('axios');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {  
  return await axios({
    method: "POST",
    url: "https://www.amegybank.com/locationservices/searchwithfilter",
    data: getRequestData()
  }).then((resp) => {
    returnData = []
    for (let entry of resp.data.location){
      returnData.push(mapData(entry));
    }
    return returnData
  }).catch((e) => {
    console.log("Error: ", e)
  });
}

function mapData(e){
  return {
    locator_domain: 'amegybank.com',
    location_name: e.locationName,
    street_address: e.address,
    city: e.city,
    state: e.stateProvince,
    zip: e.postalCode,
    country_code: e.country,
    store_number: e.locationId,
    phone: e.phoneNumber,
    location_type: getAttribute(e.locationAttributes, "Other Services"),
    latitude: e.lat,
    longitude: e.long,
    hours_of_operation: getAttribute(e.locationAttributes, "Location Hours"),
  }
}

function getRequestData(){
  return { 
    channel: 'Online', 
    schemaVersion: '1.0', 
    transactionId: 'txId', 
    affiliate: '0175', 
    clientUserId: 'ZIONPUBLICSITE', 
    clientApplication: 'ZIONPUBLICSITE', 
    username: 'ZIONPUBLICSITE',
    searchAddress:{ address: 'Texas', city: null,stateProvince: null,postalCode: null,country: null },       
    searchFilters: [ { fieldId: '1', domainId: '175', displayOrder: 1, groupNumber: 1 } ],
    distance: '5000', 
    searchResults: '2000'
  }
}


function getAttribute(attributes, key){
  returnVal = '<MISSING>'
  for (let a of attributes){
    if (a['name'] == key){returnVal = a['value']}
  }
  return returnVal;
}

function handleError(e){
  console.error("Error retrieving data for Amegy Bank", e)
}
