import time
import h5py 
import pytz
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timezone

# Получение спутников
def get_sites(pth):
    with h5py.File(pth, 'r') as f:
        sites = [site for site in f]
    return sites


def get_sats(pth, site, fhdf=None):
    f = h5py.File(pth, 'r') if not fhdf else fhdf
    if site in f:
        sats = [sat for sat in f[site]]
    if not fhdf:
        f.close()
    return sats


def get_data(pth, site, sat, field, fhdf=None):
    f = h5py.File(pth, 'r') if not fhdf else fhdf
    if site in f and sat in f[site]:
        times = f[site][sat][field][:]
    if not fhdf:
        f.close()
    return times


def get_series(pth, site, sat, field):
    ts = get_data(pth, site, sat, 'timestamp')
    data = get_data(pth, site, sat, field)
    return ts, data


def get_map(pth, time, field):
    result = []
    timestamp = time.timestamp()
    start = timestamp
    end = timestamp
    sites = get_sites(pth)
    f = h5py.File(pth, 'r')
    for site in sites:
        lat = np.degrees(f[site].attrs['lat'])
        lon = np.degrees(f[site].attrs['lon'])
        sats = get_sats(pth, site, fhdf=f)
        for sat in sats:
            timestamps = get_data(pth, site, sat, 'timestamp', fhdf=f)
            data = get_data(pth, site, sat, field, fhdf=f)
            match = np.where((timestamps >= start) & (timestamps <= end))
            data_match = data[match]
            for d in data_match:
                result.append((d, lon, lat))
    if not result:
        return None
    else:
        return np.array(result)
        


if __name__ == '__main__':
    plot_map = True
    pth = '2020-05-20.h5'
    if not plot_map:
        timestamps, data = get_series(pth, 'arsk', 'G03', 'dtec_20_60')
        times = [datetime.fromtimestamp(t, pytz.utc) for t in timestamps]
        plt.scatter(times, data)
        plt.xlim(times[0], times[-1])
        plt.show()
    else:
        epoch = datetime(2020, 5, 20, 12, 30, 0, tzinfo=timezone.utc)
        before = time.time()
        data = get_map(pth, epoch, 'dtec_20_60')
        print(f'It took {time.time() - before} sec. to retrieve a map')
        val = data[:, 0]
        x = data[:, 1]
        y = data[:, 2]
        plt.scatter(x, y, c=val)
        plt.xlim(-180, 180)
        plt.ylim(-90, 90)
        plt.show()
    