# must be called as we're using zipped requirements
try:
    import unzip_requirements
except ImportError:
    pass

import json
import pandas as pd

def hello(event, context):
    print("In......")
    df = pd.DataFrame(data={"name":["Soumil", "Nitin"]})
    print(df)
    print("\n")
    print(df.shape)

    response = {
        "statusCode": 200,
        "body": json.dumps("hEllo")
    }

