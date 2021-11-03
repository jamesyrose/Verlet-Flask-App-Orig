from flask import Flask, request, render_template as htmlr, stream_with_context, redirect, url_for, Response, jsonify, send_file
import os
import stripe
from logger import *
import time
from datetime import datetime
from emailer import send_mail


app = Flask(__name__, 
            static_url_path='/static')
stripe.api_key = sec_key
rpath = os.path.dirname(os.path.abspath(__file__))

# MAIN PAGE  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@app.route("/")
def home():
    return htmlr("index.html")
@app.route("/", methods=['POST']) 
def home_sendnote():
    if request.form['sendnote'] == 'sendnote':
        name = request.form["name"]
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']
        build_message = "From: {} \n  Email: {} \n Phone: {} \n {}".format(name, email, phone, message)
        send_mail("info@verlet.io", "Customer Inquisition", build_message)
    return htmlr('index.html') 


# Purchase Data Page >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@app.route("/getdata")
def purhcase_page():
    _blanks = """                           &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;

              """
    return htmlr("purchase.html", valid_values=_blanks)

@app.route('/getdata', methods=['POST'])
def my_form_post_quote():
    if "submit_button" in request.form.keys():
        symbols = request.form['symbols'].upper().replace("-", "/")
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        res = request.form["resolution"]
        promo = request.form["promo"]
        if date_check(start_date) and date_check(end_date):
            valid_values, price, back_string = symbol_check(symbols, res, start_date, end_date, promo)
            un_id = id_generator()
            buy = r"""<form action="/checkout" method='POST'> 
            <script src = 'https://checkout.stripe.com/checkout.js' class='stripe-button'" 
            data-key = '{0}' 
            data-amount = '{1}' 
            data-name = 'Buy Data' 
            data-discription = '' 
            data-image = 'static/logo.png' 
            data-locale = 'auto' >
            </script>
            <script>
            // Hide default stripe button, be careful there if you
            // have more than 1 button of that class
            document.getElementsByClassName("stripe-button-el")[0].style.display = 'none';
            </script>
            <input type="submit" name="submit_button" value="Buy Data Now!" 
            class="btn-theme btn-theme-sm btn-base-bg text-uppercase">
            <input type="hidden" name="order_id" value="{2}">
             </form>""".format(pub_key, price * 100, un_id)

            order_string = "{0},{1},{2},{3}".format(un_id, price *100 , back_string, res)
            os.system("echo '{0}' >> {1}".format(order_string,
                                               os.path.join(rpath, "orderQuote.log")
                                               )
                                               )
            valid_values = " <div style='background-color: rgb(70, 70, 70, .35); padding: 15px;'> <h4><font color ='white'>{}</font></h4></div>".format(valid_values)
            # checking to make sure server is running
            if (int(datetime.now().timestamp()) - float(os.popen("cat {}".format(os.path.join(rpath, "running.txt"))).read().replace("\n", ""))) >  3600:
                add_string = "<p><font color='red'> Our servers are currently inactive.<br> Your order will be processed once the server is active again. <br> We apologize for any Inconvience</font></p>"
                valid_values = "{}{}".format(add_string, valid_values)
            return htmlr("purchase.html", price_est="${}".format(price), valid_values=valid_values, buy_button=buy)
        else: 
            return htmlr("purchase.html", price_est="{}".format("Dates: wrong format or value. <br> earliest Date is 2000-01-01"))
    elif 'sendnote' in request.form.keys():
        name = request.form["name"]
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']
        build_message = "From: {} \n  Email: {} \n Phone: {} \n {}".format(name, email, phone, message)
        send_mail("info@verlet.io", "Customer Inquisition", build_message)
        return htmlr('purchase.html')
    else:
        pass
    return htmlr('purchase.html')




@app.route("/bulk", methods=["POST"])
def bulk(): 
    def stripe_charge(customer, price, bulk):
        charge = stripe.Charge.create(
            customer = customer.id,
            amount = price,
            currency = 'usd',
            description = "Verlet Bulk Download {}".format(bulk)
            )
    bulk_down = request.form["bulk"]
    customer = stripe.Customer.create(email=request.form['stripeEmail'],
                                     source=request.form["stripeToken"])
    
    if bulk_down in ["tech", "pharma", "banks"]:
        stripe_charge(customer, 5999, bulk_down)
        return redirect(url_for("bulk_download", file_name="{}.zip".format(bulk_down)))
    elif bulk_down in ["commodities", "blue"]:
        stripe_charge(customer, 14999, bulk_down)
        return redirect(url_for('bulk_download', file_name="{}.zip".format(bulk_down)))


       
@app.route('/bulk_download/<file_name>')  
def bulk_download(file_name):
   zip_file = "/home/verletio/web_main/files/PreMadeOptions/{}".format(file_name)
   print(zip_file)
   return send_file(zip_file)


@app.route('/checkout', methods=['POST'])
def checkout():
    # Set your secret key: remember to change this to your live secret key in production
    # See your keys here: https://dashboard.stripe.com/account/apikeys
    un_id = request.form["order_id"]
    order_req = os.popen("grep {} {}".format(un_id, 
                                             os.path.join(rpath, "orderQuote.log"))
                        ).read().split(",")
    if len(order_req) < 3:
        return "An Error Occured, please try again <br> If the problem persists, please contact us"
    price = order_req[1]
    data_request = order_req[2]
    res = order_req[3].replace("\n", "")
    customer = stripe.Customer.create(email=request.form['stripeEmail'], 
                                     source=request.form["stripeToken"])
    charge = stripe.Charge.create(
        customer = customer.id,
        amount = int(round(float(price))),
        currency = 'usd',
        description = "Data {}".format(un_id)
        ) 
    order_time = int(datetime.now().timestamp())
    send_req(un_id, 
             request.form['stripeEmail'], 
             "{}--{}".format(res, 
                             data_request.replace("%20%", "-")
                                         .replace("\n", "")), 
             price, 
             request.form["stripeToken"], 
             order_time)
    return redirect(url_for("success", price=price, data="{}--{}".format(res, data_request), token = request.form["stripeToken"], email = request.form["stripeEmail"].lower().replace("@", "AT"), un_id=un_id))

@app.route("/success/<price>/<data>/<token>/<email>/<un_id>")
def success(price, data, token, email, un_id): 
    price = float(price)/100
    d = open(os.path.join(rpath, "templates", "loading.html")).read()
    d = d.replace("<price>", str(price))\
         .replace("<data>", data\
                .replace("--", "<br>")\
                .replace("-",  "  "))\
         .replace("<raw_data>", data)\
         .replace("<token>", token)\
         .replace("<email>", email.replace("AT", "@"))\
         .replace("<email2>", email)\
         .replace("<un_id>", un_id)
    email_string = """Your Order Is Being Processed \n 
                      Please allow time as large demands and high traffic activity can throttle rates\n\n
                      Order ID:  {0}\n
                      Charged: USD $ {1}\n
                      Data: \n
                      {2} \n \n
                      If you encounter any errors, please contact us at info@verlet.io
                      """.format(un_id, int((float(price)*100))/100, data.replace("----", " Resolution\n").replace("--", "\n"))
    send_mail(email.replace("AT","@"), "Verlet Data Order Reciept", email_string)
    return d

@app.route("/slow/<un_id>")
def slow(un_id): 
    while True: 
        if "No,{}".format(un_id) not in open(os.path.join(rpath, "request_log.csv")).read():
            break
    return jsonify("oh so slow")


@app.route("/done/<price>/<data>/<token>/<email>/<un_id>")
def done(price, data, token, email, un_id):
    if "ERROR,{}".format(un_id) in open(os.path.join(rpath, "request_log.csv")).read(): 
        template = open(os.path.join(rpath, "templates", "error.html")).read()
        template = template.replace("<price>", str(price))\
                           .replace("<data>", data.replace("--", "<br>")
                                                  .replace("%20%", " ")\
                                                  .replace("-",  "  "))\
                           .replace("<token>", token)\
                           .replace("<email>", email.replace("AT", "@"))\
                           .replace("<un_id>", un_id)\
                           .replace("<d_link>", "https://storage.googleapis.com/verlet/{}.zip".format(un_id))
        return template

    template = open(os.path.join(rpath, "templates", "download_ready.html")).read()
    template = template.replace("<price>", str(price))\
                        .replace("<data>", data.replace("--", "<br>")
                                                .replace("%20%", " ")\
                                                .replace("-",  "  "))\
                        .replace("<token>", token)\
                        .replace("<email>", email.replace("AT", "@"))\
                        .replace("<un_id>", un_id)\
                        .replace("<d_link>", "https://storage.googleapis.com/verlet/{}.zip".format(un_id))
    return template

# About Us >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@app.route("/about")
def about():
    return htmlr("about.html")

@app.route("/about", methods=['POST'])
def about_sendnote():
    if request.form['sendnote'] == 'sendnote':
        name = request.form["name"]
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']
        build_message = "From: {} \n  Email: {} \n Phone: {} \n {}".format(name, email, phone, message)
        send_mail("info@verlet.io", "Customer Inquisition", build_message)
    return htmlr('about.html')



# Avaliable Data >>>>>>>>>>>>>>>>>>>>>>>>>>>....
@app.route("/avadata")
def avadata():
    m = open(os.path.join(rpath, "files", "minute.txt")).read().replace("\n", "<br>&nbsp&nbsp").replace(",", "   ").replace(" ", "&nbsp;").replace("Ticker", "&nbsp&nbspTicker")
    s = open(os.path.join(rpath, "files", "second.txt")).read().replace("\n", "<br>&nbsp&nbsp").replace(",", "   ").replace(" ", "&nbsp;").replace("Ticker", "&nbsp&nbspTicker")
    b = open(os.path.join(rpath, "files", "big.txt")).read().replace("\n", "<br>&nbsp&nbsp").replace(",", "   ").replace(" ", "&nbsp;").replace("Ticker", "&nbsp&nbspTicker")
    return htmlr("products.html", minute="<font face='Courier' size='-1' color='white'>{}</font>".format(m), second="<font face='Courier' size='-1' color='white'>{}</font>".format(s), big="<font face='Courier' size='-1' color='white'>{}</font>".format(b))

@app.route('/avadata', methods=['POST'])
def avadata_sendnote():
    if request.form['sendnote'] == 'sendnote':
        name = request.form["name"]
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']
        build_message = "From: {} \n  Email: {} \n Phone: {} \n {}".format(name, email, phone, message)
        send_mail("info@verlet.io", "Customer Inquisition", build_message)
    return htmlr('purchase.html')


# FAQ>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@app.route("/faq")
def faq():
    return htmlr("faq.html")

@app.route("/faq", methods=['POST'])
def faq_sendnote():
    if request.form['sendnote'] == 'sendnote':
        name = request.form["name"]
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']
        build_message = "From: {} \n  Email: {} \n Phone: {} \n {}".format(name, email, phone, message)
        send_mail("info@verlet.io", "Customer Inquisition", build_message)
    return htmlr('faq.html')




# TERMS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@app.route("/termsofuse")
def terms():
    return htmlr("terms.html")

# privacy >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@app.route("/privacypolicy")
def privacy():
    return htmlr("privacy.html")

# DOWNLOAD PAGE >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@app.route("/download")
def download_page(): 
    return htmlr("download.html")
@app.route("/download",  methods=["POST"])
def download_link(): 
    trans_id = request.form["id"].strip()
    email = request.form["email"].strip()
    if check_download_exists(trans_id, email):
        button = """ <a href="https://storage.googleapis.com/verlet/{}.zip"><button type="button" class="btn-theme btn-theme-sm btn-base-bg text-uppercase">Download Here</button>
        """.format(trans_id)
        return htmlr("download.html", buy_button=button)
    elif trans_id not in os.popen("grep {} {}".format(trans_id, os.path.join(rpath, "request_log.csv"))).read():
        message = """<font color="white"><h2>  
        Transaction ID not found</font></h2> 
        """
        return htmlr("download.html", message=message) 
       
    else:
        message  = """<font color="white"><h4>  
        Please Wait, we need to process your download again. <br><br>
        Personal Downloads are only avaliable 24 hrs after ordered. <br><br>
        You will be emailed when it is done <br></font></h4> 
        """
        # checking to make sure server is running
        if (int(datetime.now().timestamp()) - float(os.popen("cat {}".format(os.path.join(rpath, "running.txt"))).read().replace("\n", ""))) > 3600:
            add_string = "<p><font color='red'> Our servers are currently inactive.<br> Your order will be processed once the server is active again. <br> We apologize for any Inconvience</font></p>"
            message = "{}{}".format(add_string, message)
        reorder(trans_id, email)
        return htmlr("download.html", message=message)

if __name__ == "__main__":
    app.run(debug=True)
