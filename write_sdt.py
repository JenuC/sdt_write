import numpy as np

# Requires the "sdtheader.dat" built header information

### Example1 : random dataset
#binary_data=(np.random.randint(100,size=[256*256*256])).astype(np.uint16)

### Example2 : any data set with 256x256x256 - uint16
with open('badger.dat','rb') as fid:
    binary_data=np.fromstring(fid.read(),np.uint16)    

#phantom_data= binary_data.ravel().astype(np.uint16)
    
with open('sdtheader.dat','rb') as fid:
    header_=fid.read() # prebuilt header_file for all 256x256 files

phantom_data=''.join([header_,binary_data.tobytes()])

with open('phantom_data.sdt','wb') as fid:
    fid.write(phantom_data)
