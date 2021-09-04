from unittest import TestCase

from models import db,User,VocabularyListName,VocabularyList,Articles,Categories,VocabularyFromArticle,UserFinishReading

from models import ImportArticles,ImportCategory,FinishImportReading,VocabularyFromImportArticle

from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///leetenglish-test"

app.config['TESTING'] = True

app.config['DEBUT_TB_HOSTS'] = ['dont-show-debug-toolbar']

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['WTF_CSRF_ENABLED'] = False

class TestCaseForOwnVocabulary(TestCase):
    """Testing for Your Own Vocabulary Test Case"""
    @classmethod
    def setUpClass(cls):
        db.drop_all()
        db.create_all()
        test_user1 = User.register(
            username="test1",
            email="test1@gmail.com",
            password="test1",
            first="test1",
            last="test1",
            quote="test1",
            sex="F",
            avatar="avatar_test1",
            points=100
            )

        test_user2 = User.register(
            username="test2",
            email="test2@gmail.com",
            password="test2",
            first="test2",
            last="test2",
            quote="test2",
            sex="F",
            avatar="avatar_test2",
            points=101
            )
        db.session.add_all([test_user1,test_user2])
        db.session.commit()

        vocalList1 = VocabularyListName(list_name="test1",description="descriptionTest10",user_id=1)
        vocalList2 = VocabularyListName(list_name="test2",description="descriptionTest20",user_id=1)

        db.session.add(vocalList1)
        db.session.commit()

        db.session.add(vocalList2)
        db.session.commit()

        vocabularyList1 = VocabularyList(
            spell="test1",
            definition="definitionTest1",
            part_of_speech="test1Speech",
            list_id=1)

        vocabularyList2 = VocabularyList(
            spell="test2",
            definition="definitionTest2",
            part_of_speech="test1Speech",
            list_id=1)

        db.session.add_all([vocabularyList1,vocabularyList2])
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.drop_all()

    def test_create_own_vocabulary_list(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"
    
        resp = client.post('/vocabulary/add_list',data={"newList":"listTest1","list_description":"descriptionTest1"},follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn("listTest1",html)

    def test_delete_vocabulary_list(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp1 = client.get('/vocabulary/list/delete/1',follow_redirects=True)
        html = resp1.get_data(as_text=True)

        self.assertEqual(resp1.status_code,200)
        self.assertIn("Vocabulary list delete successful [list_id:1]!",html)

    def test_add_vocabulary(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"
        
        resp = client.post("/vocabulary/definition/list/1",data={"vocabulary":"hello"})
        resp1 = client.post("/vocabulary/definition/list/1",data={"vocabulary":"friend"},follow_redirects=True)
        html = resp1.get_data(as_text=True)

        self.assertEqual(resp.status_code,302)
        self.assertEqual(resp1.status_code,200)
        self.assertIn("hello",html)
        self.assertIn("friend",html)

class TestCaseVocabularyFromArticles(TestCase):

    """Test Case For Vocabulary Articles"""

    @classmethod
    def setUpClass(cls):
        db.drop_all()
        db.create_all()

        test_user1 = User.register(
            username="test1",
            email="test1@gmail.com",
            password="test1",
            first="test1",
            last="test1",
            quote="test1",
            sex="F",
            avatar="avatar_test1",
            points=100
            )

        test_user2 = User.register(
            username="test2",
            email="test2@gmail.com",
            password="test2",
            first="test2",
            last="test2",
            quote="test2",
            sex="F",
            avatar="avatar_test2",
            points=101
            )

        db.session.add_all([test_user1,test_user2])
        db.session.commit()

        test1Category = Categories(
            category="test1",
            description="test1 description"
        )

        test2Category = Categories(
            category="test2",
            description="test2 description"
        )

        db.session.add_all([test1Category,test2Category])
        db.session.commit()

        test1_article = Articles(
            author="test1",
            title="test1Article",
            category=1,
            description="test1 description one",
            cover_url="www.test1.com",
            content="test1 articles content",
            user_id=1
        )

        test2_article = Articles(
            author="test2",
            title="test2Article",
            category=1,
            description="test2 description one",
            cover_url="www.test2.com",
            content="test2 articles content",
            user_id=1
        )

        db.session.add_all([test1_article,test2_article])
        db.session.commit()


        testVolcal1= VocabularyFromArticle(
            spell="test1Spell",
            definition="test1",
            part_of_speech="test1",
            article_id=1,
            user_id=1,
            image_url="www.google.com"
        )

        testVolcal2= VocabularyFromArticle(
            spell="test2Spell",
            definition="test2",
            part_of_speech="test2",
            article_id=1,
            user_id=1,
            image_url="www.google.com"
        )

        db.session.add_all([testVolcal1,testVolcal2])
        db.session.commit()

        test1_finish1 = UserFinishReading(user_id=1,article_id=1)
        db.session.add(test1_finish1)
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.drop_all()

    
    def test_preload_vocabulary_list_work(self):

        """Is the preload vocabulary list works as expects"""

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.get("/vocabulary/article/list/preload")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn("test1Article",html)


    def test_preload_vocabulary_view(self):

        """Testing vocabulary view list"""

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.get("/vocabulary/article/1/list")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn("test1Spell",html)
        self.assertIn("test2Spell",html)

    def test_preload_vocabulary_edit_get(self):
        """Test Preload Vocabulary Edit Testcase"""

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"
        
        resp = client.get('/vocabulary/article/1/list/test1Spell')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn('test1Spell',html)

    def test_preload_vocabulary_edit_post(self):
        """Test Proload Article Edit Post"""

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.post("/vocabulary/article/1/list/test1Spell",data={
            "vocabulary":"test1SpellEdit",
            "partOfSpeech":"test1Edit",
            "definition":"test1EditDefinition",
            "image_url":"test1EditImageUrl"
            },follow_redirects=True)

        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn("test1EditDefinition",html)


class TestCaseVocabularyFromImportArticles(TestCase):
    """Testing Vocabulary From Import Articles"""

    @classmethod
    def setUpClass(cls):
        db.drop_all()
        db.create_all()

        test_user1 = User.register(
            username="test1",
            email="test1@gmail.com",
            password="test1",
            first="test1",
            last="test1",
            quote="test1",
            sex="F",
            avatar="avatar_test1",
            points=100
            )

        test_user2 = User.register(
            username="test2",
            email="test2@gmail.com",
            password="test2",
            first="test2",
            last="test2",
            quote="test2",
            sex="F",
            avatar="avatar_test2",
            points=101
            )

        db.session.add_all([test_user1,test_user2])
        db.session.commit()

        test1ImportCategory = ImportCategory(
            category="test1CategoryImport",
            description="test1Category Description Import",
            user_id=1
        )

        test2ImportCategory = ImportCategory(
            category="test2CategoryImport",
            description="test2Category Description Import",
            user_id=1
        )

        db.session.add_all([test1ImportCategory,test2ImportCategory])
        db.session.commit()

        test1ImportArticle = ImportArticles(
            author="test1Import",
            title="test1Import",
            category=1,
            description="test1Import Description",
            cover_url="test10Import.com",
            content="test10Import Content",
            user_id=1
        )

        test2ImportArticle = ImportArticles(
            author="test2Import",
            title="test2Import",
            category=1,
            description="test2Import Description",
            cover_url="test20Import.com",
            content="test20Import Content",
            user_id=1
        )

        db.session.add_all([test1ImportArticle,test2ImportArticle])
        db.session.commit()

        test1ImportVol = VocabularyFromImportArticle(
            spell="test1ImportSpell",
            definition="test1ImportDefinition",
            part_of_speech="test1ImportPartOfSpeech",
            article_id=1,
            user_id=1
        )

        test2ImportVol = VocabularyFromImportArticle(
            spell="test2ImportSpell",
            definition="test2ImportDefinition",
            part_of_speech="test2ImportPartOfSpeech",
            article_id=1,
            user_id=1
        )

        db.session.add_all([test1ImportVol,test2ImportVol])
        db.session.commit()

        test1ImportFinish = FinishImportReading(user_id=1,import_article_id=1)
        test2ImportFinish = FinishImportReading(user_id=1,import_article_id=2)
        db.session.add_all([test1ImportFinish,test2ImportFinish])
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.drop_all()

    def test_display_import_article(self):
        """Test Case of display import article"""

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.get("/vocabulary/article/list/imports")
        html = resp.get_data(as_text=True)
        
        self.assertEqual(resp.status_code,200)
        self.assertIn('test2Import',html)
        self.assertIn('test1Import',html)

    def test_display_import_articles_vocabulary(self):
        """Test case of display import articles vocabulary"""

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"
            
        resp = client.get("/vocabulary/article/list/imports/1")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn('test1ImportSpell',html)
        self.assertIn('test2ImportSpell',html)

    
    def test_edit_import_article_vocabulary_get(self):
        """Test Case of Edit import articles vocabulary"""

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.get("/vocabulary/article/list/imports/1/test1ImportSpell")
        html = resp.get_data(as_text=True)
        
        self.assertEqual(resp.status_code,200)
        self.assertIn("test1ImportSpell",html)
        self.assertIn("test1ImportDefinition",html)

    def test_edit_import_article_vocabulary_post(self):
        """Test Case of Edit import Articles Vocabulary Post"""

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.post("/vocabulary/article/list/imports/1/test1ImportSpell",data={
            "vocabulary":"test1ImportSpellEdit",
            "partOfSpeech":"test1ImportPortOfSpeechEdit",
            "definition":"test1ImportDefinitionEdit",
            "image_url":"test1Import.com"
            },follow_redirects=True)

        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn("test1ImportSpellEdit",html)
        self.assertIn("test1ImportPortOfSpeechEdit",html)
