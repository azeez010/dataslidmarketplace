from datetime import datetime
from utils import upload_image, upload_blog_image
from models import Blog, app, db
from flask import request, redirect, flash, url_for, render_template
from flask_login import login_required, current_user
from flask_ckeditor import CKEditor

ROWS_PER_PAGE = 10
app.config['CKEDITOR_PKG_TYPE'] = 'full-all'
# ck = CKEditor(app)

@app.route("/blog", methods=["GET"])
def blog():
    id = request.args.get('id')
    blog = Blog.query.filter_by(id=id).first()
    return render_template("blog/blog.html", blog=blog)

@app.route("/blogs", methods=["GET"])
def blogs():
    page = request.args.get('page', 1, type=int)
    blogs = Blog.query.order_by(Blog.datetime.desc()).paginate(page=page, per_page=ROWS_PER_PAGE)
    return render_template("blog/blogs.html", blogs=blogs)


@app.route("/your-blogs", methods=["GET"])
def your_blogs():
    page = request.args.get('page', 1, type=int)
    blogs = Blog.query.filter_by(user_id=current_user.id).order_by(Blog.datetime.desc()).paginate(page=page, per_page=ROWS_PER_PAGE)
    return render_template("blog/your_blogs.html", blogs=blogs)


@app.route("/create-blog", methods=["GET", "POST"])
@login_required
def create_blog():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("ckeditor")
        summary = request.form.get("summary")
        image = request.files.get("image")
        slug = title.replace(" ", "-")
        blog = Blog(user_id=current_user.id, title=title, slug=slug, description=description, summary=summary, datetime=datetime.now())
        db.session.add(blog)
        # OBJ_KEY for the image
        OBJ_KEY = "blog"
        # upload image 
        upload_blog_image(blog, OBJ_KEY, image)
        # Commit to db
        db.session.commit()
        flash("Your successfully created a blog")
        return redirect(url_for("blogs"))
    else:
        return render_template("blog/create.html")

@app.route("/edit-blog", methods=["GET", "POST"])
@login_required
def edit_blog():
    if request.method == "POST":
        blog_id = request.form.get("id") 
        blog = Blog.query.filter_by(id=blog_id).first()
        title = request.form.get("title")
        description = request.form.get("ckeditor")
        summary = request.form.get("summary")
        image = request.files.get("image")
        slug = title.replace(" ", "-")
        
        if blog.user.id == current_user.id:
            blog.title = title
            blog.description = description
            blog.summary = summary
            blog.slug = slug

            OBJ_KEY = "blog"
            # upload image 
            upload_blog_image(blog, OBJ_KEY, image)
            # Commit to db    
            db.session.commit()
            flash("You have succesfully editted the blog")
            return redirect(url_for('blog', id=blog.id, title=blog.slug, date=blog.datetime.strftime('%d-%m-%Y') ))
        else:
            flash("You cannot edit this blog")
            return redirect(url_for('blog', id=blog.id, title=blog.slug, date=blog.datetime.strftime('%d-%m-%Y') ))
    else:
        blog_id = request.args.get("id") 
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template("blog/edit.html", blog=blog)

@app.route("/delete-blog", methods=["GET", "POST"])
@login_required
def delete_blog():
    blog_id = request.args.get("id") 
    
    blog = Blog.query.filter_by(id=blog_id).first()
    if blog:
        if blog.user.id == current_user.id:
            db.session.delete(blog)
            db.session.commit()
            
            flash("You have succesfully deleted the blog")
            return redirect(url_for("your_blogs"))
        else:
            flash("You cannot delete this blog")
            return redirect(url_for("blog", id=id))
    else:
            flash("Blog no longer exists")
            return redirect(url_for("blog", id=id))
