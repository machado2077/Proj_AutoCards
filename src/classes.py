from time import sleep
from abc import ABC, abstractmethod
from selenium.webdriver import Firefox
from .funcs import os, get_from_txt, get_imgs_name, remove_imgs_list, shelve



class FlashCard:
    """
        Classe que representa um objeto Flash Card, que são cartões utilizados em revisões espaçadas e que possuem o conteúdo estudado na parte da frente e sua "resposta na parte de trás."""
        
    def __init__(self, front: str, back: str) -> None:
        self.front = front
        self.back = back



class MyCard(FlashCard):
    
    _DEFAULT_BACK = '*CONFIRA NO DICIONÁRIO CONFIGURADO OU NA FERRAMENTA DE TRADUÇÃO*'    

    def __init__(self, front: str, source: str) -> None:
        super().__init__(front, back=self._DEFAULT_BACK)
        self.source = source
        self.inserted = False

    @property
    def representation(self):
        return str({'front': self.front, 'back': self.back, 'source': 
        self.source, 'inserted': self.inserted})


class AbstraticSource(ABC):    

    @abstractmethod
    def return_sources(self):
        ...


    @abstractmethod
    def update_sources(self):
        ...



class TextSourceAdmin(AbstraticSource):

    def __init__(self, card_source):
        self.card_source = card_source
        
    
    def return_sources(self):
        """
            Retorna o caminho do arquivo de texto"""
        return self.card_source


    def update_sources(self, phrases: list) -> None:
        with open(self.card_source, 'w') as source:
            for phrase in phrases:
                source.write(f'{phrase}\n')



class GeneralSourceAdmin(TextSourceAdmin): 
    
    def __init__(self, card_type: str, card_source: str) -> None:
        self.card_type = card_type
        self.card_source = card_source
        
    
    def return_sources(self) -> 'Implementação da superclasse':        
        if self.card_type == 'text':
            return TextSourceAdmin.return_sources(self)


    def update_sources(self, cards: list) -> 'Implementação da superclasse':
        for_update = []
        if self.card_type == 'text':
            for card in cards:
                if card.inserted == False:
                    for_update.append(card.front)    
            return TextSourceAdmin.update_sources(self, for_update)



class AbstraticCardWriter(ABC):    
    
    @abstractmethod
    def get_phrases(self):
        ...

    @abstractmethod
    def write(self):
        ...



class TextCardWriter(AbstraticCardWriter):
    
    def get_phrases(self, source):
        phrases = get_from_txt(source)
        return phrases


    def write(self, phrase, source):
        return MyCard(phrase, source)    



class ImageCardWriter(AbstraticCardWriter):
    #TODO: type annotations após finalizar o método
    def get_phrases(self, source):
        return print('obtendo frases...')


    def write(self, phrase, source):
        return print('escrevendo card...')



class CardWriterAdmin(TextCardWriter, ImageCardWriter):

    def __init__(self, card_type: str, card_source: str) -> None:
        self.card_type = card_type
        self.card_source = card_source        


    def write(self, phrase: str, source: str) -> 'Implementação da superclasse':
        if self.card_type == 'text':
            return TextCardWriter.write(self, phrase, source)
        else:
            return ImageCardWriter.write(self, phrase, source)



class DataBaseAdmin(AbstraticSource):
    
    def __init__(self, db_cards: str, db_key: str) -> None:
        self.db_cards = db_cards
        self.db_key = db_key
        self._database = shelve        
        

    def _verify_key(self) -> None:
        with self._database.open(self.db_cards) as db:            
            if not self.db_key in db.keys():
                db[self.db_key] = []            


    def update_sources(self, cards: list) -> None:
        self._verify_key()
        with self._database.open(self.db_cards) as db:
            cards_temp = db[self.db_key]
            cards_temp.extend(
                [ card for card in cards if card.inserted == False ]
            )
            db[self.db_key] = cards_temp
    

    def return_sources(self) -> list:
        self._verify_key()
        with self._database.open(self.db_cards) as db:
            cards_list = db[self.db_key]
        return cards_list



class ContextManager(
    
    CardWriterAdmin, GeneralSourceAdmin, DataBaseAdmin
    
    ):    

    def __init__(self, card_type: str, card_source: str,
                db_cards: str, db_key: str) -> None:
        
        if not (card_type == 'text' or card_type == 'image'):                    
            raise Exception('card_type should be "text" or "image"')

        super().__init__(card_type, card_source)
        DataBaseAdmin.__init__(self, db_cards, db_key)
        self.cards_list = []            


    def create_card(self) -> None:        
        self._verify_cards()
        card_src = self.return_sources()
        src = self.card_source
        for phrase in self.get_phrases(card_src):                    
            card = self.write(phrase, src)
            self.cards_list.append(card)
        DataBaseAdmin.update_sources(self, self.cards_list)
                        
    
    def _verify_cards(self) -> None:
        cards = DataBaseAdmin.return_sources(self)
        self.cards_list += [card for card in cards]


    def update_card(self, card: MyCard) -> None:
        for c in self.cards_list:
            if c.representation == card.representation:
                c.inserted = True
                break

    
    def update_sources(self) -> None:
        GeneralSourceAdmin.update_sources(self, self.cards_list)
        DataBaseAdmin.update_sources(self, self.cards_list)


'''class ContextManager:

    def __init__(self, card_type, source):        
        self.card_type = card_type
        self.source = source
        self.cards = []
        self.writer = CardWriterAdmin(card_type, source)
        self.sourceAdmin = SourceAdmin(card_type, source)


    def create_cards(self):
        card_src = self.sourceAdmin.return_sources()
        for phrase in self.writer.get_phrases(card_src):
            card = self.writer.write(phrase, card_src)
            #dBAdmin.algumacoisa(card)
            self.cards.append(card)
'''
       

class AnkiBot:
    """
        Classe responsável pelo bot que insere os AutoCards na plataforma Anki"""

    def __init__(self, card_type, card_source, db_cards, db_key):                   
       self.contextManager = ContextManager(
                                card_type, card_source,
                                db_cards,db_key)

    def start(self, login_path: str='') -> None:
        """
            Método responsável pela interação com a plataforma Anki, desde o login até a inserção dos conteúdos que compõe o flash card.

            Arguments:
                gen_type {str} -- txt: Em texto;    img: Em imagem"""                
        #TODO: REALIZAR A TRATATIVA CASO NÃO HAJA CARDS
        self.contextManager.create_card()
        created_cards = self.contextManager.cards_list
        if len(created_cards) == 0:
            print('Sem cards para inserir')
            return

        #SETTINGS
        if login_path != '':
            em, pw = get_from_txt(login_path)
        else:
            em, pw = get_from_txt('login.txt')        
        url = 'https://ankiweb.net/account/login'                
        try:
            browser = Firefox()
            browser.implicitly_wait(30)
            browser.get(url)            
        except Exception as err:
            browser.close()
            print('NÃO FOI POSSÍVEL CONECTAR\n', err)
            input('\n\nPressione a tecla enter.')
            print('\nFINALIZANDO...')
        else:                    
            #LOGIN
            browser.find_element_by_css_selector('input[id="email"]').send_keys(em)
            browser.find_element_by_css_selector('input[type="password"]').send_keys(pw)
            browser.find_element_by_css_selector('input[type="submit"]').click()
            sleep(1)

            #ADD BUTTON
            browser.find_elements_by_css_selector('a[class="nav-link"]')[1].click()
            sleep(1)
        
            #INPUT FLASHCARDS
            for card in created_cards:
                try:
                    browser.find_element_by_id('f0').send_keys(card.front)

                    browser.find_element_by_id('f1').send_keys(card.back)
                
                    browser.find_element_by_css_selector('button[class$="primary"]').click()
                    sleep(1)                        
            
                except Exception as err:
                    print(err)
                
                else:
                    self.contextManager.update_card(card)
            
        finally:
            self.contextManager.update_sources()
            browser.quit()

