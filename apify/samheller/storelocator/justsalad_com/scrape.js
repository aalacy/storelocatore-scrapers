const Apify = require('apify');
const axios = require('axios');
const AreaCodes = require('areacodes');
let areaCodes = new AreaCodes();

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {
  return await axios({
    method: 'GET',
    url: 'https://justsalad.com/assets/geo/js.geojson'
  }).then((resp) => {
    returnData = [];
    for (let entry of resp.data.features){
      //Skip upcoming properties
      if (entry.properties.comingSoon !== undefined && entry.properties.comingSoon == true){continue;}

      //Skip dubai properties
      if (entry.properties.locationPhone.startsWith('04')){ continue;}

      area = areaCodes.get(entry.properties.locationPhone, (err, d) => {return d});

      //Skip unrecognized area codes (looks like HK properties)
      if (area == undefined){continue}; 

      
      returnData.push({
        locator_domain: 'justsalad.com',
        location_name: entry.properties.locationName,
        street_address: entry.properties.locationAddress,
        city: area.city,
        state: area.state,
        zip: '<MISSING>',
        country_code: 'US',
        store_number: entry.properties.locationID,
        phone: entry.properties.locationPhone,
        location_type: '<MISSING>',
        latitude: entry.geometry.coordinates[0],
        longitude: entry.geometry.coordinates[1],
        hours_of_operation: entry.properties.hours1 + " " + entry.properties.hours2,
      })
    }
    return returnData;
  })
}
