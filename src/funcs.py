import os, requests, json

def get_from_txt(file='frases.txt'):    
    """
        Função que obtém frases de um arquivo .txt. Essa obtenção se dá orientada ao caractere de quebra de linha \\n. A função também realiza tratamento de espaços em branco a cada frase obtida e, se houver no arquivo apenas espaços em branco, o retorno será uma lista vazia.

        Keyword Arguments:
            file {str} -- nome do arquivo que contém as frases. 
            (default: {'frases.txt'})

        Returns:
            list -- lista contendo as frases obtidas do arquivo."""
    while True:
        if os.path.isfile(file) and str(file).endswith('.txt'):            
            with open(file, 'r') as f:                
                phrases = [line.strip() for line in f.read().split('\n') if line.strip() != '']        
                return phrases  
        else:
            print(f'\n\n"{file}" não é um arquivo ou um path de arquivo válido.')
            file = input('\nInsira um arquivo existente no mesmo path da VENV ou insira um path de arquivo válido: ')


def get_imgs_name(folder_path):
    if not os.path.isdir(folder_path):
        print(f'"{folder_path}" não é um diretório.')
    files = []
    for file in os.listdir(folder_path):
        if file.endswith('.png') or file.endswith('.jpg'):
            files.append(os.path.join(folder_path, file))
    return files

#api_key = '22cd3eed8288957'

def get_from_img(filename, overlay=False, api_key='22cd3eed8288957', language='eng'):        
    payload = {'isOverlayRequired': overlay,
               'apikey': api_key,
               'language': language,
               }
    with open(filename, 'rb') as f:
        try:
            r = requests.post('https://api.ocr.space/parse/image',
                            files={filename: f},
                            data=payload,
                            )
        except Exception as err:
            print(err)
            return 
        else:
            results = json.loads(r.content.decode())
            text = results.get('ParsedResults')[0]['ParsedText'].replace('\n', '').replace('\r', ' ').strip()
            
    return (text, filename)



def remove_imgs(folder_path):
    if not os.path.isdir(folder_path):
        print(f'"{folder_path}" não é um diretório.')
    for file in os.listdir(folder_path):
        if file.endswith('.png') or file.endswith('.jpg'):
            os.unlink(os.path.join(folder_path, file))


def remove_imgs_list(imgs_list):
    for img_path in imgs_list:
        if os.path.isfile(img_path) and (img_path.endswith('.png') or img_path.endswith('.jpg')):
            os.unlink(img_path)
        

def verify_mnt(source):
   if len(os.listdir(source)) == 0:
      os.system(f'google-drive-ocamlfuse /{source}')

#FUNÇÃO PARA OBTER AS IMAGENS DO DIRETÓRIO MONTADO gdrive

"""
- verificar se há o diretório Legendas
   - se não, montar com o comando
- obter o caminho de todas elas as imagens -> get_imgs_name
- realizar o processo de extração do textos
- excluir as imagens -> remove_imgs_list

"""
