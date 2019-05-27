const noDataLabel = 'NO-DATA';

// Leaves only digits for the phone number
const formatPhoneNumber = string => string.replace(/\D/g, '');

const formatHours = array => array.join(',').replace(/\s+/g, '');

// Simply receives data from the scrape, then formats it.
const formatData = ({
  // If any data points are undefined / null, return 'NO-DATA'
  locatorDomain = 'verizonwireless.com',
  location_name: location_name = noDataLabel,
  address: { streetAddress: streetAddress = noDataLabel },
  address: { addressLocality: addressLocality = noDataLabel },
  address: { addressRegion: addressRegion = noDataLabel },
  address: { postalCode: postalCode = noDataLabel },
  address: { addressCountry: addressCountry = noDataLabel },
  StoreID: StoreID = noDataLabel,
  telephone: telephone = noDataLabel,
  '@type': storeType = noDataLabel,
  naics = noDataLabel,
  geo: { latitude: latitude = noDataLabel },
  geo: { longitude: longitude = noDataLabel },
  openingHoursSpecification: hours = noDataLabel,
}) => ({
  // Then set the label similar to the template and make adjustments
  locator_domain: locatorDomain,
  location_name,
  street_address: streetAddress,
  city: addressLocality,
  state: addressRegion,
  zip: postalCode,
  country_code: addressCountry,
  store_number: StoreID,
  phone: formatPhoneNumber(telephone),
  location_type: storeType,
  naics_code: naics,
  latitude,
  longitude,
  hours_of_operation: formatHours(hours[0].dayOfWeek),
});

module.exports = {
  formatPhoneNumber,
  formatData,
};

/* Pre-format

{ location_name: 'Aspen Grove',
  '@context': 'http://schema.org',
  '@type': 'Store',
  image:
   'https://ss7.vzw.com/is/image/VerizonWireless/store-aspen-grove-203452-outside',
  '@id': 'https://www.verizonwireless.com/',
  name: 'Verizon Wireless',
  serviceJson: '',
  address:
   { '@type': 'PostalAddress',
     streetAddress: '7301 S Santa Fe Dr, Ste 724',
     addressLocality: 'Littleton',
     addressRegion: 'CO',
     postalCode: '80120',
     addressCountry: 'US' },
  geo:
   { '@type': 'GeoCoordinates',
     latitude: 39.5823397,
     longitude: -105.0258531 },
  url:
   'https://www.verizonwireless.com/stores/colorado/littleton/aspen-grove-203452/',
  telephone: '+1303.797.3224',
  openingHoursSpecification:
   [ { '@type': 'OpeningHoursSpecification', dayOfWeek: [Array] } ] }

*/
