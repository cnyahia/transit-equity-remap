# CapRemap: Transit Equity Analysis
![net](figs/network.PNG)

To view code, problem description, and *interactive plots*, check out [https://cnyahia.github.io/transit-equity-remap/](https://cnyahia.github.io/transit-equity-remap/).
For more discussion on this analysis visit 

This repository includes equity analysis for CapMetro's restructuring of its transit system in 2018. CapRemap was controversial-- many activists claim that it had a disproportionately adverse impact on minorities.

CapMetro claims that the benefits to minorities far exceeds the negative impact; however, an initial look at CapMetro's service equity analysis (FTA's SAFE analysis) shows that the analysis approach has several limitations:
1. A detailed analysis of changes to the service frequency is lacking
2. A route-level approach is used where a 1/2 mile walk-shed represents the network coverage. While route-level walk-sheds are commonly used, stop-based coverage with buffers of a 1/4 mile radius seems more 
appropriate since customers walk to bus stops (not routes).
3. The routes analyzed were restricted to those that had a greater than 25% change in geographic coverage or service characteristics, where this 25% threshold was set by CapMetro. 
Even after selecting the routes with major changes, they were only analyzed further if the % minority population in the walk-shed was greater than 35%. 
It is not clear if this excludes from the analysis parts of the network that were negatively impacted.
4. CapMetro's method depends on the irregular shapes of census block groups to determine the network coverage, and a block group is assumed to be covered if any part of it overlaps with a route walk-shed. Evidently, the 
network coverage should be restricted to demographics *within* the area of 1/4 mile buffers around stops.

To address those limitations, an alternative stop-level equity analysis is developed. This stop-level analysis maps the demographic characteristics from census-tracts to stop buffers, where the area of intersection between 
the census tracts and the buffers is used to weight the contribution of each tract. Then, for each stop, the change in morning peak service is analyzed. The network level impact on minorities is then measured using stop-level metrics.

The results indicate that CapRemap did not significantly improve service throughout the network. In fact, for all demographics, there was a decrease in the expected number of buses passing during the morning peak. 
Although CapMetro provided a *high frequency network* with improved service on specific routes, these improvements were at the expense of other non-frequent lines. That said, in contrast to activists' claims, there is no clear 
indication that minorities experienced greater service reductions. The fraction of total doors opening (service improvements) that was located in minority areas is similar to the fraction of total doors closing (service reductions) 
that was inflicted on minority areas (i.e., no significant *net* change in AM peak service); this also applies to areas with White people. 