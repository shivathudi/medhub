
# coding: utf-8

# 
# ### Files required: SanFrancisco.csv, Addresses.csv

# ### Libraries

# In[3]:

import pandas as pd, numpy as np
import os, sys, glob, ast, gpxpy.geo, urllib, urllib2, json, csv
from random import randint
from time import sleep
import phonenumbers
pd.options.mode.chained_assignment = None


# ### Supporting Functions

# In[4]:

def address_to_coordinates(address):
    """
    Given a text address, returns the corresponding latitude and longitude

    Input: Address (String)
    
    Output: Latitude, Longitude
    """    
    sleep(randint(1,3))
    params = {
            'address' : address,
            'sensor' : 'false',
    }  
    url = 'https://maps.google.com/maps/api/geocode/json?' + urllib.urlencode(params)

    response = urllib2.urlopen(url)
    result = json.load(response)
    try:
        location = result['results'][0]['geometry']['location']
        latitude, longitude = location['lat'], location['lng']
        return latitude, longitude
    except:
        latitude, longitude = None, None
        return latitude, longitude

def calc_dist(lat1, lon1, lat2, lon2):
    """
    Given 2 pairs of latitude and longitude, returns the Haversine distance between them

    Input: Latitude and Longitude of the 2 locations
    
    Output: Distance in meters
    """    
    try:
        return gpxpy.geo.haversine_distance(lat1, lon1, lat2, lon2)
    except:
        return None


# ### Function to get nearest doctors

# In[5]:

def getNearestDoctors(addr, specialty, n = 5, max_dist = 5):
    """
    Given a text address and number of doctors (n), returns the n nearest doctors

    Input: Address (String), number of doctors
    
    Output: CSV consisting of data for n nearest doctors
    """    
    # Read in SF NPI data, and address to coordinates mapping for all SF doctors
    sf_npi_data = pd.read_csv("Data_Scraping/nearest_doctors/SanFrancisco_withRatings.csv")
    address_data = pd.read_csv("Data_Scraping/nearest_doctors/Addresses.csv")
        
    # Get unique doctors
    sf_npi_data = sf_npi_data.drop_duplicates('Professional Enrollment ID')

    # Remove duplicates from addresses
    address_data = address_data.drop_duplicates()
    
    # Filter based on specialty
    sf_npi_data = sf_npi_data.loc[sf_npi_data['Primary specialty'].isin(specialty)]
    
    # Remove Index column in case it's present in the CSVs
    try:
        address_data = address_data.drop('Unnamed: 0', axis = 1)
        sf_npi_data = sf_npi_data.drop('Unnamed: 0', axis = 1)
    except:
        pass
    
    # Remove City from 'Line 1 Street Address' ('San Francisco' was appended to Line 1 Addresses to query Google Maps API)
    address_data[u'Line 1 Street Address'] = address_data[u'Line 1 Street Address'].apply(lambda x: x[:-14])
    
    # Join addresses to sf_npi_data, to get Lat Lon for all rows
    result = pd.merge(sf_npi_data, address_data, how='left', on=[u'Line 1 Street Address'])
    result = result[pd.notnull(result['coordinates'])]
    
    # Get coordinates of queried address from Google Maps API
    queryCoord = address_to_coordinates(addr)
#     queryCoord = (37.790886, -122.392533)

    # Get distance of all doctors from queried address
    result['Distance'] = result['coordinates'].apply(lambda x: calc_dist(queryCoord[0], queryCoord[1], ast.literal_eval(x)[0], ast.literal_eval(x)[1]))
        
    # Converting to miles
    result['Distance'] = result['Distance'] * 0.000621371
    
    # Subsetting based on max_dist
    result = result.loc[result['Distance'] < max_dist]

    # Output nearest doctors to CSV
    result = result.sort_values(by=['Distance', 'Rating'], ascending=[True, False])
    topresult = result.head(n)
    
    # Formatting phone numbers
    topresult['Phone Number'] = topresult['Phone Number'].astype(int).astype(str)
    topresult['Phone Number'] = topresult['Phone Number'].apply(lambda x: phonenumbers.format_number(phonenumbers.parse(x, 'US'), phonenumbers.PhoneNumberFormat.NATIONAL))
    
    # Selecting only relevant columns to be returned to user
    topresult = topresult[['Last Name', 'First Name', 'Distance', 'Rating', 'Line 1 Street Address', 'Primary specialty', 'Medical school name', 'Phone Number']]
    
    # Replace NaN with blank
    topresult = topresult.replace(np.nan, '', regex = True)
    
    # Converting dataframe to list of lists
    topresult_list = topresult.values.tolist()
    
    return topresult_list


# ### Query

# In[6]:

# print getNearestDoctors(addr = '101 howard street', specialty = ['CHIROPRACTIC', 'GENERAL PRACTICE'], n = 5, max_dist = 5)



