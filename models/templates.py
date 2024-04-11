import numpy as np
import pandas as pd
from pandas import DataFrame
from pydantic import BaseModel

class RegularUnits(BaseModel):
    tech: int = 0
    workers: int = 0

class ManagementCompany(RegularUnits):
    name: str

class TemporaryTable:

    @staticmethod
    def creating_temporary_table() -> DataFrame:
        names_of_columns = ['technique', 'workers']
        names_of_rows = ['City_roads', 
                        'Regional_roads', 
                        'Courtyard_territories', 
                        'Villages_territories'
                        ]
        data = {'technique': [0] * 4, 
                'workers': [0] * 4
                }
        temporary_table = pd.DataFrame(data, 
                                    index=names_of_rows, 
                                    columns=names_of_columns, 
                                    dtype=np.int8
                                    )
        return temporary_table