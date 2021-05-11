#Upload laz after creating in R
import requests
import glob
import os

def upload(path):
    """Upload an item to zenodo"""
    
    token = os.environ.get('ZENODO_TOKEN')
    
     # Get the deposition id from the already created record
    deposition_id = "4746605"
    data = {'name': os.path.basename(path)}
    files = {'file': open(path, 'rb')}
    r = requests.post('https://zenodo.org/api/deposit/depositions/%s/files' % deposition_id,
                      params={'access_token': token}, data=data, files=files)
    print("request of path {} returns {}".format(path, r.json()))
    
files = glob.glob("/orange/idtrees-collab/zenodo/training/*.laz")
for f in files:
    print(f)
    try:
        upload(f)
    except Exception as e:
        print(e)