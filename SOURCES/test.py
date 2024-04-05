from PATHS import *

ldk = PathQuery('SOURCES/input/paths.json')
ldk.outputAsGeoJSON(ldk.searchBy(RouteId = '128', RouteVarId = '256'), 'SOURCES/output/geotest.json')