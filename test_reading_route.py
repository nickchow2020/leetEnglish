from unittest import TestCase
from models import Categories,Articles,db,User,UserFinishReading,VocabularyFromArticle
from models import ImportCategory,ImportArticles,ImportCategoryArticles
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///leetenglish-test"

app.config['TESTING'] = True

app.config['DEBUT_TB_HOSTS'] = ['dont-show-debug-toolbar']

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['WTF_CSRF_ENABLED'] = False

class ReadingHomePublic(TestCase):
    """Testing Home Page of reading public articles"""
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

        category_1 = Categories(
            category = "test1",
            description = "category about test1"
        )

        category_2 = Categories(
            category = "test2",
            description = "category about test2"
        )

        db.session.add_all([category_1,category_2])
        db.session.commit()

        article_test1 = Articles(
            author="test1",
            title="test1",
            category=1,
            description="test1 article",
            cover_url="test1_cover.com",
            content="test1 content",
            user_id=1
        )

        article_test2 = Articles(
            author="test2",
            title="test2",
            category=1,
            description="test2 article",
            cover_url="test2_cover.com",
            content="test2 content",
            user_id=2
        )

        article_test3 = Articles(
            author="test3",
            title="test3",
            category=2,
            description="test3 article",
            cover_url="test3_cover.com",
            content="test3 content",
            user_id=2
        )

        article_test4 = Articles(
            author="test4",
            title="test4",
            category=2,
            description="test4 article",
            cover_url="test4_cover.com",
            content="test4 content",
            user_id=2
        )

        db.session.add_all([article_test1,article_test2,article_test3,article_test4])
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.drop_all()

    def test_without_login(self):
        with app.test_client() as client:
            resp = client.get("/articles",follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code,200)
            self.assertIn("Please login first",html)

    def test_with_login(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

            resp = client.get('/articles')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code,200)
            self.assertIn("Read Public Articles",html)
            self.assertIn("about me, test1",html)
            self.assertIn("Import Your Own Articles",html)

    
    def test_display_public_category_list(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test2"

            resp = client.get("/articles/preload")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code,200)
            self.assertIn("test1",html)
            self.assertIn("test2",html)

    def test_public_category_display(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test2"

            resp = client.get('/articles/preload/test1')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code,200)
            self.assertIn('<h5 class="card-title">test1</h5>',html)
            self.assertIn('<h5 class="card-title">test2</h5>',html)

    def test_reading_article_display(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test2"

            resp = client.get('/articles/1')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code,200)
            self.assertIn("test1",html)

    def test_for_finish_reading(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

            resp = client.post('/articles/1')
            resp1 = client.post('/articles/1',follow_redirects=True)
            html = resp1.get_data(as_text=True)

            self.assertEqual(resp.status_code,302)
            self.assertEqual(resp1.status_code,200)
            self.assertIn("test1",html)
            self.assertIn("You already Finish Reading this article",html)

    def test_getting_definition(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

            resp = client.post("/article/get_definition/1",data={"new_word":"hello"})
            resp1 = client.post("/article/get_definition/1",data={"new_word":"hello"},follow_redirects=True)
            html = resp1.get_data(as_text=True)

            definition = VocabularyFromArticle.query.all()

            self.assertEqual(len(definition),1)
            self.assertEqual(definition[0].definition,"an expression of greeting")
            self.assertEqual(resp.status_code,302)
            self.assertIn("hello",html)
            self.assertIn("an expression of greeting",html)

    def test_adding_image(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

            test_vocal_1=VocabularyFromArticle(
                spell='hello',
                definition="an expression of greeting",
                part_of_speech="advert",
                article_id=1,
                user_id=1,
                )

            db.session.add(test_vocal_1)
            db.session.commit()

            resp = client.post("/articles/1/1/hello",data={"select_vocabulary":"test1.image.com"})
            resp1 = client.post("/articles/1/1/hello",data={"select_vocabulary":"test1.image.com"},follow_redirects=True)
            html = resp1.get_data(as_text=True)

            definition = VocabularyFromArticle.query.all()

            self.assertEqual(definition[0].definition,"an expression of greeting")
            self.assertEqual(definition[0].image_url,"test1.image.com")
            self.assertEqual(resp1.status_code,200)
            self.assertIn("image added successful",html)
            self.assertEqual(resp.status_code,302)


class ReadingHomeOwn(TestCase):
    """Testing for import Articles"""
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

        category_test1 = ImportCategory(
            category="test1",
            description="description of test1",
            user_id=1
        )

        category_test2 = ImportCategory(
            category="test2",
            description="description of test2",
            user_id=1
        )

        db.session.add(category_test1)
        db.session.commit()

        db.session.add(category_test2)
        db.session.commit()

        testArticle = ImportArticles(
            author="test1",
            title="test1Title",
            category=1,
            description="good test1",
            cover_url="test1.com",
            content='test1 content',
            user_id=1
        )

        db.session.add(testArticle)
        db.session.commit()

        category_article = ImportCategoryArticles(
            category_id=1,
            article_id=1
        )

        db.session.add(category_article)
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.drop_all()

        
    def test_articles_import_display(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.get('/articles/import')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn("Create a category of you own articles",html)

    def test_create_article_category(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.post('/articles/import',data={'category':'test3','description':'test3 description'})
        resp1 = client.post('/articles/import',data={'category':'test4','description':'test4 description'},follow_redirects=True)
        html = resp1.get_data(as_text=True)

        self.assertEqual(resp.status_code,302)
        self.assertEqual(resp1.status_code,200)
        self.assertIn('Category Create Successful',html)
        self.assertIn('test4',html)

    def test_when_category_articles_empty(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = 'test1'

        resp = client.get('/articles/import/test2',follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn("Create a category of you own articles",html)

    
    def test_when_category_articles_exist(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = 'test1'

        resp = client.get('/articles/import/test1')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn('test1Title',html)
        

    def test_reading_article(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"
        
        resp = client.get('/articles/import/test1/1')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn('test1Title',html)

    def test_delete_category(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp =  client.post('/articles/import/delete/category/2')

        categories = ImportCategory.query.all()
        self.assertEqual(len(categories),3)
        self.assertEqual(resp.status_code,302)

    def test_edit_category_display(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.get("/articles/import/edit/category/1")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn('description of test1',html)

    def test_edit_category_post(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.post("/articles/import/edit/category/1",data={"category":"test1","description":"description about test1 category"},follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn("description about test1 category",html)
