import os
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
fp_shape = './us_states_shapefiles/s_11au16.shp'
df = pd.read_csv('./output_aggregation_table.csv')

dsets = {'mean_ws_mean-means': {}, 'mean_cf': {}, 'mean_depth': {},
         'mean_lcoe': {'vmin': 0, 'vmax': 300}}

for dset, kwargs in dsets.items():
    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111)

    a = plt.scatter(df.longitude, df.latitude, c=df[dset], s=30,
                    cmap='viridis', marker='s', **kwargs)
    plt.colorbar(a, label=dset)

    is os.path.exists(fp_shape):
        gdf = gpd.GeoDataFrame.from_file(fp_shape)
        gdf = gdf.to_crs({'init': 'epsg:4326'})
        gdf.geometry.boundary.plot(ax=ax, color=None, edgecolor='k',
                                   linewidth=0.5)
        ax.set_aspect(1.3)

    lim_buff = 0.5
    plt.xlim(df.longitude.min() - lim_buff, df.longitude.max() + lim_buff)
    plt.ylim(df.latitude.min() - lim_buff, df.latitude.max() + lim_buff)
    plt.savefig('./{}.png'.format(dset), bbox_inches='tight')
    plt.close()
