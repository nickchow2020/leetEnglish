from unittest import TestCase
from flask import request
from requests.api import get
from werkzeug.utils import send_file
from models import Categories,Articles,db,User,UserFinishReading,VocabularyFromArticle
from models import VocabularyListName,VocabularyList,ImportArticles,ImportCategory,FinishImportReading,VocabularyFromImportArticle
from app import app, vocabulary

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///leetenglish-test"

app.config['TESTING'] = True

app.config['DEBUT_TB_HOSTS'] = ['dont-show-debug-toolbar']

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['WTF_CSRF_ENABLED'] = False

class TestCaseOfPracticeYourOwnVocabularyList(TestCase):
    """Practice Your Own Vocabulary List"""

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

        vocalList1 = VocabularyListName(
            list_name="test1List",
            description="test1 List Description",
            user_id=1
        )

        db.session.add(vocalList1)
        db.session.commit()

        vocalUnderList1 = VocabularyList(
            spell="test1Spell",
            definition="test1SpellDefinition",
            part_of_speech="test1SpellPartOfSpeech",
            list_id=1,
        )

        vocalUnderList2 = VocabularyList(
            spell="test2Spell",
            definition="test2SpellDefinition",
            part_of_speech="test2SpellPartOfSpeech",
            list_id=1,
        )

        vocalUnderList3 = VocabularyList(
            spell="test3Spell",
            definition="test3SpellDefinition",
            part_of_speech="test3SpellPartOfSpeech",
            list_id=1,
        )

        db.session.add_all([vocalUnderList1,vocalUnderList2,vocalUnderList3])
        db.session.commit()

    
    @classmethod
    def tearDownClass(cls):
        db.drop_all()

    def test_show_practice_vocabulary_list(self):

        """Test Show Practice Vocabulary List"""
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.get("/practice/own/vocabulary/list")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn("test1List",html)
        self.assertIn("test1 List Description",html)

    def test_show_practice_vocabulary_list_vocabulary(self):

        """Test Show Practice Vocabulary List"""

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.get("/practice/own/vocabulary/list/1")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn('test1SpellDefinition',html)
        self.assertIn('test2SpellDefinition',html)
        self.assertIn('test3SpellDefinition',html)


    def test_practice_vocabulary_list(self):
        """Test Show Practice Vocabulary List"""

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.get("/practice/own/vocabulary/list/1/page/0?practice=1,2")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)

    def test_practice_answer_question(self):
        """Test Answer Question"""

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.post("/practice/own/vocabulary/list/1/page/0?practice=1",data={"answer":"test1Spell"},follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn("Congrats, you just make another milestones",html)

    def test_practice_answer_question1(self):
        """Test Practice Answer question"""

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.post("/practice/own/vocabulary/list/1/page/0?practice=1,2",data={"answer":"test1Spell"},follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn("test2Spell",html)




class TestCaseOfPracticeYourPreloadVocabularyList(TestCase):

    """Practice Your Preload Vocabulary List"""

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

        db.session.add(test_user1)
        db.session.commit()

        category1 = Categories(
            category="test1",
            description="test1 descrition"
        )

        category2 = Categories(
            category="test2",
            description="test2 descrition"
        )

        db.session.add_all([category1,category2])
        db.session.commit()

        test1_Article=Articles(
            author="test1Article",
            title="test1Article",
            category=1,
            description="test1Article Description",
            cover_url="test1Article.com",
            content="test1ArticleContent",
            user_id=1
        )

        test2_Article=Articles(
            author="test2Article",
            title="test2Article",
            category=1,
            description="test2Article Description",
            cover_url="test2Article.com",
            content="test2ArticleContent",
            user_id=1
        )

        db.session.add_all([test1_Article,test2_Article])
        db.session.commit()

        test1Volcal = VocabularyFromArticle(
            spell="test1SpellProload",
            definition="test1SpellDefinition Proload",
            part_of_speech="test1PartOfSpeech",
            article_id=1,
            user_id=1
        )

        test2Volcal = VocabularyFromArticle(
            spell="test2SpellProload",
            definition="test2SpellDefinition Proload",
            part_of_speech="test2PartOfSpeech",
            article_id=1,
            user_id=1
        )

        db.session.add_all([test1Volcal,test2Volcal])
        db.session.commit()

        read1Article = UserFinishReading(
            user_id=1,
            article_id=1
        )

        read2Article = UserFinishReading(
            user_id=1,
            article_id=2
        )

        db.session.add_all([read1Article,read2Article])
        db.session.commit()
        
    @classmethod
    def tearDownClass(cls):
        db.drop_all()

    
    def test_show_preload_vocabulary_list(self):
        """TestCase Show Preload Vocabulary List"""

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.get("/practice/public/vocabulary/list")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn("test1Article",html)
        self.assertIn("test2Article",html)

    def test_show_preload_vocabulary_list_under_article(self):
        """TestCase how preload vocabulary List"""

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.get('/practice/public/vocabulary/list/1')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn("test1SpellProload",html)
        self.assertIn("test2SpellProload",html)

    def test_practice_vocabulary_list_preload_article(self):
        """TestCase with practice vocabulary list preload"""

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.get('/practice/public/vocabulary/list/1/page/0?practice=1,2')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)

    def test_practice_vocabulary_list_preload_article_post(self):
        """TestCase with practice vocabulary list preload on post"""

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.post('/practice/public/vocabulary/list/1/page/0?practice=1,2',data={"answer":"test1SpellProload"},follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn("test2SpellProload",html)


    def test_practice_vocabulary_with_wrong_anwser(self):
        """TestCase with practice vocabulary list preload on wrong answer"""

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.post('/practice/public/vocabulary/list/1/page/0?practice=1,2',data={"answer":"test1SpellProload11"},follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn("That is wrong answer, please try again",html)


class TestCaseOnImportArticleVocabulary(TestCase):
    """TestCaseOnImportArticleVocabulary List"""

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

        db.session.add(test_user1)
        db.session.commit()

        test1Category = ImportCategory(
                category="test1ImportCategory",
                description="test1ImportCategory Description",
                user_id=1
        )

        test2Category = ImportCategory(
                category="test2ImportCategory",
                description="test2ImportCategory Description",
                user_id=1
        )

        db.session.add_all([test1Category,test2Category])
        db.session.commit()
    
        test1ImportArticle = ImportArticles(
            author="test1ImportArticle",
            title="test1ImportArticleTitle",
            category=1,
            description="test1ImportArticleTitle Description",
            cover_url="test1ImportArticleUrl.com",
            content="test1ImportArticleContent",
            user_id=1
        )

        test2ImportArticle = ImportArticles(
            author="test2ImportArticle",
            title="test2ImportArticleTitle",
            category=1,
            description="test2ImportArticleTitle Description",
            cover_url="test2ImportArticleUrl.com",
            content="test2ImportArticleContent",
            user_id=1
        )

        test3ImportArticle = ImportArticles(
            author="test3ImportArticle",
            title="test3ImportArticleTitle",
            category=1,
            description="test3ImportArticleTitle Description",
            cover_url="test3ImportArticleUrl.com",
            content="test3ImportArticleContent",
            user_id=1
        )

        db.session.add_all([test1ImportArticle,test2ImportArticle,test3ImportArticle])
        db.session.commit()

        test1Vocalbulary = VocabularyFromImportArticle(
            spell="test1Vocabulary",
            definition="test1Vocabulary Definition",
            part_of_speech="test1Vocabulary PartOfSpeech",
            article_id=1,
            user_id=1
        )

        test2Vocalbulary = VocabularyFromImportArticle(
            spell="test2Vocabulary",
            definition="test2Vocabulary Definition",
            part_of_speech="test2Vocabulary PartOfSpeech",
            article_id=1,
            user_id=1
        )

        test3Vocalbulary = VocabularyFromImportArticle(
            spell="test3Vocabulary",
            definition="test3Vocabulary Definition",
            part_of_speech="test3Vocabulary PartOfSpeech",
            article_id=1,
            user_id=1
        )

        db.session.add_all([test1Vocalbulary,test2Vocalbulary,test3Vocalbulary])
        db.session.commit()

        test1ImportFinish = FinishImportReading(
            user_id=1,
            import_article_id=1
        )

        test2ImportFinish = FinishImportReading(
            user_id=1,
            import_article_id=2
        )

        db.session.add_all([test1ImportFinish,test2ImportFinish])
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.drop_all()

    def test_show_vocabulary_list(self):
        """TestCase about show all the vocabulary list"""

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.get("/practice/imports/vocabulary/list")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn("test1ImportArticleTitle",html)
        self.assertIn("test2ImportArticleTitle",html)

    def test_show_vocabulary_list_import(self):
        """TestCase about show all the vocabulary list with a article id"""

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"
            
        resp = client.get("/practice/imports/vocabulary/list/1")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn("test1Vocabulary",html)
        self.assertIn("test2Vocabulary",html)
        self.assertIn("test3Vocabulary",html)

    def test_practice_vocabulary_import(self):
        """TestCase about practice vocabulary with a import articles"""

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.get("/practice/imports/vocabulary/list/1/page/0?practice=1,2")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)

    def test_practice_vocabulary_import_post(self):
        """TestCase about practice vocabulary with a import post articles"""

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.post("/practice/imports/vocabulary/list/1/page/0?practice=1,2",data={"answer":"test1Vocabulary"},follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn("test2Vocabulary",html)


    def test_practice_vocabulary_import_vocabulary_post_wrong_answer(self):
        """TestCase about preactice answer an wrong answer"""

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.post("/practice/imports/vocabulary/list/1/page/0?practice=1,2",data={"answer":"test1Vocabulary11"},follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn("That is wrong answer, please try again",html)
