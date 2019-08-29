import geopandas as gpd



gdf = gpd.read_file("./temp_src/prueba.shp")
gdf.to_file("prueba.geojson", driver="GeoJSON")