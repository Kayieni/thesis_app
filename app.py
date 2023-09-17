from flask import Flask
from flask_mysqldb import MySQL
from flask_cors import CORS
from views import views

app = Flask(__name__) #init the flask server
app.register_blueprint(views, url_prefix = "/") #to link the views file
CORS(app)
#Add database configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'thesis'
 
app.secret_key = 'This is your secret key to utilize session in Flask'

mysql = MySQL(app)

if __name__ == '__main__':
	app.run(debug=True, port=8000) #to imediately apply the changes on prefered port