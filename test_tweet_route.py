from unittest import TestCase

from models import db,User,Message,Likes

from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///leetenglish-test"

app.config['TESTING'] = True

app.config['DEBUT_TB_HOSTS'] = ['dont-show-debug-toolbar']

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['WTF_CSRF_ENABLED'] = False

class TestCaseForOwnVocabulary(TestCase):
    """TestCase On Tweet Section"""

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
            points=100
            )

        db.session.add_all([test_user1,test_user2])
        db.session.commit()

        test1Message = Message(
            text="test1Message",
            user_id=1
        )

        test2Message = Message(
            text="test2Message",
            user_id=1
        )

        test3Message = Message(
            text="test3Message",
            user_id=2
        )

        test4Message = Message(
            text="test4Message",
            user_id=2
        )

        db.session.add_all([test1Message,test2Message,test3Message,test4Message])
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.drop_all()

    def test_tweet_section_home_page(self):
        """TestCase Tweet section home page"""
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.get("/tweets")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn("test1Message",html)

    def test_post_comment_home_page(self):
        """TestCase Tweet Section Home Page"""
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "test1"

        resp = client.post("/tweets/test1/1/comment",data={"comment":"test1Good"},follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn("test1Good",html)

    def test_delete_comment_home_page(self): 
        """TestCase tweet section on delete comment""" 

        with app.test_client() as client: 
            with client.session_transaction() as change_session: 
                change_session["username"] = "test1" 

        resp = client.post("/tweet/delete/2",follow_redirects=True) 
        html = resp.get_data(as_text=True) 

        self.assertEqual(resp.status_code,200) 
        self.assertNotIn("test2Message",html) 

    
    def test_add_likes_on_home_page(self): 
        """TestCase Tweet section on Like comment message""" 

        with app.test_client() as client: 
            with client.session_transaction() as change_session: 
                change_session["username"] = "test1" 

        resp = client.post("/tweet/like/1",follow_redirects=True) 

        self.assertEqual(resp.status_code,200) 
        self.assertIsNotNone(Likes.query.filter(Likes.user_id==1)) 

    def test_add_tweet_message(self): 
        """TestCase about adding new tweet message""" 

        with app.test_client() as client: 
            with client.session_transaction() as change_session: 
                change_session["username"] = "test1" 
        
        resp = client.post("/tweets/test1/add",data={"text":"test1 Hello,World"},follow_redirects=True) 
        html = resp.get_data(as_text=True) 

        self.assertEqual(resp.status_code,200) 
        self.assertIn("test1 Hello,World",html) 

    def test_following_user(self): 
        """TestCase Following User""" 

        with app.test_client() as client: 
            with client.session_transaction() as change_session: 
                change_session["username"] = "test1" 
        
        resp = client.post("/tweets/user/follow/2") 

        resp1 = client.get("/tweets") 
        html = resp1.get_data(as_text=True) 

        self.assertIn("test3Message",html) 
        self.assertIn("test4Message",html) 

    def test_reading_other_user_message(self): 

        """Test Read Other User Information""" 

        with app.test_client() as client: 
            with client.session_transaction() as change_session: 
                change_session["username"] = "test1" 
            
        resp = client.get("/tweets/users/2") 
        html = resp.get_data(as_text=True) 

        self.assertEqual(resp.status_code,200) 
        self.assertIn("test3Message",html) 

    def test_comment_other_user_message(self): 
        with app.test_client() as client: 
            with client.session_transaction() as change_session: 
                change_session["username"] = "test1" 
        
        resp = client.post("/tweets/test1/2/comment/1",data={"comment":"test1,hello world"},follow_redirects=True) 
        html = resp.get_data(as_text=True) 

        self.assertEqual(resp.status_code,200) 
        self.assertIn("test1,hello world",html) 






