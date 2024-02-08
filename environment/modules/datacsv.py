import pandas as pd
from config.config import CSV_PATH

class CSV:
    def __init__(self, csv_name ):
        self.csv_name=csv_name

    def set_data(self, data=[]):
        df = pd.DataFrame(data)
        df.to_csv( CSV_PATH + "/" + self.csv_name + ".csv", index=False, mode='a', header=False )