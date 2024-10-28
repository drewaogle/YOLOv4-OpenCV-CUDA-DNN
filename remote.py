from dnn_inference import YOLOv4
import urllib3
from pathlib import Path
import io,hashlib, hmac

class RemoteYOLOv4(YOLOv4):
    root="https://aperturedata-public.s3.us-west-2.amazonaws.com/aperturedb_applications/"
    files={
            "coco.names":"634a1132eb33f8091d60f2c346ababe8b905ae08387037aed883953b7329af84",
            "yolov4-tiny.cfg": "6cbf5ece15235f66112e0bedebb324f37199b31aee385b7e18f0bbfb536b258e",
            "yolov4-tiny.weights": "cf9fbfd0f6d4869b35762f56100f50ed05268084078805f0e7989efe5bb8ca87",
            "yolov4.cfg": "a15524ec710005add4eb672140cf15cbfe46dea0561f1aea90cb1140b466073e",
            "yolov4.weights": "8463fde6ee7130a947a73104ce73c6fa88618a9d9ecd4a65d0b38f07e17ec4e4"
            }
    chunk_size = 1024*128
    output_path="./models"

    def __init__(self,args=None):
        print("REMOTEYOLO")
        self.http = urllib3.PoolManager()
        for f in self.files.keys():
            disk_path=Path(self.output_path).joinpath(f)
            disk_path.absolute().parent.mkdir( exist_ok=True)
            self.download_file( self.root+f, disk_path, self.files[f])
        super().__init__(args)

    def download_file(self, from_path, to_path, expected_sha256 ):
        if to_path.exists():
            with open( to_path,"rb") as hash_file:
                sha = hashlib.sha256()
                while True:
                    data = hash_file.read(1024*64)
                    if not data:
                        break
                    sha.update(data)
                if sha.hexdigest() == expected_sha256:
                    return
                else:
                    print(f"Digest = {sha.hexdigest()} vs {expected_sha256}: Hash failed, aborting!") # we could delete and redownload.
                    sys.exit(1)

        req = self.http.request('GET', from_path, preload_content=False)
        with open( to_path, 'wb') as out:
            while True:
                data = req.read(self.chunk_size)
                if not data:
                    break
                out.write(data)
        req.release_conn()
