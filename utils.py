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



def getBusCount(stops_row_id, dep_times):
    '''
    This method takes in a *row* of the stops[`STOP_ID`] *Series*
    
    The method also takes in dep_times, which is a
    dataframe with columns
    `stop_id` `departure_time`
     66            9:35:38
     66            9:00:41  
     
    The method returns the number of departure times in the 
    dep_times dataframe for the current `STOP ID` in the row
    of the stops[`STOP_ID`] *Series*
    -----
    :input stops_row_id: the `STOP_ID` of a *row* of the stops[`STOP_ID`] Series
    :input dep_times: a dataframe with departure times for each stop
    :return: the number of departure times for the current stops_row
    -----
    '''
    return dep_times[dep_times['stop_id']==stops_row_id].shape[0]



def getStopPropDemog(stops_row_buffer, census, group='prop_minority'):
    '''
    Extracts the percent group (e.g. prop. minority) at the stop level
    from the census data
    
    - The input stops_row_buffer is a *row* of the *GeoSeries* describing the 
    stops[`buffer`], where the `buffer` is a 1/4 mile radius circle around the stop
    
    - census is a *GeoDataFrame* with census data, where this gdf
    is used to find census tracts that overlap with each stop,
    and then map the census tract info. to the stop
    
    -----
    :input stops_row_buffer: a row of the GeoSeries describing stops['buffer']
    :input census: a geodataframe with census demographic data
    :input group: the (prop. demographic) attribute that we're mapping
    from census tracts to the stop
    :return: stop level prop. demographic
    -----
    '''
    census_intersects = census['geometry'].intersection(stops_row_buffer)
    nonempty_intersects = census_intersects[census_intersects.is_empty == False]
    
    per_group_tracts = list()  # stores the contribution of percent minority in each tract
    # weights the percent contribution by area of stop in tract
    
    for idx_tract, inter_poly in nonempty_intersects.iteritems():
        ratio = (inter_poly.area)/(stops_row_buffer.area)
        per_group_tracts.append(  (ratio)*(census.loc[idx_tract, group])  )
    
    return sum(per_group_tracts)



def getStopDemog(stops_row_buffer, census, group='minority'):
    '''
    Extracts the number of group members within a stop (e.g. number of Black people)
    
    - The input stops_row_buffer is a *row* of the *GeoSeries* describing the 
    stops[`buffer`], where the `buffer` is a 1/4 mile radius circle around the stop
    
    - census is a *GeoDataFrame* with census data, where this gdf
    is used to find census tracts that overlap with each stop,
    and then map the census tract info. to the stop
    
    Note: when passed *census_intersect_coverage* instead of stops_row_buffer, where
    census_intersects_coverage is the unary_union of all the stops, this method
    returns the proportion of group (e.g. minority) that overlaps with the entire
    coverage area. In other words, this method would map demographic groups to the
    entire coverage area when the coverage area is passed. In that case, the method
    would not be applied row-wise to an entire GeoSeries!
    
    Note: demographic groups considered are not normalized (i.e., minority not 
    proportion of minorities), where we need to divide by the tract area to find
    the proportion of group within the intersection area.
    
    -----
    :input stops_row_buffer: a row of the GeoSeries describing stops['buffer'] || or, the union of all stops
    :input census: a geodataframe with census demographic data and attribute `geometry`
    :input group: the (demographic) attribute that we're mapping
    from census tracts to the stop
    :return: stop level demographic || or, demographic in the union of all stops
    -----
    '''
    census_intersects = census['geometry'].intersection(stops_row_buffer)
    nonempty_intersects = census_intersects[census_intersects.is_empty == False]
    
    group_tracts = list()  # stores the contribution of minorities from each tract
    # weights the percent contribution by area of stop in tract
    
    for idx_tract, inter_poly in nonempty_intersects.iteritems():
        ratio = (inter_poly.area)/(census.loc[idx_tract, 'geometry'].area)
        group_tracts.append(  (ratio)*(census.loc[idx_tract, group])       )
    
    return sum(group_tracts)


"""
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
"""


def getDoorsOpening(stops_row_impact):
    '''
    For a row of the stops[`impact`] *Series*, stops_row_impact, the output
    takes the value of `impact` for the stops with positive `impact`
    and places a value of zero for stops with negative `impact`
    -----
    :input stops_row_impact: row of the stops[`impact`] Series, 
    where `impact` represents the change in service after CapRemap
    :return: `impact` of positively impacted stops, 0 o.w. 
    -----
    '''
    return max(stops_row_impact, 0)



def getDoorsClosing(stops_row_impact):
    '''
    For a row of the stops[`impact`] *Series*, stops_row_impact, the output
    takes the value of `impact` for the stops with negative `impact`
    and places a value of zero for stops with positive `impact`
    -----
    :input stops_row_impact: row of the stops[`impact`] Series, 
    where `impact` represents the change in service after CapRemap
    :return: `impact` of negatively impacted stops, 0 o.w. 
    -----
    '''
    return max(-stops_row_impact, 0)



def getBusDiffBool(stops_row_impact, threshold=10):
    '''
    For a row of the stops[`impact`] *Series*, stops_row_impact,
    the output is -1,0, or 1 if the `impact` is less than threshold, between
    (-threshold, threshold), or greater than threshold.
    -----
    :input stops_row_impact: a row of the stops[`impact`] *Series*
    :input threshold: margin beyond which a change in counts is significant
    :output: boolean indicator if above or below threshold
    -----
    '''
    if stops_row_impact <= -threshold:
        return -1
    elif stops_row_impact >= threshold:
        return 1
    else:
        return 0

    
    
def isPeak(departureTime, peak_hour):
    '''
    goes through a row of the *Series* representing the `departure_time` col.
    in stop_times_sup.txt and checks if the `departure_time` is within the peak hour
    -----
    :input departureTimes: a row of the *Series* corresponding to `departure_time` in
    stop_times_sup.txt, where stop_times_sup.txt comes from the GTFS data
    :input peak_hour: a tuple representing our definition of *morning peak*
    :output boolean: 1 if trip is in the morning peak, 0 otherwise
    -----
    '''
    hour = float(departureTime.strip().split(':')[0])
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
    same as getPtCoords (points) and getPolyCoords (polygons),
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
    same as getPolyCoords but for points
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


        
def getPolyCoords(geom, coord_type):
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

