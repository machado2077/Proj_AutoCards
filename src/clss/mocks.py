from typing import List
from src.funcs.imgFuncs import get_imgs_path, remove_imgs_list
from src.funcs.textFunc import get_from_json


class MockImageSource:
    def __init__(self, img_path_file: str):
        self.source = get_from_json(img_path_file, 'imgPath')
    
    def get_images(self) -> List[str]:        
        imgs_data = []
        paths = get_imgs_path(self.source)
        for path in paths:            
            _bytes = bytes(path, encoding='utf-8')
            imgs_data.append(
                {'bytes': _bytes, 'source': path}
            )
        return imgs_data

    def remove_images(self, img_list: List[str]) -> None:
        ...
