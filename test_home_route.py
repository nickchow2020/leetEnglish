from unittest import TestCase
from models import Follows, db,User,Quotes
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///leetenglish-test"

app.config['TESTING'] = True

app.config['DEBUT_TB_HOSTS'] = ['dont-show-debug-toolbar']

app.config['WTF_CSRF_ENABLED'] = False

class HomeRouteTesting(TestCase):

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

    test_user3 = User.register(
        username="test3",
        email="test3@gmail.com",
        password="test3",
        first="test3",
        last="test3",
        quote="test3",
        sex="F",
        avatar="avatar_test3",
        points=102
        )
    
    test_user4 = User.register(
        username="test4",
        email="test4@gmail.com",
        password="test4",
        first="test4",
        last="test4",
        quote="test4",
        sex="F",
        avatar="avatar_test4",
        points=104
        )

    db.session.add_all([test_user1,test_user2,test_user3,test_user4])
    db.session.commit()


    test_quote1 = Quotes(quote="test1")
    test_quote2 = Quotes(quote="test2")
    test_quote3 = Quotes(quote="test3")
    test_quote4 = Quotes(quote="test4")
    db.session.add_all([test_quote1,test_quote2,test_quote3,test_quote4])
    db.session.commit()

  @classmethod
  def tearDownClass(cls):
    db.drop_all()


  """Testing Home Route Page"""

  def test_without_login(self):
    with app.test_client() as client:
      resp = client.get("/")
      html = resp.get_data(as_text=True)

      self.assertEqual(resp.status_code,200)
      self.assertIn('<h1 class="display-4 text-center">LeetEnglish</h1>',html)


  def test_with_login(self):
    with app.test_client() as client:
      with client.session_transaction() as change_session:
        change_session["username"] = "test3"
      
      resp = client.get('/')  
      html = resp.get_data(as_text=True)

      self.assertEqual(resp.status_code,200)
      self.assertIn('<h2 class="text-success" id="title_top_three">Keep Up the Motivation</h2>',html)
      self.assertIn('<title>LeetEnglish</title>',html)

  def test_login_get_form(self):
    with app.test_client() as client:
      resp = client.get("/login")
      html = resp.get_data(as_text=True)

      self.assertEqual(resp.status_code,200)
      self.assertIn('<h1 class="title-login">USER LOGIN</h1>',html)

  def test_login_post_form(self):
    with app.test_client() as client:
      resp = client.post("/login",data={'username':'test1','password':'test1'},follow_redirects=True)
      html = resp.get_data(as_text=True)

      self.assertEqual(resp.status_code,200)
      self.assertIn('Login successful, Welcome back test1 !!!',html)

  
  def test_login_user_not_exist(self):
    with app.test_client() as client:
      resp = client.post("/login",data={'username':'test10','password':'test10'},follow_redirects=True)
      html = resp.get_data(as_text=True)

      self.assertEqual(resp.status_code,200)
      self.assertIn('Username or Password is not correct, please try another one!!!',html)

  def test_register_duplicate_user(self):
    with app.test_client() as client:
      resp = client.post("/register",follow_redirects=True,
          data={
            'username':'test4',
            'email':'test4@gmail.com',
            'password':'test4',
            'first_name':'test4',
            'last_name':"test4",
            'quote':'4',
            'gender':'F',
            'avatar':'avatar.com',
            'points':105})

      html = resp.get_data(as_text=True)

      self.assertEqual(resp.status_code,200)
      self.assertIn('username or email are already been use, try other one please',html)

  def test_register_new_user(self):
    with app.test_client() as client:
      resp = client.post("/register",follow_redirects=True,
          data={
            'username':'test5',
            'email':'test5@gmail.com',
            'password':'test5',
            'first_name':'test5',
            'last_name':"test5",
            'quote':'3',
            'gender':'F',
            'avatar':'avatar.com',
            'points':105})

      html = resp.get_data(as_text=True)

      total_user = db.session.query(User).count()


      self.assertEqual(resp.status_code,200)
      self.assertEqual(total_user,5)
      self.assertIn('Hi, thank you for join our leanring community, test5',html)

  def test_logout(self):
    with app.test_client() as client:
      with client.session_transaction() as change_session:
        change_session["username"] = "test3"

      resp = client.get("/signout",follow_redirects=True)
      html = resp.get_data(as_text=True)

      self.assertEqual(resp.status_code,200)
      self.assertIn('Successful sign out see you next time!',html)