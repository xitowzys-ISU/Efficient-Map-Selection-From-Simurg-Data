import time
import h5py
import pytz
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timezone


class Simurg:
    def __init__(self, pth):
        self.pth = pth
        self.f = h5py.File(self.pth, 'r')

    def __del__(self):
        self.f.close()

    # Возвращает станции приема спутников
    def getSites(self):
        sites = [site for site in self.f]
        return sites

    # Возвращает спутники
    def getSats(self, site):
        sats = [sat for sat in self.f[site]]
        return sats

    def getData(self, site, sat, field):
        if site in self.f and sat in self.f[site]:
            times = self.f[site][sat][field][:]
        return times

    def getSeries(self, site, sat, field):
        ts = self.getData(site, sat, 'timestamp')
        data = self.getData(site, sat, field)
        return ts, data

    def getMap(self, time, field):
        result = []
        timestamp = time.timestamp()
        start = timestamp
        end = timestamp
        sites = self.getSites()
        for site in sites:
            lat = np.degrees(self.f[site].attrs['lat'])
            lon = np.degrees(self.f[site].attrs['lon'])
            sats = self.getSats(site)
            for sat in sats:
                timestamps = self.getData(site, sat, 'timestamp')
                data = self.getData(site, sat, field)
                match = np.where((timestamps >= start) & (timestamps <= end))
                data_match = data[match]
                for d in data_match:
                    result.append((d, lon, lat))
        if not result:
            return None
        else:
            return np.array(result)


if __name__ == "__main__":
    print("Start program")
    simurg = Simurg('2020-05-20.h5')

    plot_map = True

    if not plot_map:
        timestamps, data = simurg.getSeries('arsk', 'G03', 'dtec_20_60')
        times = [datetime.fromtimestamp(t, pytz.utc) for t in timestamps]
        plt.scatter(times, data)
        plt.xlim(times[0], times[-1])
        plt.show()
    else:
        epoch = datetime(2020, 5, 20, 12, 30, 0, tzinfo=timezone.utc)
        before = time.time()
        data = simurg.getMap(epoch, 'dtec_20_60')
        print(f'It took {time.time() - before} sec. to retrieve a map')
        val = data[:, 0]
        x = data[:, 1]
        y = data[:, 2]
        plt.scatter(x, y, c=val)
        plt.xlim(-180, 180)
        plt.ylim(-90, 90)
        plt.show()
