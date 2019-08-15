from flask import Flask, render_template, send_file, request
from selenium import webdriver
from PIL import Image
from io import BytesIO, StringIO
import os, base64

CAPTCHA_FOLDER = os.path.join('static', 'images')
nfce_code = '24170813064901000199650010000038481801014103'

# create the application object
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = CAPTCHA_FOLDER

# use decorators to link the function to a url
@app.route('/', methods=['POST', 'GET'])
def home():
	if request.method == 'POST':
		return submit_result(request.form['captcha_input'])
	elif request.method == 'GET':
		return render_page()		

def render_page():
	global driver

	url = 'https://nfce.set.rn.gov.br/portalDFE/NFCe/ConsultaNFCe.aspx'
	driver.get(url)
	captcha = driver.find_element_by_id("img_captcha")
	captchaLocation = captcha.location
	captchaSize = captcha.size

	fullPage = driver.get_screenshot_as_png()
	img = Image.open(BytesIO(fullPage))
	img = img.crop((int(captchaLocation['x']), int(captchaLocation['y']), int(captchaLocation['x'] + captchaSize['width']), int(captchaLocation['y'] + captchaSize['height'])))
	img = img.convert('RGB')

	img_io = BytesIO()
	img.save(img_io, 'jpeg', quality=100)
	img_io.seek(0)
	result = base64.b64encode(img_io.getvalue())
	return render_template('index.html', captcha_image=result.decode('ascii'))  # render a template

def submit_result(input_data):
	global driver

	access_key = driver.find_element_by_id('ctl03_txt_chave_acesso')
	captcha_key = driver.find_element_by_id('txt_cod_antirobo')
	button = driver.find_element_by_id('btn_consulta_resumida')

	access_key.send_keys(nfce_code)
	captcha_key.send_keys(input_data)
	button.click()

	# Checking results
	page = driver.page_source
	try:
		error_message = driver.find_element_by_id('lblMensagemErro') # Verifica a exsitência do id com a mensagem de erro
		return render_template('unsuccess.html')  # render a template
	except:
		return render_template('success.html')  # render a template
		
	

# start the server with the 'run()' method
if __name__ == '__main__':
	global driver
	driver = webdriver.PhantomJS()
	port = int(os.environ.get('PORT', 8080))
	app.run(debug=True, host='0.0.0.0', port=port)