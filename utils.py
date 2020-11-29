"""
this module is for defining utility functions
that will be used for implementing the equity
analysis
11-28-20
@cesnyah
"""
import numpy as np
import sklearn
from scipy.spatial import distance
import datetime



def getBusCount(stops_row, dep_times):
    '''
    This method takes in a *row* of the stops geodataframe
    that includes information on each stop, with a column
    `STOP ID` that includes integer ID values.
    The method also takes in dep_times, which is a
    dataframe with columns
    `stop_id` `departure_time`
     66            9:35:38
     66            9:00:41  
    The method returns the number of departure times in the 
    dep_times dataframe for the current `STOP ID` in the row
    of the stops geodataframe
    -----
    :input stops_row: a *row* of a geodataframe describing stops
    :input dep_times: a dataframe with departure times for each stop
    :return: the number of departure times for the current stops_row
    '''
    stop_id = stops_row['STOP_ID']  # the method is applied by row
    return dep_times[dep_times['stop_id']==stop_id].shape[0]



def getStopPropDemog(stops_row, census, group='prop_minority'):
    '''
    Extracts the percent group (e.g. % minority) at the stop level
    from the census data
    - The input stops_row is a row of the dataframe including
    stops information with the attribute `buffer` being
    the 1/4 mile radius circle around the stop
    - census is a geodataframe with census data, where this gdf
    is used to find census tracts that overlap with each stop,
    and then map the census tract info. to the stop
    -----
    :input stops_row: a row of the gdf describing stops
    :input census: a geodataframe with census demographic data
    :input group: the %(demographic) attribute that we're mapping
    from census tracts to the stop
    :return: stop level %demographic
    '''
    census_intersects = census['geometry'].intersection(stops_row['buffer'])
    nonempty_intersects = census_intersects[census_intersects.is_empty == False]
    
    per_group_tracts = list()  # stores the contribution of percent minority in each tract
    # weights the percent contribution by area of stop in tract
    
    for idx_tract, inter_poly in nonempty_intersects.iteritems():
        ratio = (inter_poly.area)/(stops_row['buffer'].area)
        per_group_tracts.append(  (ratio)*(census.loc[idx_tract, group])  )
    
    return sum(per_group_tracts)



def getStopDemog(stops_row, census, group='minority'):
    '''
    Extracts the number of group members within a stop (e.g. number of Black people)
    - The input stops_row is a row of the dataframe including
    stops information with the attribute `buffer` being
    the 1/4 mile radius circle around the stop
    - census is a geodataframe with census data, where this gdf
    is used to find census tracts that overlap with each stop,
    and then map the census tract info. to the stop
    -----
    :input stops_row: a row of the gdf describing stops
    :input census: a geodataframe with census demographic data
    :input group: the %(demographic) attribute that we're mapping
    from census tracts to the stop
    :return: stop level %demographic
    '''
    census_intersects = census['geometry'].intersection(stops_row['buffer'])
    nonempty_intersects = census_intersects[census_intersects.is_empty == False]
    
    group_tracts = list()  # stores the contribution of minorities from each tract
    # weights the percent contribution by area of stop in tract
    
    for idx_tract, inter_poly in nonempty_intersects.iteritems():
        ratio = (inter_poly.area)/(census.loc[idx_tract, 'geometry'].area)
        group_tracts.append(  (ratio)*(census.loc[idx_tract, group])       )
    
    return sum(group_tracts)



def getCensusBusDiff(census_row, total_stops_phwd, net='positive'):
    '''
    Maps stops-level change in bus service `impact` to census level
    data. For each census tract, finds the proportion of each stop that
    overlaps with the tract, and then aggregates the `impact` of each stop
    based on the proportion of its 1/4 mile buffer that lies within the 
    tract.
    -----
    :input census_row: a row of the census geodataframe
    :input total_stops_phwd: a geodataframe describing the stops
    :net: a boolean variable that can be used to restrict the analysis
    to stops that had `postive` improvement or `negative` improvement
    if left as None, the method uses the `impact` attribute which refers
    to both positive and/or negative improvement
    :return: tract level aggregation of stop-level changes
    -----
    '''
    if net == 'positive':
        extract = total_stops_phwd[total_stops_phwd['impact'] > 0]
    elif net == 'negative':
        extract = total_stops_phwd[total_stops_phwd['impact'] < 0]
    else:
        extract = total_stops_phwd
    
    tractBusDiff = 0
    
    # find the intersection of all the stops with the current census tract row
    all_stops_tract_intersect = extract['buffer'].intersection(census_row['geometry'])  
    
    # get the stops that have non-zero intersection with the census tract
    stops_tract_inter = all_stops_tract_intersect[all_stops_tract_intersect.is_empty == False]
    
    # iterate through every stop that intersects TAZ, should be a small number
    for idx_stops_tract_row, stops_tract_row in stops_tract_inter.iteritems():  
        tot_stop_area = extract.loc[idx_stops_tract_row, 'buffer'].area
        intersect_area = stops_tract_row.area  # get the area of the intersection
        prop_area = intersect_area/(tot_stop_area)  # get the proportion of the stop in the TAZ
        bus_diff_prop = (extract.loc[idx_stops_tract_row, 'impact'])*(prop_area)  # get the contribution of the stop BUS_DIFF to the census level impact
        tractBusDiff += bus_diff_prop  # update dict at current TAZ value with the contribution of this stop to impact
    return tractBusDiff



def getDoorsOpening(stops_row):
    '''
    For a row of the stops geodataframe, stops_row, the output
    takes the value of `impact` for the stops with positive `impact`
    and places a value of zero for stops with negative `impact`
    -----
    :input stops_row: row of the stops gdf, with the col. `impact`
    representing the change in service after CapRemap
    :return: `impact` of positively impacted stops, 0 o.w. 
    -----
    '''
    return max(stops_row['impact'], 0)



def getDoorsClosing(stops_row):
    '''
    For a row of the stops geodataframe, stops_row, the output
    takes the value of `impact` for the stops with negative `impact`
    and places a value of zero for stops with positive `impact`
    -----
    :input stops_row: row of the stops gdf, with the col. `impact`
    representing the change in service after CapRemap
    :return: `impact` of negatively impacted stops, 0 o.w. 
    -----
    '''
    return max(-stops_row['impact'], 0)



def getBusDiffBool(total_stops_row, threshold=10):
    '''
    This method takes in a *row* of a geodataframe with info. on the stops.
    The geodataframe must have a column labeled `impact` that represents the
    change in service after implementation of CapRemap.
    The output is -1,0, or 1 if the `impact` is less than threshold, between
    (-threshold, threshold), or greater than threshold.
    -----
    :input total_stops_row: row of the stops geodataframe
    :input threshold: margin beyond which a change in counts is significant
    :output: boolean indicator if above or below threshold
    '''
    if total_stops_row['impact'] <= -threshold:
        return -1
    elif total_stops_row['impact'] >= threshold:
        return 1
    else:
        return 0

    
    
def isPeak(departureTimes_sup, peak_hour):
    '''
    goes through a row of the stop_times_sup.txt
    df and checks if the row is within peak hour
    this stop_times_sup.txt file gives departure times
    per stop
    -----
    :input stop_trips: a row of stop_times_sup.txt from GTFS data
    :input valid_trips: pre-determined trip IDs that fall within service IDs
    that represent weekday trips (and not special events)
    :input peak_hour: a tuple representing our definition of peak_hour
    :output boolean: 1 if trip is valid, 0 otherwise
    '''
    hour = float(departureTimes_sup['departure_time'].strip().split(':')[0])
    if peak_hour[0] <= hour < peak_hour[1]:
        return 1
    else:
        return 0


    
def checkMulti(geom):
    '''
    for line elements in a shapefile,
    check if the row is a shapely line or a
    shapely multiline
    -----
    :input geom: element of the geometry column
    :output: either 1 if multiline, 0 otherwise
    -----
    '''
    if geom.geom_type == 'MultiLineString':
        return 1
    else:
        return 0


    
def getLineCoords(geom, coord_type):
    '''
    same as getPtCoords (points) and getCoords (polygons),
    gets the coordinates for line and multiline shapes
    the key difference is that this method returns 
    the x or y coordinate for either multiline plotting or line
    plotting depending on type.
    To implement the plotting, plot each line and 
    multiline elements separately by using the info. from the
    boolean classficiation (see checkMulti)
    -----
    :input geom: element of the geometry column
    :input coord_type: either 'x' or 'y' 
    :output coord_list: a list with the x or y coordinates of the shapely line or multiline
    -----
    '''
    if geom.geom_type == 'MultiLineString':
        lines = list(geom)
        if coord_type == 'x':  
            x_coords = list()
            for line in lines:
                x_coords.append(  list(line.coords.xy[0]) )
            return x_coords
        elif coord_type == 'y':
            y_coords = list()
            for line in lines:
                y_coords.append(  list(line.coords.xy[1])   )
            return y_coords
    else:
        if coord_type == 'x':
            return list(geom.coords.xy[0])
        elif coord_type == 'y':
            return list(geom.coords.xy[1])   
            

            
def getPtCoords(geom, coord_type):
    '''
    same as getCoords but for points
    instead of polygons
    -----
    input geom: element of the geometry column
    :input coord_type: either 'x' or 'y' 
    :output coord_list: a list with the x or y coordinates of the shapely point
    -----
    '''
    if coord_type == 'x':
        return list(geom.coords.xy[0] )[0]
    elif coord_type == 'y':
        return list(geom.coords.xy[1] )[0]
    else:
        raise Exception('... error in getCoords, check coord_type input ...')


        
def getCoords(geom, coord_type):
    '''
    returns the coordinates for the geometry column
    of a polygon
    -----
    :input geom: element of the geometry column
    :input coord_type: either 'x' or 'y' 
    :output coord_list: a list with the x or y coordinates of the shapely linear ring
    -----
    '''
    if coord_type == 'x':
        return list(geom.exterior.coords.xy[0] )
    elif coord_type == 'y':
        return list(geom.exterior.coords.xy[1] )
    else:
        raise Exception('... error in getCoords, check coord_type input ...')

