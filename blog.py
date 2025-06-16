from flask import Flask, render_template, url_for
app = Flask(__name__)

posts = [
    {
        'author' : 'David',
        'title' : 'Blog Post 1',
        'content' : 'First post content',
        'date_posted' : 'April 20, 2023'
    },
    {
        'author' : 'John',
        'title' : 'Blog Post 2',
        'content' : 'Second post content',
        'date_posted' : 'April 21, 2023'
    },
    {
        'author' : 'Jane',
        'title' : 'Blog Post 3',
        'content' : 'Third post content',
        'date_posted' : 'April 22, 2023'
    }
]

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)