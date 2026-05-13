import gzip
import shutil

with gzip.open('wikiElec.ElecBs3.txt.gz', 'rb') as f_in:
    with open('wikiElec.ElecBs3.txt', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)