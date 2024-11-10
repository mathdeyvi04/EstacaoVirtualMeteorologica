import numpy as np
import xarray as xr
import rasterio
from rasterio.transform import from_bounds

# Abrir o arquivo NetCDF
dataset = xr.open_dataset('ABI-L2-LSTF.nc')

# Extração das variáveis relevantes do dataset
LST = dataset['LST'][:]  # Temperatura de superfície
x = dataset['x'][:]  # Coordenadas de varredura x
y = dataset['y'][:]  # Coordenadas de varredura y

# Limites de latitude e longitude (obtidos do dataset)
lon_mais_oeste = -156.2995
lat_mais_norte = 81.3282
lon_mais_leste = -6.2995
lat_mais_sul = -81.3282

# Definir os limites geográficos do dataset
transform = from_bounds(lon_mais_oeste, lat_mais_sul, lon_mais_leste, lat_mais_norte, LST.shape[1], LST.shape[0])

# Salvar o arquivo como GeoTIFF
with rasterio.open(
    'goes16_LST_geotiff.tif', 'w',
    driver='GTiff',
    height=LST.shape[0],
    width=LST.shape[1],
    count=1,  # Quantidade de bandas
    dtype=LST.dtype,
    crs='EPSG:4326',
    transform=transform,
) as dst:
    dst.write(LST, 1)  # Escrever os dados LST na primeira banda

