from pyemvue.pyemvue import PyEmVue
from datetime import timedelta,datetime

import sys

def main(argv):
    
    datahome= argv[0] if len(argv)==1 else "/home/jbf/data/emporia/"
    print('datahome='+datahome)
    
    vue = PyEmVue() 
    vue.login(username='', password='', token_storage_file='/home/jbf/tmp/keys.json')

    t2= datetime.utcnow()
    print('utcnow='+str(t2))
    
    sinceHour= timedelta( minutes=t2.minute, seconds=t2.second, microseconds=t2.microsecond )
    t2= t2 - sinceHour
    print('t2='+str(t2))
    t1= t2 - timedelta(hours=1)

    path= t1.strftime( datahome + '%Y/%m/%d/' )
    fln= path + t1.strftime( '%Y%m%dT%H.csv')

    import os
    if not os.path.exists(path):
        os.makedirs(path)

    w= open(fln,'w')

    devices = vue.get_devices()
    device= devices[-1]

    w.write( "UT" )
    for ch in device.channels:
        try: 
            w.write(',')
            w.write( '%s(kW/h)' % ch.name )
        except:
            print('**** Bad start')
            stop
    w.write('\n')

    data= {}
    for ch in device.channels:
        data[ch]= vue.get_chart_usage( ch, t1, t2 )

    nrec= len(data[device.channels[0]][0])
    ndev= len(device.channels)
    for i in range(nrec):
        xx= t1 + timedelta(seconds=i)
        w.write( xx.strftime( '%Y-%m-%dT%H:%M:%SZ' ) )
        for j in range(ndev):
            d= data[device.channels[j]][0][i]
            if ( d==None ):
                w.write(',***')
            else:
                w.write(',%f' % (d*3600))
        w.write('\n')

if __name__ == "__main__":
    main( sys.argv[1:] )

