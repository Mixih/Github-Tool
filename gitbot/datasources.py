import csv


class CSVDataSource:

    def __init__(self, datafile):
        self.datafile = datafile
        # test opent he file to make sure it exists
        open(self.datafile, 'r').close()

    def get_users(self, usercol, namecol):
        with open(self.datafile, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield (row[usercol], row[namecol])
