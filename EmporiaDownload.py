from datetime import datetime
from datetime import timedelta
from pyemvue.pyemvue import PyEmVue
import sys

def collectChannel( vue, device, t1, t2, fln ):
    'Request the data from the API and write it to the file'
    w = open(fln, 'w')

    w.write("UT")
    for ch in device.channels:
        try: 
            w.write(',')
            w.write('%s(kW/h)' % ch.name)
        except:
            print('**** Bad start', file=sys.stderr)
            stop
    w.write('\n')

    data = {}
    for ch in device.channels:
        data[ch] = vue.get_chart_usage(ch, t1, t2)

    nrec = len(data[device.channels[0]][0])
    ndev = len(device.channels)
    for i in range(nrec):
        xx = t1 + timedelta(seconds=i)
        w.write(xx.strftime('%Y-%m-%dT%H:%M:%SZ'))
        for j in range(ndev):
            d = data[device.channels[j]][0][i]
            if (d == None):
                w.write(',***')
            else:
                w.write(',%f' % (d * 3600))
        w.write('\n')
    
def main(argv):
    
    datahome = argv[0] if len(argv) == 1 else "/tmp/emporia/"
    print('datahome=' + datahome, file=sys.stderr)
    
    vue = PyEmVue() 
    vue.login(username='', password='', token_storage_file='/home/jbf/tmp/keys.json')

    t2 = datetime.utcnow()
    print('utcnow=' + str(t2), file=sys.stderr)
    
    sinceHour = timedelta(minutes=t2.minute, seconds=t2.second, microseconds=t2.microsecond)
    t2 = t2 - sinceHour
    print('t2=' + str(t2), file=sys.stderr)
    t1 = t2 - timedelta(hours=1)

    path = t1.strftime(datahome + '%Y/%m/%d/')

    import os
    if not os.path.exists(path):
        os.makedirs(path)

    devices = vue.get_devices()

    fln = path + t1.strftime('%Y%m%dT%H.csv')
    device = devices[-1]
    collectChannel( vue, device, t1, t2, fln )

    fln = path + t1.strftime('%Y%m%dT%H_all.csv')
    device = devices[0]
    collectChannel( vue, device, t1, t2, fln )

if __name__ == "__main__":
    main( sys.argv[1:] )

