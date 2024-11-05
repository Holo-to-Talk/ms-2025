@app.route('/user/login', methods=['GET', 'POST'])
def login():
    error_msg = []
    
    # セッションの有無でログイン画面を切り替える
    # get Requestがおくられたら
    if request.method == 'GET':
        if 'user' in session:
            return redirect("/")
        else:
            return render_template('login.html')
    
    # post Request が送られたら
    if request.method == 'POST':
        mail = request.form.get('mail', '')
        password = request.form.get('password', '')
        
        result = login_trial(mail,password)
        
        if result:
            session['user'] = result
            return redirect("/")
    else:
        return render_template("login.html", error_msg=[])
    
    
    
    def login_trial(mail, password):
    try:
        with app.app_context():
            cur = mysql.connection.cursor()
            sql_query = "SELECT * FROM staff_list WHERE mail = %s"
            cur.execute(sql_query, (mail,))
            user_info = cur.fetchone()
            if user_info:
                stored_salt = user_info[4][:29].encode('utf-8')
                
                hashed_input_password = bcrypt.hashpw(password.encode('utf-8'), stored_salt)

                if hashed_input_password == user_info[4].encode('utf-8'):
                    if int(user_info[18]) == 0: #ログインフラグのチェック
                        session['user'] = user_info
                        return True
                    else:
                        error_msg.append("※ログインが無効化されています。")
                        return False
                else:
                    error_msg.append("※メールアドレスまたはパスワードが間違っています。")
                    return False
            else:
                error_msg.append("※メールアドレスまたはパスワードが間違っています。")
                return False
            
    except Exception as e:
        error_msg.append("SQL文エラー: " + str(e))
        return False