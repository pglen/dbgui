import datetime, sys

if __name__ == '__main__':

    # test date consistancy
    dnnn = datetime.datetime.now()
    print("dnnn", dnnn, dnnn.timestamp())

    dsss = datetime.datetime.isoformat(dnnn)
    print("dsss", dsss)
    dddd = datetime.datetime.fromisoformat(dsss)
    print("dddd", dddd, dddd.timestamp())


