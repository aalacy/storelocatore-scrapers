const { parseString } = require('xml2js');

const noDataLabel = 'NO-DATA';

// Converts XML to JSON
const xml2json = xmlString => new Promise((fullfill, reject) => {
  parseString(xmlString, { explicitArray: false }, (err, result) => {
    if (err) {
      reject(err);
    } else {
      fullfill(result);
    }
  });
});

// Makes the a phone number 10 digits with no punctutations
const formatPhoneNumber = string => string.replace(/\D/g, '');

const validateHours = (string1, string2) => {
  if (string1 === noDataLabel || string1.length === 0) {
    return noDataLabel;
  }
  if (string1 !== noDataLabel || string1.length !== 0) {
    if (string2 === noDataLabel || string2.length === 0) {
      return string1;
    }
  }
  return `${string1}, ${string2}`;
};

// Simply receives data from the scrape, then formats it.
const parseData = ({
  // If any data points are undefined / null, return 'NO-DATA'
  locatorDomain = 'shopnsavefood.com__api', Name = noDataLabel, Address1 = noDataLabel, City = noDataLabel,
  State = noDataLabel, Zip = noDataLabel, countryCode = 'US', StoreID = noDataLabel,
  Phone: Phone = noDataLabel, IsGasStation = noDataLabel,
  naics = noDataLabel, Latitude = noDataLabel,
  Longitude = noDataLabel, Hours = noDataLabel, Hours2 = noDataLabel,
}) => ({
    // Then set the label similar to the template and make adjustments (gas station / store / hours)
    locator_domain: locatorDomain,
    location_name: Name,
    street_address: Address1,
    city: City,
    state: State,
    zip: Zip,
    country_code: countryCode,
    store_number: StoreID,
    // Although redundant is required due to format Phone Number
    ...((Phone === noDataLabel) && { phone: noDataLabel }),
    ...((Phone !== noDataLabel) && { phone: formatPhoneNumber(Phone) }),
    ...((IsGasStation === 'true') && { location_type: 'Gas Station' }),
    ...((IsGasStation === 'false') && { location_type: 'Store' }),
    naics_code: naics,
    latitude: Latitude,
    longitude: Longitude,
    hours_of_operation: validateHours(Hours, Hours2),
  });

module.exports = {
  xml2json,
  formatPhoneNumber,
  parseData
}