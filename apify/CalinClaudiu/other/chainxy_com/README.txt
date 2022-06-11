
Column N:
	Countries_counts_prices
		If Variation? = False:
			(N) - Shows a dict containing 'country/region','count','sub-countries','price','sku','variation_id'
			(Basically a more concise form of column F (variation_data) )
			
			Example of Variation = False:
					
					(F)variation_data				= A large dictionary containing all the data obtained from chainXY for any post-processing.
					(G)location_count_country 		=77
					(H)location_count_for_country	=worldwide
					(I)which_countries_crawled		=United States
					(N)countries_counts_prices		=[{'country/region':'worldwide','count':'77','sub-countries':'Mexico, United States.','price':'50','sku':'32-34','variation_id':'188555'}, {'country/region':'united-states','count':'69','sub-countries':'united-states','price':'45','sku':'32-10','variation_id':'188556'}, {'country/region':'mexico-caribbean-central-america','count':'8','sub-countries':'Mexico.','price':'15','sku':'32-4','variation_id':'188557'}]

			
		If Variation? = True:
			(N) - Shows the Price for the country/region indicated in column H(location_count_for_country) with the sub-countries in column I(which_countries_crawled)
			Example of Variation = True:
			(same brand as above)
					
					(F)variation_data				=32-4
					(G)location_count_country		=8
					(H)location_count_for_country	=mexico-caribbean-central-america
					(I)which_countries_crawled		=Mexico.
					(N)countries_counts_prices		=15
					
					
				(Data is taken from the 'parent' above in column N, see below:)
				[{	'country/region':'mexico-caribbean-central-america',
					'count':'8',
					'sub-countries':'Mexico.',
					'price':'15',
					'sku':'32-4',
					'variation_id':'188557'}]

Where the data from each column comes from:

ChainXY_URL - Link to the 'sub-page' of the chain as found on https://chainxy.com/chains/
brand_name - Name of the brand as found on https://chainxy.com/chains/
SIC - As found on the 'sub-page' in the right column 
NAICS - As found on the 'sub-page' in the right column 
product_id - Right click -> inspect, Ctrl+f product_id   (Comes from the <form> tag)
variation_data - Right click -> inspect, Ctrl+f data-product_variations   (Comes from the <form> tag)
location_count_country - Count as found on the 'sub-page' of each chain, without any variation selected. (Example: Location Count: 304 locations worldwide)(304)
location_count_for_country - Countries (where the above count applies to) as found on the 'sub-page' of each chain, without any variation selected.Example: Location Count: 304 locations worldwide)(worldwide)
which_countries_crawled - Countries (Hover on the flags) as found on https://chainxy.com/chains/ alternatively, ctrl+f in inspect mode searh for: flagicons
how_many_countries - Tries to count all countries specified in VariationData (I planned to use this to determine if we can get global coverage)
last_updated - As seen in the 'sub-page' of each chain in the left column.
categories - As seen in the 'sub-page' of each chain in the right column.
brand_domain - Brand
countries_counts_prices - A more concise form of 'Variation_data' containing 'country/region','count','sub-countries','price','sku','variation_id'
parent_chain - Parent chain name (if existent)
parent_chain_URL - Parent chain URL to chainxy (if existent)
Variation? - FALSE or TRUE
	FALSE -> Means this is a 'Main' record grabbed and found on https://chainxy.com/chains/
			 The count of all Variation? False rows should be similar to the count for "Chains" on this link: https://chainxy.com/product-categories/product-categories/
	
	TRUE  -> Means this is an artificial record, created by using the previous 'countries_counts_prices' column to insert more rows
			 Generates as many rows as drop-down list options for each chain 'sub-page'
			 What will change in artificial rows:
				variation_data is now the SKU previously found in countries_counts_prices for the 'parent' record.
				location_count_country is now the count for the country specified below.
				location_count_for_country is now "attribute_pa_country" from the previous variation_data of the parent chain.
				countries_counts_prices is now the price for the country/package selected in the dropdown (the variation)
				which_countries_crawled is now the countries specified in variation_description (Example: "variation_description": "<p><strong>Avis Rent A Car</strong> in <strong>Asia</strong> has <strong>172</strong> locations available from Cambodia, India, Vietnam, Taiwan, Macau, Hong Kong, Japan, Singapore, Azerbaijan, Georgia, Armenia, China, Kazakhstan, South Korea, Malaysia, Laos, Indonesia, Philippines, Brunei Darussalam, Thailand, Pakistan.</p>\n",)
																								(Here it will be: Cambodia, India, Vietnam, Taiwan .... )

Full VariationData example:
[
	{
		"attributes": {
			"attribute_pa_country": "worldwide"
		},
		"availability_html": "",
		"backorders_allowed": "False",
		"dimensions": {
			"length": "",
			"width": "",
			"height": ""
		},
		"dimensions_html": "N/A",
		"display_price": 555,
		"display_regular_price": 555,
		"image": {
			"title": "Avis Rent A Car",
			"caption": "",
			"url": "False",
			"alt": "",
			"src": "NONE",
			"srcset": "False",
			"sizes": "False",
			"full_src": "NONE",
			"full_src_w": "NONE",
			"full_src_h": "NONE",
			"gallery_thumbnail_src": "NONE",
			"gallery_thumbnail_src_w": "NONE",
			"gallery_thumbnail_src_h": "NONE",
			"thumb_src": "NONE",
			"thumb_src_w": "NONE",
			"thumb_src_h": "NONE",
			"src_w": "NONE",
			"src_h": "NONE"
		},
		"image_id": "",
		"is_downloadable": "True",
		"is_in_stock": "True",
		"is_purchasable": "True",
		"is_sold_individually": "yes",
		"is_virtual": "True",
		"max_qty": 1,
		"min_qty": 1,
		"price_html": "<span class=price><span class=woocommerce-Price-amount amount><span class=woocommerce-Price-currencySymbol>&#36;</span>555.00</span></span>",
		"sku": "386-34",
		"variation_description": "<p><strong>Avis Rent A Car</strong> in <strong>Worldwide</strong> has <strong>4775</strong> locations available from Cambodia, India, Vietnam, Taiwan, Macau, Hong Kong, Japan, Singapore, Azerbaijan, Georgia, Armenia, China, Kazakhstan, South Korea, Malaysia, Laos, Indonesia, Philippines, Brunei Darussalam, Thailand, Pakistan, Canada, Faroe Islands, Gibraltar, North Macedonia, Malta, Latvia, Netherlands, Italy, Norway, Poland, Portugal, Iceland, Romania, Hungary, Russia, Greece, Germany, Slovakia, Slovenia, France, Finland, Monaco, Luxembourg, Estonia, Spain, Sweden, Denmark, Czech Republic, Cyprus, Croatia, Switzerland, Turkey, Ukraine, Bosnia and Herzegovina, Albania, Bulgaria, Kosovo, Belgium, Belarus, Andorra, Austria, Lithuania, Barbados, Panama, Trinidad and Tobago, Caribbean Netherlands, Honduras, Cayman Islands, Saint Martin, Mexico, Anguilla, Guadeloupe, El Salvador, Dominican Republic, Dominica, Aruba, Grenada, Belize, Martinique, Turks and Caicos Islands, Costa Rica, Jamaica, Guatemala, Saint Vincent and Grenadines, Nicaragua, British Virgin Islands, Bahamas, Saint Kitts and Nevis, Haiti, Tunisia, Lebanon, Saudi Arabia, Libya, Bahrain, United Arab Emirates, Oman, Israel, Kuwait, Jordan, Qatar, Egypt, Morocco, Cook Islands, Tonga, Vanuatu, Solomon Islands, Western Samoa, Papua New Guinea, New Zealand, New Caledonia, French Polynesia, Fiji, Australia, Paraguay, Brazil, Chile, Colombia, Argentina, Venezuela, Uruguay, Suriname, French Guiana, Ecuador, Peru, Madagascar, Western Sahara, Gambia, Gabon, Equatorial Guinea, Congo (Brazzaville), Seychelles, Mayotte, Chad, Central African Republic, Cameroon, Burkina Faso, Ghana, Guinea, Kenya, Lesotho, Malawi, Mali, Mauritius, Mozambique, Namibia, Niger, Nigeria, Réunion, Senegal, South Africa, Swaziland, Botswana, Togo, Zambia, Zimbabwe, Congo (Kinshasa), Côte d&#8217;Ivoire, Benin, Angola, United Kingdom, Isle of Man, Jersey, Ireland, Guernsey, American Samoa, United States, Puerto Rico, US Virgin Islands, Northern Mariana Islands, Guam.</p>\n",
		"variation_id": 186558,
		"variation_is_active": "True",
		"variation_is_visible": "True",
		"weight": "",
		"weight_html": "N/A"
	},
	{
		"attributes": {
			"attribute_pa_country": "europe"
		},
		"availability_html": "",
		"backorders_allowed": "FALSE",
		"dimensions": {
			"length": "",
			"width": "",
			"height": ""
		},
		"dimensions_html": "N/A",
		"display_price": 95,
		"display_regular_price": 95,
		"image": {
			"title": "Avis Rent A Car",
			"caption": "",
			"url": "FALSE",
			"alt": "",
			"src": "NONE",
			"srcset": "FALSE",
			"sizes": "FALSE",
			"full_src": "NONE",
			"full_src_w": "NONE",
			"full_src_h": "NONE",
			"gallery_thumbnail_src": "NONE",
			"gallery_thumbnail_src_w": "NONE",
			"gallery_thumbnail_src_h": "NONE",
			"thumb_src": "NONE",
			"thumb_src_w": "NONE",
			"thumb_src_h": "NONE",
			"src_w": "NONE",
			"src_h": "NONE"
		},
		"image_id": "",
		"is_downloadable": "True",
		"is_in_stock": "True",
		"is_purchasable": "True",
		"is_sold_individually": "yes",
		"is_virtual": "True",
		"max_qty": 1,
		"min_qty": 1,
		"price_html": "<span class=price><span class=woocommerce-Price-amount amount><span class=woocommerce-Price-currencySymbol>&#36;</span>95.00</span></span>",
		"sku": "386-3",
		"variation_description": "<p><strong>Avis Rent A Car</strong> in <strong>Europe</strong> has <strong>1895</strong> locations available from Faroe Islands, Gibraltar, North Macedonia, Malta, Latvia, Netherlands, Italy, Norway, Poland, Portugal, Iceland, Romania, Hungary, Russia, Greece, Germany, Slovakia, Slovenia, France, Finland, Monaco, Luxembourg, Estonia, Spain, Sweden, Denmark, Czech Republic, Cyprus, Croatia, Switzerland, Turkey, Ukraine, Bosnia and Herzegovina, Albania, Bulgaria, Kosovo, Belgium, Belarus, Andorra, Austria, Lithuania.</p>\n",
		"variation_id": 186559,
		"variation_is_active": "True",
		"variation_is_visible": "True",
		"weight": "",
		"weight_html": "N/A"
	},
	{
		"attributes": {
			"attribute_pa_country": "united-states"
		},
		"availability_html": "",
		"backorders_allowed": "FALSE",
		"dimensions": {
			"length": "",
			"width": "",
			"height": ""
		},
		"dimensions_html": "N/A",
		"display_price": 90,
		"display_regular_price": 90,
		"image": {
			"title": "Avis Rent A Car",
			"caption": "",
			"url": "FALSE",
			"alt": "",
			"src": "NONE",
			"srcset": "FALSE",
			"sizes": "FALSE",
			"full_src": "NONE",
			"full_src_w": "NONE",
			"full_src_h": "NONE",
			"gallery_thumbnail_src": "NONE",
			"gallery_thumbnail_src_w": "NONE",
			"gallery_thumbnail_src_h": "NONE",
			"thumb_src": "NONE",
			"thumb_src_w": "NONE",
			"thumb_src_h": "NONE",
			"src_w": "NONE",
			"src_h": "NONE"
		},
		"image_id": "",
		"is_downloadable": "True",
		"is_in_stock": "True",
		"is_purchasable": "True",
		"is_sold_individually": "yes",
		"is_virtual": "True",
		"max_qty": 1,
		"min_qty": 1,
		"price_html": "<span class=price><span class=woocommerce-Price-amount amount><span class=woocommerce-Price-currencySymbol>&#36;</span>90.00</span></span>",
		"sku": "386-10",
		"variation_description": "<p><strong>Avis Rent A Car</strong> in the <strong>United States</strong> has <strong>1369</strong> locations available.</p>\n",
		"variation_id": 186560,
		"variation_is_active": "True",
		"variation_is_visible": "True",
		"weight": "",
		"weight_html": "N/A"
	},
	{
		"attributes": {
			"attribute_pa_country": "oceania"
		},
		"availability_html": "",
		"backorders_allowed": "FALSE",
		"dimensions": {
			"length": "",
			"width": "",
			"height": ""
		},
		"dimensions_html": "N/A",
		"display_price": 75,
		"display_regular_price": 75,
		"image": {
			"title": "Avis Rent A Car",
			"caption": "",
			"url": "FALSE",
			"alt": "",
			"src": "NONE",
			"srcset": "FALSE",
			"sizes": "FALSE",
			"full_src": "NONE",
			"full_src_w": "NONE",
			"full_src_h": "NONE",
			"gallery_thumbnail_src": "NONE",
			"gallery_thumbnail_src_w": "NONE",
			"gallery_thumbnail_src_h": "NONE",
			"thumb_src": "NONE",
			"thumb_src_w": "NONE",
			"thumb_src_h": "NONE",
			"src_w": "NONE",
			"src_h": "NONE"
		},
		"image_id": "",
		"is_downloadable": "True",
		"is_in_stock": "True",
		"is_purchasable": "True",
		"is_sold_individually": "yes",
		"is_virtual": "True",
		"max_qty": 1,
		"min_qty": 1,
		"price_html": "<span class=price><span class=woocommerce-Price-amount amount><span class=woocommerce-Price-currencySymbol>&#36;</span>75.00</span></span>",
		"sku": "386-6",
		"variation_description": "<p><strong>Avis Rent A Car</strong> in <strong>Oceania</strong> has <strong>488</strong> locations available from Cook Islands, Tonga, Vanuatu, Solomon Islands, Western Samoa, Papua New Guinea, New Zealand, New Caledonia, French Polynesia, Fiji, Australia.</p>\n",
		"variation_id": 186561,
		"variation_is_active": "True",
		"variation_is_visible": "True",
		"weight": "",
		"weight_html": "N/A"
	},
	{
		"attributes": {
			"attribute_pa_country": "sub-saharan-africa-indian-ocean"
		},
		"availability_html": "",
		"backorders_allowed": "FALSE",
		"dimensions": {
			"length": "",
			"width": "",
			"height": ""
		},
		"dimensions_html": "N/A",
		"display_price": 60,
		"display_regular_price": 60,
		"image": {
			"title": "Avis Rent A Car",
			"caption": "",
			"url": "FALSE",
			"alt": "",
			"src": "NONE",
			"srcset": "FALSE",
			"sizes": "FALSE",
			"full_src": "NONE",
			"full_src_w": "NONE",
			"full_src_h": "NONE",
			"gallery_thumbnail_src": "NONE",
			"gallery_thumbnail_src_w": "NONE",
			"gallery_thumbnail_src_h": "NONE",
			"thumb_src": "NONE",
			"thumb_src_w": "NONE",
			"thumb_src_h": "NONE",
			"src_w": "NONE",
			"src_h": "NONE"
		},
		"image_id": "",
		"is_downloadable": "True",
		"is_in_stock": "True",
		"is_purchasable": "True",
		"is_sold_individually": "yes",
		"is_virtual": "True",
		"max_qty": 1,
		"min_qty": 1,
		"price_html": "<span class=price><span class=woocommerce-Price-amount amount><span class=woocommerce-Price-currencySymbol>&#36;</span>60.00</span></span>",
		"sku": "386-8",
		"variation_description": "<p><strong>Avis Rent A Car</strong> in <strong>Sub Saharan Africa + Indian Ocean</strong> has <strong>193</strong> locations available from Madagascar, Western Sahara, Gambia, Gabon, Equatorial Guinea, Congo (Brazzaville), Seychelles, Mayotte, Chad, Central African Republic, Cameroon, Burkina Faso, Ghana, Guinea, Kenya, Lesotho, Malawi, Mali, Mauritius, Mozambique, Namibia, Niger, Nigeria, Réunion, Senegal, South Africa, Swaziland, Botswana, Togo, Zambia, Zimbabwe, Congo (Kinshasa), Côte d&#8217;Ivoire, Benin, Angola.</p>\n",
		"variation_id": 186562,
		"variation_is_active": "True",
		"variation_is_visible": "True",
		"weight": "",
		"weight_html": "N/A"
	},
	{
		"attributes": {
			"attribute_pa_country": "mexico-caribbean-central-america"
		},
		"availability_html": "",
		"backorders_allowed": "FALSE",
		"dimensions": {
			"length": "",
			"width": "",
			"height": ""
		},
		"dimensions_html": "N/A",
		"display_price": 55,
		"display_regular_price": 55,
		"image": {
			"title": "Avis Rent A Car",
			"caption": "",
			"url": "FALSE",
			"alt": "",
			"src": "NONE",
			"srcset": "FALSE",
			"sizes": "FALSE",
			"full_src": "NONE",
			"full_src_w": "NONE",
			"full_src_h": "NONE",
			"gallery_thumbnail_src": "NONE",
			"gallery_thumbnail_src_w": "NONE",
			"gallery_thumbnail_src_h": "NONE",
			"thumb_src": "NONE",
			"thumb_src_w": "NONE",
			"thumb_src_h": "NONE",
			"src_w": "NONE",
			"src_h": "NONE"
		},
		"image_id": "",
		"is_downloadable": "True",
		"is_in_stock": "True",
		"is_purchasable": "True",
		"is_sold_individually": "yes",
		"is_virtual": "True",
		"max_qty": 1,
		"min_qty": 1,
		"price_html": "<span class=price><span class=woocommerce-Price-amount amount><span class=woocommerce-Price-currencySymbol>&#36;</span>55.00</span></span>",
		"sku": "386-4",
		"variation_description": "<p><strong>Avis Rent A Car</strong> in <strong>Mexico, Caribbean + Central America</strong> has <strong>153</strong> locations available from Barbados, Panama, Trinidad and Tobago, Caribbean Netherlands, Honduras, Cayman Islands, Saint Martin, Mexico, Anguilla, Guadeloupe, El Salvador, Dominican Republic, Dominica, Aruba, Grenada, Belize, Martinique, Turks and Caicos Islands, Costa Rica, Jamaica, Guatemala, Saint Vincent and Grenadines, Nicaragua, British Virgin Islands, Bahamas, Saint Kitts and Nevis, Haiti.</p>\n",
		"variation_id": 186563,
		"variation_is_active": "True",
		"variation_is_visible": "True",
		"weight": "",
		"weight_html": "N/A"
	},
	{
		"attributes": {
			"attribute_pa_country": "asia"
		},
		"availability_html": "",
		"backorders_allowed": "FALSE",
		"dimensions": {
			"length": "",
			"width": "",
			"height": ""
		},
		"dimensions_html": "N/A",
		"display_price": 55,
		"display_regular_price": 55,
		"image": {
			"title": "Avis Rent A Car",
			"caption": "",
			"url": "FALSE",
			"alt": "",
			"src": "NONE",
			"srcset": "FALSE",
			"sizes": "FALSE",
			"full_src": "NONE",
			"full_src_w": "NONE",
			"full_src_h": "NONE",
			"gallery_thumbnail_src": "NONE",
			"gallery_thumbnail_src_w": "NONE",
			"gallery_thumbnail_src_h": "NONE",
			"thumb_src": "NONE",
			"thumb_src_w": "NONE",
			"thumb_src_h": "NONE",
			"src_w": "NONE",
			"src_h": "NONE"
		},
		"image_id": "",
		"is_downloadable": "True",
		"is_in_stock": "True",
		"is_purchasable": "True",
		"is_sold_individually": "yes",
		"is_virtual": "True",
		"max_qty": 1,
		"min_qty": 1,
		"price_html": "<span class=price><span class=woocommerce-Price-amount amount><span class=woocommerce-Price-currencySymbol>&#36;</span>55.00</span></span>",
		"sku": "386-1",
		"variation_description": "<p><strong>Avis Rent A Car</strong> in <strong>Asia</strong> has <strong>172</strong> locations available from Cambodia, India, Vietnam, Taiwan, Macau, Hong Kong, Japan, Singapore, Azerbaijan, Georgia, Armenia, China, Kazakhstan, South Korea, Malaysia, Laos, Indonesia, Philippines, Brunei Darussalam, Thailand, Pakistan.</p>\n",
		"variation_id": 186564,
		"variation_is_active": "True",
		"variation_is_visible": "True",
		"weight": "",
		"weight_html": "N/A"
	},
	{
		"attributes": {
			"attribute_pa_country": "canada"
		},
		"availability_html": "",
		"backorders_allowed": "FALSE",
		"dimensions": {
			"length": "",
			"width": "",
			"height": ""
		},
		"dimensions_html": "N/A",
		"display_price": 55,
		"display_regular_price": 55,
		"image": {
			"title": "Avis Rent A Car",
			"caption": "",
			"url": "FALSE",
			"alt": "",
			"src": "NONE",
			"srcset": "FALSE",
			"sizes": "FALSE",
			"full_src": "NONE",
			"full_src_w": "NONE",
			"full_src_h": "NONE",
			"gallery_thumbnail_src": "NONE",
			"gallery_thumbnail_src_w": "NONE",
			"gallery_thumbnail_src_h": "NONE",
			"thumb_src": "NONE",
			"thumb_src_w": "NONE",
			"thumb_src_h": "NONE",
			"src_w": "NONE",
			"src_h": "NONE"
		},
		"image_id": "",
		"is_downloadable": "True",
		"is_in_stock": "True",
		"is_purchasable": "True",
		"is_sold_individually": "yes",
		"is_virtual": "True",
		"max_qty": 1,
		"min_qty": 1,
		"price_html": "<span class=price><span class=woocommerce-Price-amount amount><span class=woocommerce-Price-currencySymbol>&#36;</span>55.00</span></span>",
		"sku": "386-2",
		"variation_description": "<p><strong>Avis Rent A Car</strong> in <strong>Canada</strong> has <strong>166</strong> locations.</p>\n",
		"variation_id": 186565,
		"variation_is_active": "True",
		"variation_is_visible": "True",
		"weight": "",
		"weight_html": "N/A"
	},
	{
		"attributes": {
			"attribute_pa_country": "middle-east-north-africa"
		},
		"availability_html": "",
		"backorders_allowed": "FALSE",
		"dimensions": {
			"length": "",
			"width": "",
			"height": ""
		},
		"dimensions_html": "N/A",
		"display_price": 55,
		"display_regular_price": 55,
		"image": {
			"title": "Avis Rent A Car",
			"caption": "",
			"url": "FALSE",
			"alt": "",
			"src": "NONE",
			"srcset": "FALSE",
			"sizes": "FALSE",
			"full_src": "NONE",
			"full_src_w": "NONE",
			"full_src_h": "NONE",
			"gallery_thumbnail_src": "NONE",
			"gallery_thumbnail_src_w": "NONE",
			"gallery_thumbnail_src_h": "NONE",
			"thumb_src": "NONE",
			"thumb_src_w": "NONE",
			"thumb_src_h": "NONE",
			"src_w": "NONE",
			"src_h": "NONE"
		},
		"image_id": "",
		"is_downloadable": "True",
		"is_in_stock": "True",
		"is_purchasable": "True",
		"is_sold_individually": "yes",
		"is_virtual": "True",
		"max_qty": 1,
		"min_qty": 1,
		"price_html": "<span class=price><span class=woocommerce-Price-amount amount><span class=woocommerce-Price-currencySymbol>&#36;</span>55.00</span></span>",
		"sku": "386-5",
		"variation_description": "<p><strong>Avis Rent A Car</strong> in <strong>Middle East + North Africa</strong> has <strong>141</strong> locations available from Tunisia, Lebanon, Saudi Arabia, Libya, Bahrain, United Arab Emirates, Oman, Israel, Kuwait, Jordan, Qatar, Egypt, Morocco.</p>\n",
		"variation_id": 186566,
		"variation_is_active": "True",
		"variation_is_visible": "True",
		"weight": "",
		"weight_html": "N/A"
	},
	{
		"attributes": {
			"attribute_pa_country": "south-america"
		},
		"availability_html": "",
		"backorders_allowed": "FALSE",
		"dimensions": {
			"length": "",
			"width": "",
			"height": ""
		},
		"dimensions_html": "N/A",
		"display_price": 55,
		"display_regular_price": 55,
		"image": {
			"title": "Avis Rent A Car",
			"caption": "",
			"url": "FALSE",
			"alt": "",
			"src": "NONE",
			"srcset": "FALSE",
			"sizes": "FALSE",
			"full_src": "NONE",
			"full_src_w": "NONE",
			"full_src_h": "NONE",
			"gallery_thumbnail_src": "NONE",
			"gallery_thumbnail_src_w": "NONE",
			"gallery_thumbnail_src_h": "NONE",
			"thumb_src": "NONE",
			"thumb_src_w": "NONE",
			"thumb_src_h": "NONE",
			"src_w": "NONE",
			"src_h": "NONE"
		},
		"image_id": "",
		"is_downloadable": "True",
		"is_in_stock": "True",
		"is_purchasable": "True",
		"is_sold_individually": "yes",
		"is_virtual": "True",
		"max_qty": 1,
		"min_qty": 1,
		"price_html": "<span class=price><span class=woocommerce-Price-amount amount><span class=woocommerce-Price-currencySymbol>&#36;</span>55.00</span></span>",
		"sku": "386-7",
		"variation_description": "<p><strong>Avis Rent A Car</strong> in <strong>South America</strong> has <strong>121</strong> locations available from Paraguay, Brazil, Chile, Colombia, Argentina, Venezuela, Uruguay, Suriname, French Guiana, Ecuador, Peru.</p>\n",
		"variation_id": 186567,
		"variation_is_active": "True",
		"variation_is_visible": "True",
		"weight": "",
		"weight_html": "N/A"
	},
	{
		"attributes": {
			"attribute_pa_country": "uk-ireland"
		},
		"availability_html": "",
		"backorders_allowed": "FALSE",
		"dimensions": {
			"length": "",
			"width": "",
			"height": ""
		},
		"dimensions_html": "N/A",
		"display_price": 50,
		"display_regular_price": 50,
		"image": {
			"title": "Avis Rent A Car",
			"caption": "",
			"url": "FALSE",
			"alt": "",
			"src": "NONE",
			"srcset": "FALSE",
			"sizes": "FALSE",
			"full_src": "NONE",
			"full_src_w": "NONE",
			"full_src_h": "NONE",
			"gallery_thumbnail_src": "NONE",
			"gallery_thumbnail_src_w": "NONE",
			"gallery_thumbnail_src_h": "NONE",
			"thumb_src": "NONE",
			"thumb_src_w": "NONE",
			"thumb_src_h": "NONE",
			"src_w": "NONE",
			"src_h": "NONE"
		},
		"image_id": "",
		"is_downloadable": "True",
		"is_in_stock": "True",
		"is_purchasable": "True",
		"is_sold_individually": "yes",
		"is_virtual": "True",
		"max_qty": 1,
		"min_qty": 1,
		"price_html": "<span class=price><span class=woocommerce-Price-amount amount><span class=woocommerce-Price-currencySymbol>&#36;</span>50.00</span></span>",
		"sku": "386-9",
		"variation_description": "<p><strong>Avis Rent A Car</strong> in <strong>UK + Ireland</strong> has <strong>77</strong> locations available from United Kingdom, Isle of Man, Jersey, Ireland, Guernsey.</p>\n",
		"variation_id": 186568,
		"variation_is_active": "True",
		"variation_is_visible": "True",
		"weight": "",
		"weight_html": "N/A"
	}
]