import os
import io
import re
from unittest import TestCase, mock, main

from src.clss.cards import MyCard
from src.clss.autoFlashCards import AutoFlashCards
from src.clss.cardWriter import DictBasedCardWriter
from src.clss.cardDeliverers import SeleniumAnkiBot
from src.clss.assistants import AnkiEditPageHandler
from src.clss.webDriverConfigurator import WebDriverConfigurator
from src.clss.error import DataConfigError
from src.clss.configurators import AppConfigurator
from src.clss.imageSources import LocalFolderSource
from src.clss.mocks import (MockImageSource, 
                            MockWebDriverConfigurator,
                            MockGoogleVision)
from src.clss.sourceAdmins import (MyCardShelveAdmin, 
                                    TextSourceAdmin, 
                                    ImageSourceAdmin)

from src.funcs.textFunc import get_from_txt
from src.funcs.resetSamplesFuncs import text_source_reset, db_cards_reset

from . import SAMPLE_FOLDER, config_file_path, filled_text_path, empty_text_path, img_folder_path



class TestDictBasedCardWriter(TestCase):
    def setUp(self):
        self.source = filled_text_path
        self.src_before = get_from_txt(self.source)
        self.writer = DictBasedCardWriter()

    def tearDown(self):
        text_source_reset(self.source, self.src_before)        

    def test_update_contents_works(self):
        phrases = self.src_before
        for phrase in phrases:
            self.writer.update_contents(
                phrase, self.source
            )
        expected = [
            {'phrase': phrase, 'source': self.source} for phrase in phrases
        ]
        self.assertEqual(expected, self.writer.contents)
    
    def test__return_written_cards_returns_equal_amount_src(self):
        phrases = self.src_before
        for phrase in phrases:
            self.writer.update_contents(phrase, self.source)
        card_list = self.writer.return_written_cards()
        expected = len(card_list)
        self.assertEqual(expected, len(self.src_before))

    def test_return_written_cards_returns_MyCard_instances(self):
        phrases = self.src_before
        for phrase in phrases:
            self.writer.update_contents(phrase, self.source)
        card_list = self.writer.return_written_cards()
        for card in card_list:
            self.assertEqual(isinstance(card, MyCard), True)



class TestTextSourceAdmin(TestCase):
    def setUp(self):
        self.source = filled_text_path
        self.src_before = get_from_txt(self.source)
        self.writer = DictBasedCardWriter()
        self.sourceAdmin = TextSourceAdmin(config_file_path, self.writer)

    def tearDown(self):
        text_source_reset(self.source, self.src_before)        
    
    def test__update_cards_clear_all_phrases_in_file(self):
        self.sourceAdmin.return_sources()        
        self.sourceAdmin.update_sources()
        expected = get_from_txt(self.source)
        self.assertEqual(expected, [])        

    def test__return_sources_returns_equal_amounts_src(self):
        card_list = self.sourceAdmin.return_sources()
        expected = len(card_list)        
        self.assertEqual(expected, len(self.src_before))

    def test_return_sources_returns_empty_list_if_empty_texts_src(self):
        self.sourceAdmin.source = empty_text_path
        expected = self.sourceAdmin.return_sources()
        text_source_reset(empty_text_path, [])
        self.assertEqual(expected, [])
        
    def test__update_sources_returns_None_if_empty_text_src(self):
        self.sourceAdmin.source = empty_text_path
        expected = self.sourceAdmin.update_sources()
        text_source_reset(empty_text_path, [])
        self.assertEqual(expected, None)



class TestMyCardShelveAdmin(TestCase):    
    def setUp(self):
        self.db_source = os.path.join(SAMPLE_FOLDER, "db_cards_test")
        self.db_key = "test_key"
        self.db_source_before = []
        self.text_src = filled_text_path
        self.text_src_before = get_from_txt(self.text_src)
        writer = DictBasedCardWriter()
        self.textAdmin = TextSourceAdmin(config_file_path, writer)
    
    def tearDown(self):
        db_cards_reset(
            self.db_source, self.db_key, 
            self.db_source_before)
        text_source_reset(
            self.text_src, 
            self.text_src_before)

    def test__storage_card_works_for_created_cards(self):        
        db = MyCardShelveAdmin(self.db_source, self.db_key)
        cardsList_1 = self.textAdmin.return_sources()
        db.update_sources(cardsList_1)
        cardsList_2 = db.return_sources()
        cards = [card.representation for card in cardsList_1]
        expected = [card.representation for card in cardsList_2]        
        self.assertEqual(expected, cards)

    def test__update_source_when_all_cards_was_inserted(self):
        db = MyCardShelveAdmin(self.db_source, self.db_key)
        card_list = self.textAdmin.return_sources()
        db.update_sources(card_list)
        for card in card_list:
            card.inserted = True
        db.update_sources(card_list)
        expected = db.return_sources()
        self.assertEqual(expected, [])
    
    def test__update_source_when_last_card_was_not_inserted(self):
        db = MyCardShelveAdmin(self.db_source, self.db_key)
        card_list = self.textAdmin.return_sources()
        db.update_sources(card_list)
        for i in range(len(card_list) - 1):
            card_list[i].inserted = True
        last_card = card_list[-1].representation
        db.update_sources(card_list)
        db_return = db.return_sources()
        expected = db_return[0].representation
        self.assertEqual(expected, last_card)

    def test__update_source_returns_None_when_no_given_cards(self):
        EMPTY_LIST = []
        db = MyCardShelveAdmin(self.db_source, self.db_key)
        expected = db.update_sources(EMPTY_LIST)
        self.assertEqual(expected, None)



class TestSeleniumAnkiBot(TestCase):
    def setUp(self):
        self.text_src = filled_text_path
        self.text_src_before = get_from_txt(self.text_src)
        writer = DictBasedCardWriter()
        self.sourceAdmin = TextSourceAdmin(config_file_path, writer)

    def tearDown(self):
        text_source_reset(self.text_src, self.text_src_before)
                
    def test__update_card_update_card_inserted_status(self):
        card = MyCard('_', '_')
        deliverer = SeleniumAnkiBot('_', '_')        
        deliverer._card_list.append(card)
        deliverer._update_card(card)
        expected = deliverer.card_list[0].inserted
        self.assertEqual(expected, True)   



class TestAutoFlashCards(TestCase):
    def setUp(self):
        self.text_src = filled_text_path
        self.text_src_before = get_from_txt(self.text_src)
        writer = DictBasedCardWriter()
        self.textAdmin = TextSourceAdmin(config_file_path, writer)
        self.db_source = os.path.join(SAMPLE_FOLDER, "db_cards_test")
        self.db_key = "test_key"
        self.db_source_before = []
        self.db_admin = MyCardShelveAdmin(self.db_source, self.db_key)

    def tearDown(self):
        db_cards_reset(self.db_source, 
                        self.db_key, 
                        self.db_source_before)
                    
        text_source_reset(self.text_src, self.text_src_before)    

    def test__verify_cards_returns_empty_cards_list(self):        
        ac = AutoFlashCards('_', '_', self.db_admin)
        ac._verify_cards()
        expected = ac.card_list
        self.assertEqual(expected, [])

    def test__card_list_append_created_cards_from_db(self):     
        card_list = self.textAdmin.return_sources()
        card_repr = [card.representation for card in card_list]
        db = self.db_admin
        db.update_sources(card_list)
        ac = AutoFlashCards('_', '_', self.db_admin)
        ac._verify_cards()        
        expected = [card.representation for card in ac.card_list]
        self.assertEqual(expected, card_repr)
    
    @mock.patch('src.clss.sourceAdmins.DictBasedCardWriter.update_contents')
    def test__cards_list_append_written_cards(self, mocked):    
        ac = AutoFlashCards('_', self.textAdmin, self.db_admin)
        ac.create_cards()
        expected = mocked.call_count
        self.assertEqual(expected, len(self.text_src_before))    

    @mock.patch('src.clss.cardDeliverers.SeleniumAnkiBot.deliver')
    def test__deliver_method_is_called_in_run_task_method(self, mocked):        
        deliver = SeleniumAnkiBot('_', '_')        
        ac = AutoFlashCards(deliver, self.textAdmin, self.db_admin)
        ac.run_task()
        mocked.assert_called_once_with(ac._card_list)        
        
    @mock.patch('src.clss.cardDeliverers.SeleniumAnkiBot.deliver')
    def test__run_task_returns_None_if_no_text_phrases(self, mocked):
        writer = DictBasedCardWriter()
        textAdm = TextSourceAdmin(config_file_path, writer)
        textAdm.source = empty_text_path
        ac = AutoFlashCards('_', textAdm, self.db_admin)
        ac.run_task()
        mocked.assert_not_called()



class TestImageSourceAdmin(TestCase):
    def setUp(self):
        path = config_file_path
        self.mockImgSource = MockImageSource(path)
        self.writer = DictBasedCardWriter()

    @mock.patch('src.clss.mocks.MockGoogleVision.img_to_str')
    def test__return_source_method_call_img_to_str_method(self, mocked):
        extractor = MockGoogleVision()
        imgAdmin = ImageSourceAdmin(self.mockImgSource, self.writer, extractor)
        imgAdmin.return_sources()
        expected = mocked.call_count
        self.assertEqual(expected, 2)

    @mock.patch('src.clss.mocks.MockImageSource.remove_images')
    def test__remove_imgs_was_called_with_imgs_list(self, mocked):
        imgs_list = self.mockImgSource.get_images()
        imgAdmin = ImageSourceAdmin(self.mockImgSource, self.writer, '_')
        for path in imgs_list:
            imgAdmin.writer.update_contents('', path)
        imgAdmin.update_sources()
        mocked.assert_called_once_with(imgs_list)


class TestWebDriverConfigurator(TestCase):
    def setUp(self):
        self.wdconfig = WebDriverConfigurator(config_file_path)

    def test__browser_name_return_correct_driver(self):
        self.wdconfig._browser_import_handler()
        expected = self.wdconfig.web_driver_settings["driver"]
        from selenium.webdriver import Chrome
        self.assertEqual(expected, Chrome)

    def test_web_drvr_options_setted_returns_Options_instance(self):
        self.wdconfig._web_driver_options_handler()
        expected = self.wdconfig.web_driver_settings\
                    ["web_driver_args"]["options"]
        self.assertTrue(expected.headless)
        from selenium.webdriver.chrome.options import Options
        self.assertEqual(type(expected), Options)

    def test_web_driver_args_keep_alive(self):
        self.wdconfig._set_web_drive_args_handler()
        expected = self.wdconfig.web_driver_settings\
                    ["web_driver_args"]["keep_alive"]
        self.assertEqual(expected, False)

    def test_web_driver_manager_install_imports_manager(self):
        self.wdconfig._install_driver_handler =\
        MockWebDriverConfigurator._mock_install_driver_handler
        expected = self.wdconfig._install_driver_handler(self.wdconfig)
        from webdriver_manager.chrome import ChromeDriverManager
        self.assertEqual(expected, ChromeDriverManager)

    @mock.patch('src.clss.webDriverConfigurator.WebDriverConfigurator._browser_import_handler')
    @mock.patch('src.clss.webDriverConfigurator.WebDriverConfigurator._install_driver_handler')
    @mock.patch('src.clss.webDriverConfigurator.WebDriverConfigurator._set_web_drive_args_handler')
    @mock.patch('src.clss.webDriverConfigurator.WebDriverConfigurator._web_driver_options_handler')
    def test_handlers_are_called_when_config_settings_running(self, mocked1, mocked2, mocked3, mocked4):
        self.wdconfig.config_settings()
        mocked1.assert_called_once()
        mocked2.assert_called_once()
        mocked3.assert_called_once()
        mocked4.assert_called_once()

    def test_raise_error_when_wrong_browser_name(self):
        self.wdconfig._user_settings["browser"] = "err"
        with self.assertRaises(DataConfigError):
            self.wdconfig._browser_import_handler()



class TestAppConfigurator(TestCase):
    def setUp(self):
        self.appConfig = AppConfigurator(config_file_path)
    
    def test_returns_configured_application(self):
        app = self.appConfig.configure(SAMPLE_FOLDER)
        file = app.__file__
        expected = os.path.join(SAMPLE_FOLDER, 'app_test.py')
        self.assertTrue(file.endswith(expected))

    def test_AutoFlashCard_assignment(self):
        app = self.appConfig.configure(SAMPLE_FOLDER)
        expected = type(app.automaton)
        self.assertEqual(expected, AutoFlashCards)

    def test_raise_error_if_not_given_name(self):
        file = 'config_with_no_app_name.json'
        path = os.path.join(SAMPLE_FOLDER, file)
        self.appConfig.app_config = "err"
        with self.assertRaises(DataConfigError):
            self.appConfig.configure(SAMPLE_FOLDER)
        


class TestLocalFolderSource(TestCase):
    def setUp(self):
        self.source = LocalFolderSource(config_file_path)
    
    def test_get_images(self):
        imgs_name = [
            os.path.basename(i.source) 
            for i in self.source.get_images()
            ]
        self.assertIn('img1.jpg', imgs_name)
        self.assertIn('img2.jpg', imgs_name)
    
    def test_wrong_folder_raises_error(self):
        self.source.folder_source = 'err'
        with self.assertRaises(DataConfigError):
            self.source.get_images()

    @mock.patch('src.clss.imageSources.os.remove')
    def test__remove_all_two_imgs(self, mocked):
        img_list = self.source.get_images()
        self.source.remove_images(img_list)
        expected = mocked.call_count
        self.assertEqual(expected, 2)
        


if __name__ == "__main__":
    main()

