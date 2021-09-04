from logging import debug
from operator import methodcaller
import os
from sys import exec_prefix
from flask import Flask,render_template,redirect,session,flash,request
from datetime import datetime
from sqlalchemy import exc
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db,User,Quotes,Articles,VocabularyFromArticle,UserFinishReading,VocabularyFromImportArticle
from models import VocabularyListName,VocabularyList,ImportCategory,ImportArticles,ImportCategoryArticles,Categories,FinishImportReading
from models import Message,CommentMessage,Follows,Likes,CommentLikes
from sqlalchemy.exc import IntegrityError
from api_request import get_english_def,get_definition_image
from forms import Login_form,MessageForm
app = Flask(__name__)
app.debug = True

# define database url
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL','postgresql:///leetenglish')

# allow intercept redirects
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

# disable FLASK-SQLALCHEMY event system warning message
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# echo every SQL implementation
app.config["SQLALCHEMY_ECHO"] = True

# define secret key for secret purpose
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY","MY_SECRET_KEY_10_20")

# connect to database leetenglish
connect_db(app)
toolbar = DebugToolbarExtension(app)

# home page route
@app.route("/")
def rootPage():
  if "username" in session:
    username = session["username"]
    # get current user data
    user = User.query.filter_by(username=username).first()

    # get top three users data
    # with filter(),order_by(),limit() and desc() order
    top_three_user = User.query.filter(User.points >= 1).order_by(User.points.desc()).limit(3).all()
    top_nine_article = Articles.query.order_by(Articles.number_of_readings.desc()).limit(9).all()

    # top_three represent top three user
    # top_nine represent top nine articles
    return render_template("home.html",user=user,top_three=top_three_user,top_nine=top_nine_article,formHome=True)
  else:
    return render_template("home.html")

# register user 
# using request.form to retrieve data
@app.route("/register",methods=["GET","POST"])
def register():
  if request.method == "POST":
    try:
      username = request.form.get("username")
      email = request.form.get("email")
      password = request.form.get("password")
      first_name = request.form.get("first_name")
      last_name = request.form.get("last_name")
      quote = request.form.get("quote")
      sex = request.form.get("gender")
      avatar = request.form.get("avatar")
      points= request.form.get("points")

      # convert quote id to words
      _quote = Quotes.query.get(quote).quote
      register_user = User.register(
        username=username,
        email=email,
        password=password,
        first=first_name,
        last=last_name,
        quote=_quote,
        sex=sex,
        avatar=avatar,
        points=points
        )

      db.session.add(register_user)
      db.session.commit()
      session["username"] = username
      flash(f"Hi, thank you for join our leanring community, {first_name}","success")
      return redirect("/")
      # handle error when User is already token
    except IntegrityError:
      flash("username or email are already been use, try other one please","danger")
      return redirect("/register")
  else:
    return render_template("register.html")


# login user with username and password
# use WTForm
@app.route("/login",methods=["GET","POST"])
def login():
  form = Login_form()
  if form.validate_on_submit():
    username = form.username.data
    password = form.password.data
    current_user = User.authenticate(username,password)
    if(current_user):
      session["username"] = username
      flash(f"Login successful, Welcome back {current_user.first_name} !!!","success")
      return redirect("/")
    else:
      flash("Username or Password is not correct, please try another one!!!","danger")
      return redirect("/login")
  return render_template("login.html",form=form)

# logout route
# to logout user
@app.route("/signout")
def signout():
    session.pop("username")
    flash("Successful sign out see you next time!","success")
    return redirect("/")


# view user portfile and update user portfile
# <username>: accept one username parameter
# <username>: to target on current_user
@app.route("/user/info/<username>",methods=["POST","GET"])
def portfile(username):
  if "username" in session:
    _username = session["username"]
    current_user = User.query.filter_by(username=_username).first()
    if request.method == "POST":
        # get user and update user info with dot notation
        current_user.email = request.form.get("email")
        current_user.first_name = request.form.get("first_name")
        current_user.last_name = request.form.get("last_name")
        current_user.quote = request.form.get("quote")
        current_user.avatar = request.form.get("avatar")
        db.session.commit()
        flash("User portfile update successful","success")
        return redirect(f"/user/info/{username}")
    else:
      user = User.query.filter_by(username=username).first()
      return render_template("user_info.html",user=user,current_user=current_user)
  else:
    flash("Please login first","warning")
    return redirect("/login")

# handle reading article with search term 
# it's accept two argument first a id of the book
# second is the option one with a search term
@app.route("/articles/<int:id>",methods=["POST","GET"],defaults={'search': None})
@app.route("/articles/<int:id>/<search>",methods=["POST","GET"])
def read_article(id,search):
  # get current article data
  current_article = Articles.query.get_or_404(id)

  # convert current article data to actual paragraph with "/n"
  paragraph = current_article.content

  # get category 
  category = current_article.theCategory

  # check if username is exist
  if "username" in session:
    # get user data
    username = session["username"]
    user = User.query.filter_by(username=username).first()
    # if has search term
    if search != None :
      # with "POST" method
      if request.method == "POST":
        # add number of reading plus one
        current_article.number_of_readings = current_article.number_of_readings + 1
        db.session.commit()

        # handle duplicate reading
        try:
          has_read = UserFinishReading(user_id=user.id,article_id=current_article.id)
          db.session.add(has_read)
          db.session.commit()
          return redirect(f"/articles/preload/{category.category}")
        except IntegrityError:
          flash("You already Finish Reading this article","warning")
          return redirect(f"/articles/{id}/{search}")
      else:
        # handle get method
        all_definition = VocabularyFromArticle.query.filter_by(spell=search).all()

        # retrieve definition image from API 
        definition_images = get_definition_image(search)
        return render_template("article.html",
              user=user,
              article=current_article,
              paragraph=paragraph,
              definitions=all_definition,
              search_key=search,
              category=category,
              definition_images=definition_images)
    # if not search term
    else:
      if request.method == "POST":
        current_article.number_of_readings = current_article.number_of_readings + 1
        db.session.commit()
        # handle duplicate
        try:
          has_read = UserFinishReading(user_id=user.id,article_id=current_article.id)
          db.session.add(has_read)
          db.session.commit()
          return redirect(f"/articles/preload/{category.category}")
        except  IntegrityError:
          flash("You already Finish Reading this article","warning")
          return redirect(f"/articles/{id}")
      return render_template("article.html",user=user,article=current_article,paragraph=paragraph,category=category)
  else:
    # login if not sign in
    flash("Please login first","warning")
    return redirect("/login")

# display top nine articles 
@app.route("/articles/topNine/<int:id>",methods=["GET","POST"],defaults={'search': None})
@app.route("/articles/topNine/<int:id>/<search>",methods=["POST","GET"])
def display_top_nine_article(id,search):
  current_article = Articles.query.get_or_404(id)

    # convert current article data to actual paragraph with "/n"
  paragraph = current_article.content

    # get category 
  category = current_article.theCategory

    # check if username is exist
  if "username" in session:
      # get user data
      username = session["username"]
      user = User.query.filter_by(username=username).first()
      # if has search term
      if search != None :
        # with "POST" method
        if request.method == "POST":
          # add number of reading plus one
          current_article.number_of_readings = current_article.number_of_readings + 1
          db.session.commit()

          # handle duplicate reading
          try:
            has_read = UserFinishReading(user_id=user.id,article_id=current_article.id)
            db.session.add(has_read)
            db.session.commit()
            return redirect("/")
          except IntegrityError:
            flash("You already Finish Reading this article","warning")
            return redirect(f"/articles/topNine/{id}")
        else:
          # handle get method
          all_definition = VocabularyFromArticle.query.filter_by(spell=search).all()

          # retrieve definition image from API 
          definition_images = get_definition_image(search)
          return render_template("article.html",
                user=user,
                article=current_article,
                paragraph=paragraph,
                definitions=all_definition,
                search_key=search,
                category=category,
                definition_images=definition_images,
                topNine=True)
      # if not search term
      else:
        if request.method == "POST":
          current_article.number_of_readings = current_article.number_of_readings + 1
          db.session.commit()
          # handle duplicate
          try:
            has_read = UserFinishReading(user_id=user.id,article_id=current_article.id)
            db.session.add(has_read)
            db.session.commit()
            return redirect("/")
          except  IntegrityError:
            flash("You already Finish Reading this article","warning")
            return redirect(f"/articles/topNine/{id}")
        return render_template("article.html",user=user,article=current_article,paragraph=paragraph,category=category,topNine=True)
  else:
      # login if not sign in
      flash("Please login first","warning")
      return redirect("/login")


# update vocabulary from article image url
@app.route("/articles/<int:user_id>/<int:article_id>/<search_key>",methods=["POST"],defaults={'topNine': None})
@app.route("/articles/<int:user_id>/<int:article_id>/<search_key>/<topNine>",methods=["POST"])
def add_article_image(user_id,article_id,search_key,topNine):
  if "username" in session:
    # get current search key related to the article and user
    current_search_key = VocabularyFromArticle.query.filter_by(user_id=user_id,article_id=article_id,spell=search_key).first()

    # update it's vocabulary url image
    current_search_key.image_url = request.form.get("select_vocabulary")
    db.session.commit()

    flash("image added successful","success")
    if topNine != None: 
      return redirect(f"/articles/topNine/{article_id}/{search_key}")
    else:
      return redirect(f"/articles/{article_id}/{search_key}")
  else:
    # if user not login, allow them to login first
    flash("Please login first","warning")
    return redirect("/login")



# rough that is going to handle definition
# it going to accept a id parameter
@app.route("/article/get_definition/<int:id>",methods=["POST"],defaults={'topNine': None})
@app.route("/article/get_definition/<int:id>/<topNine>",methods=["POST"])
def get_definition(id,topNine):
  # if user is login
  if "username" in session:
    # get current user
    username = session["username"]
    user = User.query.filter_by(username=username).first()

    # get current search term
    new_vocabulary = request.form.get("new_word")

    if topNine != None: 
      try:
        # check duplicate on search term
        exists = db.session.query(VocabularyFromArticle.id).filter_by(spell=new_vocabulary,article_id=id,user_id=user.id).first() is not None 

        # retrieve all definition
        definition = get_english_def(new_vocabulary)

        # save all defintion into model
        _definition = VocabularyFromArticle(spell=new_vocabulary,definition=definition["definition"],part_of_speech=definition["partOfSpeech"],article_id=id,user_id=user.id)
        if exists : 
          # if duplicate exist
          flash(f"{new_vocabulary} ---- already exists in the database","warning")
          return redirect(f"/articles/topNine/{id}/{new_vocabulary}")
        else:
          # if no duplicate
          db.session.add(_definition)
          db.session.commit()
        return redirect(f"/articles/topNine/{id}/{new_vocabulary}")
      except:
        return redirect(f"/articles/topNine/{id}")
    else:
      try:
        # check duplicate on search term
        exists = db.session.query(VocabularyFromArticle.id).filter_by(spell=new_vocabulary,article_id=id,user_id=user.id).first() is not None 

        # retrieve all definition
        definition = get_english_def(new_vocabulary)

        # save all defintion into model
        _definition = VocabularyFromArticle(spell=new_vocabulary,definition=definition["definition"],part_of_speech=definition["partOfSpeech"],article_id=id,user_id=user.id)
        if exists : 
          # if duplicate exist
          flash(f"{new_vocabulary} ---- already exists in the database","warning")
          return redirect(f"/articles/{id}/{new_vocabulary}")
        else:
          # if no duplicate
          db.session.add(_definition)
          db.session.commit()
        return redirect(f"/articles/{id}/{new_vocabulary}")
      except:
        return redirect(f"/articles/{id}")
  else:
      flash("Please login first","danger")
      return redirect("/login")


# implemention with vocabulary from route
@app.route("/vocabulary")
def vocabulary():
  if "username" in session:
    username = session["username"]
    # get current user data
    user = User.query.filter_by(username=username).first()
    return render_template("vocabulary.html",user=user)
  else:
    flash("Please login first","warning")
    return redirect("/login")

# implementation with add vocabulary list route
@app.route("/vocabulary/add_list",methods=["POST","GET"])
def add_vocabulary_list():
  if "username" in session:
      username = session["username"]
      # get current user data
      user = User.query.filter_by(username=username).first()
      if request.method == "POST":
        # getting data from list
        list_name = request.form.get("newList")
        description = request.form.get("list_description")
        # add vocabulary list into database
        new_list= VocabularyListName(list_name=list_name,description=description,user_id = user.id)
        db.session.add(new_list)
        db.session.commit()
        flash(f"Vocabulary list [{list_name}] create successful","success")
        return redirect("/vocabulary/add_list")
      else:
        # disply the list back to the page
        related_list_name= VocabularyListName.query.filter_by(user_id=user.id).all()
        return render_template("add_vocabulary_list.html",user=user,related_list_name=related_list_name)
  else:
    flash("Please login first","warning")
    return redirect("/login")

# delete list name
@app.route("/vocabulary/list/delete/<int:id>")
def delete_list_name(id):
  # get target list name and delete it
  targetList = VocabularyListName.query.filter_by(id=id).first()
  db.session.delete(targetList)
  db.session.commit()
  flash(f"Vocabulary list delete successful [list_id:{id}]!","success")
  return redirect("/vocabulary/add_list")

# update or edit list vocabulary
@app.route("/vocabulary/list/edit/<int:id>",methods=["GET","POST"])
def edit_list(id):
  # get edit target list
  edit_list = VocabularyListName.query.filter_by(id=id).first()
  if "username" in session:
      username = session["username"]  
      # get current user data
      user = User.query.filter_by(username=username).first()
      if request.method == "POST":
        edit_list.list_name = request.form.get("listName")
        edit_list.description = request.form.get("listDescription")
        db.session.commit()
        flash("Update successful!","success")
        return redirect("/vocabulary/add_list")
      else:
        return render_template("edit_list.html",target=edit_list,user=user)
  else:
    flash("Please login first","warning")
    return redirect("/login")

# handle vocabulary list route
@app.route("/vocabulary/list/<int:id>",methods=["POST","GET"],defaults={'search': None})
@app.route("/vocabulary/list/<int:id>/<search>",methods=["POST","GET"])
def add_vocabulary_for_list(id,search):
  if "username" in session:
      username = session["username"]
      # get current user data
      user = User.query.filter_by(username=username).first()
      # get current listName
      list_name = VocabularyListName.query.get_or_404(id)
      previous_search = VocabularyList.query.filter_by(spell=search,list_id=id).first()
      if search != None:
        definition_images = get_definition_image(search)
        if request.method == "POST":
          previous_search.image_url = request.form.get("select_vocabulary")
          db.session.commit()
          flash(f"image for vocabulary '{previous_search.spell}' added","success")
          return redirect(f"/vocabulary/list/{id}/{previous_search.spell}")
        else:
          return render_template("add_list_vocabulary.html",user=user,list_name=list_name,previous_search=previous_search,definition_images=definition_images)
      else:
        return render_template("add_list_vocabulary.html",user=user,list_name=list_name)
  else:
    flash("Please login first","warning")
    return redirect("/login")

# edit vocabulary route 
@app.route("/vocabulary/list/edit/<int:id>/<search>", methods=["POST","GET"])
def edit_list_vocabulary(id,search):
  if "username" in session:
      username = session["username"]
      # get current user data
      user = User.query.filter_by(username=username).first()
      target_vocabulary = VocabularyList.query.filter_by(list_id=id,spell=search).first()
      if request.method == "POST":
        target_vocabulary.spell = request.form.get("vocabulary")
        target_vocabulary.part_of_speech = request.form.get("partOfSpeech")
        target_vocabulary.definition = request.form.get("definition")
        target_vocabulary.image_url = request.form.get("image_url")
        db.session.commit()
        flash(f"{search} update successfully","success")
        return redirect(f"/vocabulary/list/{id}/{search}")
      else:
        return render_template("edit_list_vocabulary.html",user=user,target_vocabulary=target_vocabulary)
  else:
    flash("Please login first","warning")
    return redirect("/login")


# get definition vocabulary route
@app.route("/vocabulary/definition/list/<int:id>",methods=["POST"])
def store_list_definition(id):
  if "username" in session:
    list_name = VocabularyListName.query.get_or_404(id)
    search_key = request.form.get("vocabulary")
    exists = db.session.query(VocabularyList.id).filter_by(spell=search_key,list_id = id).first() is not None
    if exists: 
      flash(f"'{search_key}' already exist in list {list_name.list_name}","warning")
      return redirect(f"/vocabulary/list/{id}/{search_key}")
    else:
      try:
        _definition = get_english_def(search_key)
        new_vol = VocabularyList(spell=search_key,definition=_definition["definition"],part_of_speech=_definition["partOfSpeech"],list_id=id)
        db.session.add(new_vol)
        db.session.commit()
        flash(f"'{search_key}' successful add to {list_name.list_name} list","success")
        return redirect(f"/vocabulary/list/{id}/{search_key}")
      except:
        flash(f"Please entry your vocabulary","warning")
        return redirect(f"/vocabulary/list/{id}")
  else:
    flash("Please login first","warning")
    return redirect("/login")


# handle vocabulary from articles 
@app.route("/vocabulary/article/list")
def vocabulary_article_list():
  if "username" in session:
      username = session["username"]
      # get current user data
      user = User.query.filter_by(username=username).first()
      return render_template("vocabulary_article_list.html",user=user)
  else:
    flash("Please login first","warning")
    return redirect("/login")

# handle preload vocabulary articles list
@app.route("/vocabulary/article/list/preload")
def handle_proload_list():
  if "username" in session:
      username = session["username"]
      # get current user data
      user = User.query.filter_by(username=username).first()

      return render_template("vocabulary_list_preload.html",user=user)
  else:
    flash("Please login first","warning")
    return redirect("/login")

# hello, home
@app.route("/vocabulary/article/<int:id>/list")
def show_vocabulary(id):
  if "username" in session:
      username = session["username"]
      # get current user data
      user = User.query.filter_by(username=username).first()
      article = Articles.query.get_or_404(id)
      vocabularies = VocabularyFromArticle.query.filter_by(user_id=user.id,article_id=id).all()
      return render_template("show_article_vocabulary.html",user=user,vocabularies=vocabularies,article=article)
  else:
    flash("Please login first","warning")
    return redirect("/login")

# route that is allow us to edit vocabulary from articles
@app.route("/vocabulary/article/<int:article_id>/list/<search>",methods=["POST","GET"])
def edit_article_vocabulary(article_id,search):
  if "username" in session:
      username = session["username"]
      # get current user data
      user = User.query.filter_by(username=username).first()
      target_vocabulary = VocabularyFromArticle.query.filter_by(user_id=user.id,article_id=article_id,spell=search).first()
      if request.method == "POST":
        target_vocabulary.part_of_speech = request.form.get("partOfSpeech")
        target_vocabulary.definition = request.form.get("definition")
        target_vocabulary.image_url = request.form.get("image_url")
        db.session.commit()
        flash(f"{search} update successful","success")
        return redirect(f"/vocabulary/article/{article_id}/list")
      else:
        return render_template("edit_article_vocabulary.html",user=user,target_vocabulary=target_vocabulary,article_id=article_id)
  else:
    flash("Please login first","warning")
    return redirect("/login")

# route that is going to handle articles
@app.route("/articles")
def articles():
  if "username" in session:
    username = session["username"]
    # get current user data
    user = User.query.filter_by(username=username).first()
    return render_template("articles.html",user=user)
  else:
    flash("Please login first","warning")
    return redirect("/login")

# route that is going to display the default preload articles
@app.route("/articles/preload",defaults={'category': None})
@app.route("/articles/preload/<category>")
def preload_article(category):
  if "username" in session:
    username = session["username"]
    # get current user data
    user = User.query.filter_by(username=username).first()
    if category != None:
      category = Categories.query.filter_by(category=category).first()
      return render_template("show_preload_article.html",user=user,category=category)
    else:
      all_category = Categories.query.all()
      return render_template("article_preload.html",user=user,categories=all_category)
  else:
    flash("Please login first")
    return redirect("/login")


@app.route("/delete/articles/preload/<category>/<int:id>",methods=["POST"])
def delete_own_article(category,id):
  if "username" in session:
    username = session["username"]
    # get current user data
    user = User.query.filter_by(username=username).first()
    target_article = Articles.query.filter_by(user_id=user.id,id=id).first()
    db.session.delete(target_article)
    db.session.commit()

    # check if category is empty 
    category = Categories.query.filter_by(category=category).first()
    if category.articles:
      flash(f"article '{target_article.title}' delete successful","success")
      return redirect(f"/articles/preload/{category.category}")
    else:
      db.session.delete(category)
      db.session.commit()
      return redirect(f"/articles/preload")
  else:
    flash("Please login first","warning")
    return redirect("/login")

# route that is handle display import articles
@app.route("/articles/import",methods=["GET","POST"])
def article_import():
  if "username" in session:
    username = session["username"]
    # get current user data
    user = User.query.filter_by(username=username).first()
    if request.method == "POST":
      importCategory = ImportCategory(
        category=request.form.get("category"),
        description=request.form.get("description"),
        user_id=user.id)
      db.session.add(importCategory)
      db.session.commit()
      flash("Category Create Successful","success")
      return redirect("/articles/import")
    else:
      return render_template("import_article.html",user=user)
  else:
    flash("Please login first")
    return redirect("/login")


# edit category
@app.route("/articles/import/edit/category/<int:id>",methods=["POST","GET"])
def edit_import_category(id):
  if "username" in session:
    username = session["username"]
    # get current user data
    user = User.query.filter_by(username=username).first()
    target_category = ImportCategory.query.get_or_404(id)

    if request.method == "POST":
      target_category.category = request.form.get("category")
      target_category.description = request.form.get("description")
      db.session.commit()
      flash(f"Category {target_category.category} update successful!", "success")
      return redirect("/articles/import")
    else:
      return render_template("edit_category.html",user=user,target=target_category)
  else:
    flash("Please Login First")
    return redirect("/login")

# delete category
@app.route("/articles/import/delete/category/<int:id>",methods=["POST"])
def delete_import_category(id):
  if "username" in session:
    username = session["username"]
    # get current user data
    user = User.query.filter_by(username=username).first()
    targetCategory = ImportCategory.query.get_or_404(id)
    db.session.delete(targetCategory)
    db.session.commit()
    flash(f"Category {targetCategory.category} delete successful!","success")
    return redirect("/articles/import")
  else:
    flash("Please login first","warning")
    return redirect("/login")

# show import articles 
@app.route("/articles/import/<category>", methods=["POST","GET"])
def show_import_article(category):
  if "username" in session:
      username = session["username"]
      # get current user data
      user = User.query.filter_by(username=username).first()
      category = ImportCategory.query.filter_by(category=category).first()
      if category != None:
        return render_template("show_import_articles.html",user=user,category=category)
      else:
        return redirect("/articles/import")
  else:
    flash("Please login first","warning")
    return redirect("/login")

# add new articles form
@app.route("/articles/import/<category>/add", methods=["POST","GET"])
def article_import_add(category):
  if "username" in session:
      username = session["username"]
      # get current user data
      user = User.query.filter_by(username=username).first()

      # get category
      category = ImportCategory.query.filter_by(category=category).first()
      if request.method == "POST":
        if request.form.get("cover_url") == "": 
          import_article = ImportArticles(
            author=request.form.get("author"),
            title=request.form.get("title"),
            category=request.form.get("category"),
            description=request.form.get("description"),
            content=request.form.get("article_context"),
            number_of_readings = request.form.get("numberRead"),
            user_id = user.id)
          db.session.add(import_article)
          db.session.commit()
        else:
          import_article = ImportArticles(
            author=request.form.get("author"),
            title=request.form.get("title"),
            category=request.form.get("category"),
            description=request.form.get("description"),
            cover_url=request.form.get("cover_url"),
            content=request.form.get("article_context"),
            number_of_readings = request.form.get("numberRead"),
            user_id = user.id)
          db.session.add(import_article)
          db.session.commit()


        category_article = ImportCategoryArticles(category_id=category.id,article_id=import_article.id)
        db.session.add(category_article)
        db.session.commit()
        flash("article import successful","success")
        return redirect(f"/articles/import/{category.category}")
      else:
        return render_template("add_import_article.html",user=user,category=category)
  else:
    flash("Please login first","warning")
    return redirect("/login")
@app.route("/articles/import/<category>/<int:id>",methods=["POST","GET"],defaults={"search":None})
@app.route("/articles/import/<category>/<int:id>/<search>",methods=["POST","GET"])
def show_article_import(category,id,search):
  if "username" in session:
      username = session["username"]
      # get current user data
      user = User.query.filter_by(username=username).first()
      article = ImportArticles.query.get_or_404(id)
      # separeate into paragraph
      paragraph =article.content

      if request.method == "POST": 
        try:
          finish_article = FinishImportReading(user_id=user.id,import_article_id=article.id)
          db.session.add(finish_article)
          db.session.commit()
          flash("Great Job, Just finish reading one article!","success")
          return redirect(f"/articles/import/{category}")
        except exc.IntegrityError:
          flash("you already finish reading this article!","warning")
          return redirect(f"/articles/import/{category}/{id}")
      else:
        if search != None:
          definition = VocabularyFromImportArticle.query.filter_by(spell=search,article_id=id,user_id=user.id).all()
          definition_images = get_definition_image(search)
          return render_template("show_article_import.html",
                user=user,
                article=article,
                paragraph=paragraph,
                category=category,
                definitions=definition,
                search_key=search,
                definition_images=definition_images)
        else:
          return render_template("show_article_import.html",user=user,article=article,paragraph=paragraph,category=category)
  else:
    flash("Please login first","warning")
    return redirect("/login")

# route that add import article vocabulary definition
@app.route('/article/get_definition/<category>/<int:id>',methods=["POST"])
def get_import_definition(category,id):
  if "username" in session:
    user = User.query.filter_by(username=session["username"]).first()
    search = request.form.get("new_search")
    try:
      definition = get_english_def(search)
      vocabulary = VocabularyFromImportArticle(
        spell=search,
        definition=definition["definition"],
        part_of_speech=definition["partOfSpeech"],
        article_id=id,
        user_id=user.id
      )
      db.session.add(vocabulary)
      db.session.commit()
      return redirect(f"/articles/import/{category}/{id}/{search}")
    except:
      flash("no definitnon found","danger")
      return redirect(f"/articles/import/{category}/{id}/{search}")
  else:
    flash("Please login first","warning")
    return redirect("/login")

# route that update import article vocabulary image URL
@app.route("/article/import/add/img/<category>/<int:id>/<search>",methods=["POST"])
def article_add_image(search,id,category):
  if "username" in session:
    user = User.query.filter_by(username=session["username"]).first()
    target_vocabulary = VocabularyFromImportArticle.query.filter_by(spell=search,article_id=id,user_id=user.id).first()
    target_vocabulary.image_url = request.form.get("select_vocabulary")
    db.session.commit()
    flash("Image added successful","success")
    return redirect(f"/articles/import/{category}/{id}/{search}")
  else:
    flash("Please login first","warning")
    return redirect("/login")

# delete import article
@app.route("/delete/import/article/<category>/<int:id>",methods=["POST"])
def delete_import_article(id,category):
  if "username" in session:
    user = User.query.filter_by(username=session["username"]).first()
    target_article = ImportArticles.query.filter(ImportArticles.id==id,ImportArticles.user_id==user.id).first()
    db.session.delete(target_article)
    db.session.commit()
    flash("Article delete successful","warning")
    return redirect(f"/articles/import/{category}")
  else:
    flash("Please login first","warning")
    return redirect("/login")

# make import articles public 
@app.route("/articles/public/<category>/<int:id>",methods=["POST"])
def make_public(category,id):
  if "username" in session:
      user = User.query.filter_by(username=session["username"]).first()
      target_article = ImportArticles.query.get_or_404(id)
      # check if category is already exist 
      exists = db.session.query(Categories.id).filter_by(category=category).first() is not None

      # check if article is exist 
      ar_exists = db.session.query(Articles.id).filter_by(title=target_article.title).first() is not None
      if exists :
        _category = Categories.query.filter_by(category=category).first()
        make_public_article = Articles(
          author=target_article.author,
          title=target_article.title,
          category=_category.id,
          description = target_article.description,
          url=target_article.url,
          cover_url = target_article.cover_url,
          content = target_article.content,
          user_id = user.id
        )
        if ar_exists:
          flash("article already exist","warning")
          return redirect(f"/articles/import/{category}")
        else:
          db.session.add(make_public_article)
          db.session.commit()
          flash("Article has been public","success")
          return redirect(f"/articles/import/{category}")
      else:
        new_category = Categories(category=category,description=f"article about {category}")
        db.session.add(new_category)
        db.session.commit()
        make_public_article = Articles(
          author=target_article.author,
          title=target_article.title,
          category=new_category.id,
          description = target_article.description,
          url=target_article.url,
          cover_url = target_article.cover_url,
          content = target_article.content,
          user_id = user.id
        )
        if ar_exists :
          flash("article already exist","warning")
          return redirect(f"/articles/import/{category}")
        else:
          db.session.add(make_public_article)
          db.session.commit()
          flash("Article has been public","success")
          return redirect(f"/articles/import/{category}")
  else:
    flash("Please login first","warning")
    return redirect("/login")

# display import articles with id
@app.route("/vocabulary/article/list/imports",defaults={"id":None})
@app.route("/vocabulary/article/list/imports/<int:id>")
def vocabulary_import_list(id):
  if "username" in session:
    user = User.query.filter_by(username=session["username"]).first()
    if id != None:
      target_article = ImportArticles.query.get_or_404(id)
      vocabularies = VocabularyFromImportArticle.query.filter_by(article_id=target_article.id,user_id=user.id).all()
      return render_template("show_import_article_vocabulary.html",user=user,article=target_article,vocabularies=vocabularies)
    else:
      return render_template("vocabulary_list_import.html",user=user)
  else:
    flash("Please login first","warning")
    return redirect("/login")

# update import article vocabulary
@app.route("/vocabulary/article/list/imports/<int:id>/<search>",methods=["POST","GET"])
def edit_import_article_vocabulary(id,search):
  if "username" in session:
    user = User.query.filter_by(username=session["username"]).first()
    target_vocabulary = VocabularyFromImportArticle.query.filter_by(spell=search,user_id=user.id,article_id=id).first()
    if request.method == "POST":
      target_vocabulary.spell = request.form.get("vocabulary")
      target_vocabulary.part_of_speech = request.form.get("partOfSpeech")
      target_vocabulary.definition = request.form.get("definition")
      target_vocabulary.image_url = request.form.get("image_url")
      db.session.commit()
      flash("vocabulary update successful","success")
      return redirect(f"/vocabulary/article/list/imports/{id}")
    else:
      return render_template("edit_import_article_vocabulary.html",user=user,target_vocabulary=target_vocabulary)
  else:
    flash("Please login first","warning")
    return redirect("/login")

# practice route
@app.route("/practice")
def practice_route():
  if "username" in session:
    user = User.query.filter_by(username=session["username"]).first()
    return render_template("practice.html",user=user)
  else:
    flash("Please login first","warning")
    return redirect("/login")
initial_index = 0
# practice with own vocabulary list 
@app.route("/practice/own/vocabulary/list",methods=["POST","GET"],defaults={"id":None})
@app.route("/practice/own/vocabulary/list/<int:id>",methods=["POST","GET"])
def practice_own_list(id):
  if "username" in session:
    user = User.query.filter_by(username=session["username"]).first()
    if id != None: 
      if request.method == "POST":
        select_vocabularies = request.form.getlist("select_vocabulary")
        string_selects = ",".join(select_vocabularies)
        global initial_index
        initial_index = 0
        return redirect(f"/practice/own/vocabulary/list/{id}/page/?practice={string_selects}")
      else:
        list_name = VocabularyListName.query.get_or_404(id)
        return render_template("show_own_list_vocabularies.html",user=user,list_name=list_name)
    else:
      return render_template("show_own_vocabulary_list.html",user=user)
  else:
    flash("Please login first","warning")
    return redirect("/login")

# display practice vocabulary route
@app.route("/practice/own/vocabulary/list/<int:id>/page/",methods=["POST","GET"],defaults={"vocal_id":None})
@app.route("/practice/own/vocabulary/list/<int:id>/page/<int:vocal_id>",methods=["POST","GET"])
def practice_vocabulary_page(id,vocal_id):
  if "username" in session:
    # get user information
    user = User.query.filter_by(username=session["username"]).first()
    list_name = VocabularyListName.query.get_or_404(id)
    arguments = request.args["practice"]
    list_arguments = arguments.split(",")
    select_vocabularies = [VocabularyList.query.get_or_404(int(vol_id)) for vol_id in list_arguments]
    select_vocabularies_dictionary = [{"id":inx+1 ,"spell":vol.spell,"definition":vol.definition,"partOfSpeech":vol.part_of_speech,"image":vol.image_url} for inx,vol in enumerate(select_vocabularies)]
    # when vocal id show
    if vocal_id != None:
      if request.method == "POST":
        global initial_index
        if request.form.get("answer").lower() == select_vocabularies_dictionary[initial_index]["spell"].lower():
          initial_index += 1
          if initial_index == len(select_vocabularies):
            initial_index = 0
            return render_template("finish_practice.html",user=user,list_name=list_name,total=len(select_vocabularies_dictionary))
          return render_template("practice_flashcard.html",user=user,select_vocabulary=select_vocabularies_dictionary[initial_index],list_name=list_name,total=len(select_vocabularies_dictionary))
        else:
          return render_template("practice_flashcard.html",user=user,select_vocabulary=select_vocabularies_dictionary[initial_index],list_name=list_name,total=len(select_vocabularies_dictionary),wrongAnswer=True)
      else:
        return render_template("practice_flashcard.html",user=user,select_vocabulary=select_vocabularies_dictionary[initial_index],list_name=list_name,total=len(select_vocabularies_dictionary))
    else:
      # show a list of practice vocabulary
      return redirect(f"/practice/own/vocabulary/list/{id}/page/0?practice={arguments}")
  else:
    flash("Please login first","warning")
    return redirect("/login")

# practice with public/preload article vocabulary 
@app.route("/practice/public/vocabulary/list",methods=["POST","GET"],defaults={"id":None})
@app.route("/practice/public/vocabulary/list/<int:id>",methods=["POST","GET"])
def practice_public_vocabulary(id):
  if "username" in session:
      # get user information
      user = User.query.filter_by(username=session["username"]).first()
      if id != None:
        if request.method == "POST":
          global initial_index
          initial_index = 0
          select_vocabularies = request.form.getlist("select_vocabulary")
          string_selects = ",".join(select_vocabularies)
          return redirect(f"/practice/public/vocabulary/list/{id}/page?practice={string_selects}")
        else:
          vocabularies = VocabularyFromArticle.query.filter_by(user_id=user.id,article_id=id).all()
          target_article = Articles.query.get_or_404(id)
          return render_template("show_preload_article_vocabularies.html",user=user,vocabularies=vocabularies,target_article=target_article)
      else:
        return render_template("show_public_article_list.html",user=user)
  else:
    flash("Please login first","warning")
    return redirect("/login")

# display practice vocabulary route
@app.route("/practice/public/vocabulary/list/<int:id>/page",methods=["POST","GET"],defaults={"vocal_id":None})
@app.route("/practice/public/vocabulary/list/<int:id>/page/<int:vocal_id>",methods=["POST","GET"])
def practice_preload_vocabulary_page(id,vocal_id):
  if "username" in session:
    # get user information
    user = User.query.filter_by(username=session["username"]).first()
    article = Articles.query.get_or_404(id)
    arguments = request.args["practice"]
    list_arguments = arguments.split(",")
    select_vocabularies = [VocabularyFromArticle.query.get_or_404(int(vol_id)) for vol_id in list_arguments]
    select_vocabularies_dictionary = [{"id":inx+1 ,"spell":vol.spell,"definition":vol.definition,"partOfSpeech":vol.part_of_speech,"image":vol.image_url} for inx,vol in enumerate(select_vocabularies)]
    # when vocal id show
    if vocal_id != None:
      if request.method == "POST":
        global initial_index
        if request.form.get("answer").lower() == select_vocabularies_dictionary[initial_index]["spell"].lower():
          initial_index += 1
          if initial_index == len(select_vocabularies):
            initial_index = 0
            return render_template("finish_practice_preload.html",user=user,article=article,total=len(select_vocabularies_dictionary))
          return render_template("practice_flashcard_preload.html",user=user,select_vocabulary=select_vocabularies_dictionary[initial_index],article=article,total=len(select_vocabularies_dictionary))
        else:
          return render_template("practice_flashcard_preload.html",user=user,select_vocabulary=select_vocabularies_dictionary[initial_index],article=article,total=len(select_vocabularies_dictionary),wrongAnswer=True)
      else:
        return render_template("practice_flashcard_preload.html",user=user,select_vocabulary=select_vocabularies_dictionary[initial_index],article=article,total=len(select_vocabularies_dictionary))
    else:
      # show a list of practice vocabulary
      return redirect(f"/practice/public/vocabulary/list/{id}/page/0?practice={arguments}")
  else:
    flash("Please login first","warning")
    return redirect("/login")

# implement with import article practice with vocabulary list 
@app.route("/practice/imports/vocabulary/list",methods=["POST","GET"],defaults={"id":None})
@app.route("/practice/imports/vocabulary/list/<int:id>",methods=["POST","GET"])
def show_practice_import_vocabulary(id):
  if "username" in session:
    # get user information
    user = User.query.filter_by(username=session["username"]).first()
    if id != None:
      if request.method == "POST":
        global initial_index
        initial_index = 0
        select_vocabularies = request.form.getlist("select_vocabulary")
        string_selects = ",".join(select_vocabularies)
        return redirect(f"/practice/imports/vocabulary/list/{id}/page?practice={string_selects}")
      else:
        vocabularies = VocabularyFromImportArticle.query.filter_by(user_id=user.id,article_id=id).all()
        target_article = ImportArticles.query.get_or_404(id)
        return render_template("show_imports_article_vocabularies.html",user=user,vocabularies=vocabularies,target_article=target_article)
    else:
      return render_template("show_imports_article_list.html",user=user)
  else:
    flash("Please login first","warning")
    return redirect("/login")


# implement with import article practice with vocabularies 
@app.route("/practice/imports/vocabulary/list/<int:id>/page",methods=["POST","GET"],defaults={"vocal_id":None})
@app.route("/practice/imports/vocabulary/list/<int:id>/page/<int:vocal_id>",methods=["POST","GET"])
def practice_imports_vocabulary_page(id,vocal_id):
  if "username" in session:
    # get user information
    user = User.query.filter_by(username=session["username"]).first()
    article = ImportArticles.query.get_or_404(id)
    arguments = request.args["practice"]
    list_arguments = arguments.split(",")
    select_vocabularies = [VocabularyFromImportArticle.query.get_or_404(int(vol_id)) for vol_id in list_arguments]
    select_vocabularies_dictionary = [{"id":inx+1 ,"spell":vol.spell,"definition":vol.definition,"partOfSpeech":vol.part_of_speech,"image":vol.image_url} for inx,vol in enumerate(select_vocabularies)]
    # when vocal id show
    if vocal_id != None:
      if request.method == "POST":
        global initial_index
        if request.form.get("answer").lower() == select_vocabularies_dictionary[initial_index]["spell"].lower():
          initial_index += 1
          if initial_index == len(select_vocabularies):
            initial_index = 0
            return render_template("finish_practice_imports.html",user=user,article=article,total=len(select_vocabularies_dictionary))
          return render_template("practice_flashcard_imports.html",user=user,select_vocabulary=select_vocabularies_dictionary[initial_index],article=article,total=len(select_vocabularies_dictionary))
        else:
          return render_template("practice_flashcard_imports.html",user=user,select_vocabulary=select_vocabularies_dictionary[initial_index],article=article,total=len(select_vocabularies_dictionary),wrongAnswer=True)
      else:
        return render_template("practice_flashcard_imports.html",user=user,select_vocabulary=select_vocabularies_dictionary[initial_index],article=article,total=len(select_vocabularies_dictionary))
    else:
      # show a list of practice vocabulary
      return redirect(f"/practice/imports/vocabulary/list/{id}/page/0?practice={arguments}")
  else:
    flash("Please login first","warning")
    return redirect("/login")

# implement tweets home page
@app.route("/tweets")
def tweet_home_page():
  if "username" in session:
    # get user information
    user = User.query.filter_by(username=session["username"]).first()
    messages = (Message
                    .query
                    .filter(Message.user_id == user.id)
                    .order_by(Message.timestamp.desc())
                    .limit(100)
                    .all())

    following_users_message = (
      Message
        .query
        .filter(Message.user_id.in_([user.id for user in user.following]))
        .order_by(Message.timestamp.desc())
        .limit(100)
        .all()
    )
    
    return render_template("tweet_home.html",
        user=user,
        messages=messages,
        following_users_message=following_users_message,
        target_user = user
    )
  else:
    flash("Please login first","warning")
    return redirect("/login")

# display user tweets 
@app.route("/tweets/<username>/add",methods=["POST","GET"])
def add_tweets(username):
  if "username" in session:
    # get user information
    user = User.query.filter_by(username=session["username"]).first()
    form = MessageForm()
    if form.validate_on_submit():
      message = Message(text=form.text.data,timestamp=datetime.utcnow(),user_id=user.id)
      db.session.add(message)
      db.session.commit()
      flash("successfully added your tweets","success")
      return redirect("/tweets")
    return render_template("add_tweets.html",user=user,form=form)
  else:
    flash("Please login first","warning")
    return redirect("/login")

# add message comments routes 
@app.route("/tweets/<username>/<int:message_id>/comment",methods=["POST","GET"],defaults={'user_id': None})
@app.route("/tweets/<username>/<int:message_id>/comment/<int:user_id>",methods=["POST","GET"])
def add_message_comment(username,message_id,user_id):
  if "username" in session:
    # get user information
    user = User.query.filter_by(username=username).first()
    comment = CommentMessage(text=request.form.get("comment"),timestamp=datetime.utcnow(),user_id=user.id,message_id=message_id)
    db.session.add(comment)
    db.session.commit()
    if user_id == None:
      return redirect("/tweets")
    else:
      return redirect(f"/tweets/users/{user_id}")
  else:
    flash("Please login first","warning")
    return redirect("/login")

# display all user and able to search users 
@app.route("/tweets/users",methods=["POST","GET"])
def show_all_user():
  if "username" in session:
    # get user information
    user = User.query.filter_by(username=session["username"]).first()
    follows_id = [user.id for user in user.following]
    if request.args:
      search_turm = request.args["search_user"].lower()
      search = "%{}%".format(search_turm)
      search_user = User.query.filter(User.first_name.ilike(search)).all()
      return render_template("show_all_users.html",user=user,all_user=search_user,follows_id=follows_id,argument=search_turm)
    else:
      all_user = User.query.all()
      return render_template("show_all_users.html",user=user,all_user=all_user,follows_id=follows_id)
  else:
    flash("Please Login first","warning")
    return redirect("/login")

# show specific user information
@app.route("/tweets/users/<int:id>")
def show_specific_user(id):
  if "username" in session:
    # get user information
    user = User.query.filter_by(username=session["username"]).first()
    messages = (Message
                    .query
                    .filter(Message.user_id == id)
                    .order_by(Message.timestamp.desc())
                    .limit(100)
                    .all())
    target_user = User.query.get_or_404(id)
    if request.args:
      return render_template("tweet_home.html",user=user,messages=messages,id=id,argument=request.args["search_user"],target_user=target_user)
    else:
      return render_template("tweet_home.html",user=user,messages=messages,id=id,target_user=target_user)
  else:
    flash("Please login first","warning")
    return redirect("/login")

# adding following
@app.route("/tweets/user/follow/<int:user_id>",methods=["POST"])
def add_follow_tweet(user_id):
  if "username" in session:
    # get user information
    user = User.query.filter_by(username=session["username"]).first()
    thefollow = Follows(user_being_followed_id=user_id,user_following_id=user.id)
    db.session.add(thefollow)
    db.session.commit()
    if request.args:
      search_term = request.args["search_user"]
      return redirect(f"/tweets/users?search_user={search_term}")
    else:
      return redirect("/tweets/users")
  else:
    flash("Please login first","warning")
    return redirect("/login")

# adding un following
@app.route("/tweets/user/unfollow/<int:user_id>",methods=["POST"])
def add_un_follow_tweet(user_id):
  if "username" in session:
    # get user information
      user = User.query.filter_by(username=session["username"]).first()
      thefollow = Follows.query.filter_by(user_being_followed_id=user_id,user_following_id=user.id).first()
      db.session.delete(thefollow)
      db.session.commit()
      if request.args:
        search_term = request.args["search_user"]
        return redirect(f"/tweets/users?search_user={search_term}")
      else:
        return redirect("/tweets/users")
  else:
    flash("Please login first","warning")
    return redirect("/login")

# adding a route for delete tweet message
@app.route("/tweet/delete/<int:tweet_id>", methods=["POST"])
def delete_tweet(tweet_id):
  if "username" in session:
    # get user information
    user = User.query.filter_by(username=session["username"]).first()
    deleteMessage = Message.query.filter(
      Message.id==tweet_id,
      Message.user_id==user.id).first()
    db.session.delete(deleteMessage)
    db.session.commit()
    return redirect("/tweets")
  else:
    flash("Please login first")
    return redirect("/login")

# adding a route to delete tweet comments
@app.route('/tweet/delete/comment/<int:msg_id>/<int:comment_id>', methods=["POST"],defaults={'current_user_id': None})
@app.route('/tweet/delete/comment/<int:msg_id>/<int:comment_id>/<int:current_user_id>', methods=["POST"])
def delete_tweet_comment(msg_id,comment_id,current_user_id):
  if "username" in session:
      # get user information
      user = User.query.filter_by(username=session["username"]).first()
      delete_comment = CommentMessage.query.filter(
        CommentMessage.id==comment_id,
        CommentMessage.message_id==msg_id,
        CommentMessage.user_id==user.id).first()
      db.session.delete(delete_comment)
      db.session.commit()
      if current_user_id == None:
        return redirect("/tweets")
      else:
        return redirect(f"/tweets/users/{current_user_id}")
  else:
    flash("Please login first")
    return redirect("/login")

# add tweet message likes feature 
@app.route("/tweet/like/<int:meg_id>",methods=["POST"],defaults={'current_user_id': None})
@app.route("/tweet/like/<int:meg_id>/<int:current_user_id>",methods=["POST"])
def tweet_message_like(meg_id,current_user_id):
  if "username" in session:
      # get user information
      user = User.query.filter_by(username=session["username"]).first()
      try:
        like_msg = Likes(user_id=user.id,message_id=meg_id)
        db.session.add(like_msg)
        db.session.commit()
        if current_user_id != None:
          return redirect(f"/tweets/users/{current_user_id}")
        else:
          return redirect("/tweets")
      except exc.IntegrityError:
        db.session.rollback()
        target_like= Likes.query.filter(Likes.message_id==meg_id,Likes.user_id==user.id).first()
        db.session.delete(target_like)
        db.session.commit()
        if current_user_id != None:
          return redirect(f"/tweets/users/{current_user_id}")
        else:
          return redirect("/tweets")
  else:
    flash("Please login first","warning")
    return redirect("/login")


# add a route for like tweet comment feature 
@app.route("/tweet/like/comment/<int:comment_id>",methods=["POST"],defaults={'current_user_id': None})
@app.route("/tweet/like/comment/<int:comment_id>/<int:current_user_id>",methods=["POST"])
def tweet_comment_like(comment_id,current_user_id):
  if "username" in session:
      # get user information
      try:
        user = User.query.filter_by(username=session["username"]).first()
        like_comment = CommentLikes(comment_id=comment_id,user_id=user.id)
        db.session.add(like_comment)
        db.session.commit()
        if current_user_id != None:
          return redirect(f"/tweets/users/{current_user_id}")
        else:
          return redirect("/tweets")
      except exc.IntegrityError:
        db.session.rollback()
        target_like= CommentLikes.query.filter(CommentLikes.comment_id==comment_id,CommentLikes.user_id==user.id).first()
        db.session.delete(target_like)
        db.session.commit()
        if current_user_id != None:
          return redirect(f"/tweets/users/{current_user_id}")
        else:
          return redirect("/tweets")
  else:
    flash("Please login first","warning")
    return redirect("/login")

# display current user messages
@app.route("/tweets/messages",defaults={"current_user_id": None})
@app.route("/tweets/messages/<int:current_user_id>")
def show_tweets_message(current_user_id):
  if "username" in session:
    user = User.query.filter_by(username=session["username"]).first()
    if current_user_id != None:
      messages = (Message
                      .query
                      .filter(Message.user_id == current_user_id)
                      .order_by(Message.timestamp.desc())
                      .limit(100)
                      .all())
      return render_template("show_user_messages.html",user=user,messages=messages,current_user_id=current_user_id)
    else:
      messages = (Message
                      .query
                      .filter(Message.user_id == user.id)
                      .order_by(Message.timestamp.desc())
                      .limit(100)
                      .all())
      return render_template("show_user_messages.html",user=user,messages=messages)
  else:
    flash("Please login first","warning")
    return redirect("/login")

# deleted message comments on own messages pages
@app.route('/messages/delete/comment/<int:msg_id>/<int:comment_id>', methods=["POST"],defaults={'current_user_id': None})
@app.route('/messages/delete/comment/<int:msg_id>/<int:comment_id>/<int:current_user_id>', methods=["POST"])
def delete_messages_comment(msg_id,comment_id,current_user_id):
  if "username" in session:
      # get user information
      user = User.query.filter_by(username=session["username"]).first()
      delete_comment = CommentMessage.query.filter(
        CommentMessage.id==comment_id,
        CommentMessage.message_id==msg_id,
        CommentMessage.user_id==user.id).first()
      db.session.delete(delete_comment)
      db.session.commit()
      if current_user_id != None:
        return redirect(f"/tweets/messages/{current_user_id}")
      else:
        return redirect("/tweets/messages")
  else:
    flash("Please login first")
    return redirect("/login")

# add new comment on messages pages
@app.route("/messages/<username>/<int:message_id>/comment",methods=["POST"],defaults={"current_user_id": None})
@app.route("/messages/<username>/<int:message_id>/comment/<int:current_user_id>",methods=["POST"])
def messages_comment(username,message_id,current_user_id):
  if "username" in session:
    # get user information
    user = User.query.filter_by(username=username).first()
    comment = CommentMessage(text=request.form.get("comment"),timestamp=datetime.utcnow(),user_id=user.id,message_id=message_id)
    db.session.add(comment)
    db.session.commit()
    if current_user_id != None:
      return redirect(f"/tweets/messages/{current_user_id}")
    else:
      return redirect("/tweets/messages")
  else:
    flash("Please login first","warning")
    return redirect("/login")
  
# delete message on messages pages
@app.route("/messages/delete/<int:tweet_id>", methods=["POST"])
def delete_message(tweet_id):
  if "username" in session:
    # get user information
    user = User.query.filter_by(username=session["username"]).first()
    deleteMessage = Message.query.filter(
      Message.id==tweet_id,
      Message.user_id==user.id).first()
    db.session.delete(deleteMessage)
    db.session.commit()
    return redirect("/tweets/messages")
  else:
    flash("Please login first")
    return redirect("/login")

# like message on messages page
@app.route("/messages/like/<int:meg_id>",methods=["POST"],defaults={"current_user_id": None})
@app.route("/messages/like/<int:meg_id>/<int:current_user_id>",methods=["POST"])
def messages_message_like(meg_id,current_user_id):
  if "username" in session:
      # get user information
      user = User.query.filter_by(username=session["username"]).first()
      try:
        like_msg = Likes(user_id=user.id,message_id=meg_id)
        db.session.add(like_msg)
        db.session.commit()
        if current_user_id != None:
          return redirect(f"/tweets/messages/{current_user_id}")
        else:
          return redirect("/tweets/messages")
      except exc.IntegrityError:
        db.session.rollback()
        target_like= Likes.query.filter(Likes.message_id==meg_id,Likes.user_id==user.id).first()
        db.session.delete(target_like)
        db.session.commit()
        if current_user_id != None:
          return redirect(f"/tweets/messages/{current_user_id}")
        else:
          return redirect("/tweets/messages")
  else:
    flash("Please login first","warning")
    return redirect("/login")
  
# like message comment on messages page
@app.route("/messages/like/comment/<int:comment_id>",methods=["POST"],defaults={"current_user_id": None})
@app.route("/messages/like/comment/<int:comment_id>/<int:current_user_id>",methods=["POST"])
def messages_comment_like(comment_id,current_user_id):
  if "username" in session:
      # get user information
      try:
        user = User.query.filter_by(username=session["username"]).first()
        like_comment = CommentLikes(comment_id=comment_id,user_id=user.id)
        db.session.add(like_comment)
        db.session.commit()
        if current_user_id != None:
          return redirect(f"/tweets/messages/{current_user_id}")
        else:
          return redirect("/tweets/messages")
      except exc.IntegrityError:
        db.session.rollback()
        target_like= CommentLikes.query.filter(CommentLikes.comment_id==comment_id,CommentLikes.user_id==user.id).first()
        db.session.delete(target_like)
        db.session.commit()
        if current_user_id != None:
          return redirect(f"/tweets/messages/{current_user_id}")
        else:
          return redirect("/tweets/messages")
  else:
    flash("Please login first","warning")
    return redirect("/login")

# show all following user 
@app.route("/tweets/following",defaults={"current_user_id": None})
@app.route("/tweets/following/<int:current_user_id>")
def show_following_user(current_user_id):
  if "username" in session:
    # get user information
    user = User.query.filter_by(username=session["username"]).first()
    if current_user_id != None:
      current_user = User.query.get_or_404(current_user_id)
      return render_template("show_following_user.html",user=user,current_user=current_user)
    else:
      return render_template("show_following_user.html",user=user)
  else:
    flash("Please login first","warning")
    return redirect("/login")

# un-following user on tweets following pages
@app.route("/tweets/following/unfollow/<int:user_id>",methods=["POST"])
def unfollow_following(user_id):
  if "username" in session:
    # get user information
      user = User.query.filter_by(username=session["username"]).first()
      thefollow = Follows.query.filter_by(user_being_followed_id=user_id,user_following_id=user.id).first()
      db.session.delete(thefollow)
      db.session.commit()
      return redirect("/tweets/following")
  else:
    flash("Please login first","warning")
    return redirect("/login")

# show all follower user page 
@app.route("/tweets/follower",defaults={"visit_user_id":None})
@app.route("/tweets/follower/<int:visit_user_id>")
def show_follower(visit_user_id):
  if "username" in session:
    # get user information
      user = User.query.filter_by(username=session["username"]).first()
      if visit_user_id != None:
        visited_user = User.query.get_or_404(visit_user_id)
        return render_template("show_follower_user.html",user=user,visited_user=visited_user)
      else:
        return render_template("show_follower_user.html",user=user)
  else:
    flash("Please login first","warning")
    return redirect("/login")


# about section on leetEnglish
@app.route("/about")
def leetEnglishAbout():
  if "username" in session:
    # get user information
      user = User.query.filter_by(username=session["username"]).first()
      return render_template("about_leetenglish.html",user=user)
  else:
    flash("Please login first","warning")
    return redirect("/login")