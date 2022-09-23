from bson import ObjectId
from pymongo import MongoClient
import certifi
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

SECRET_KEY = 'CODEQNA'

# client = MongoClient('mongodb+srv://test:sparta@cluster0.kenusfb.mongodb.net/Cluster0?retryWrites=true&w=majority')
# db = client.code_qna_board

# client = MongoClient('mongodb+srv://test:sparta@cluster0.xfqlj4u.mongodb.net/Cluster0?retryWrites=true&w=majority')
# db = client.code_qna_board

client = MongoClient('3.35.4.171', 27017, username="test", password="test", tlsCAFile=certifi.where())
db = client.code_qna_board


# 메인 페이지
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        QnA_list = list(db.boards.find({}))

        #############
        boards = list(db.boards.find())
        # boards에서 _id를 하나씩 꺼내서, 문자열화 시킴(원래는 object형)
        for board in boards:
            board["_id"] = str(board["_id"])

        # board 역순 정렬
        boards.reverse()

        user_info = db.users.find_one({"username": payload["id"]})
        # user_info = db.users.find_one({'username':ObjectId(id)})
        print(payload)

        return render_template('index.html', QnA_list=QnA_list, boards=boards, user=user_info, token=token_receive)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

        # 페이지 이동
        @app.route('/write', methods=["GET"])
        def to_write():
            boards = list(db.boards.find({}, {'_id': False}))
            return jsonify({'boards': boards})

        return render_template('index.html', QnA_list=QnA_list, boards=boards)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/none')
def none():
    boards = list(db.boards.find())
    for board in boards:
        board["_id"] = str(board["_id"])
    boards.reverse()
    msg = request.args.get("msg")
    return render_template('index.html', boards=boards)


@app.route('/detail/<id>')
def detail_nonepage(id):
    msg = request.args.get("msg")
    detail_board = db.boards.find_one({'_id': ObjectId(id)})

    comments = list(db.comments.find())
    boards = list(db.boards.find())

    # boards에서 _id를 하나씩 꺼내서, 문자열화 시킴(원래는 object형)
    for comment in comments:
        comment["_id"] = str(comment["_id"])

    for board in boards:
        board["_id"] = str(board["_id"])

    comment_id = db.comments.find_one({'_id': ObjectId(id)})
    return render_template('detail.html', id=id, detail_board=detail_board, comments=comments,
                           comment_id=comment_id, boards=boards)


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/register')
def register():
    msg = request.args.get("msg")
    return render_template('register.html', msg=msg)


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 6)  # 로그인 6시간 유지(만료시간)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    usernick_receive = request.form['usernick_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "usernick": usernick_receive,  # 닉네임
        "password": password_hash,  # 비밀번호
        "profile_name": username_receive,  # 프로필 이름 기본값은 아이디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/sign_up/check_dup_nick', methods=['POST'])
def check_dup_nick():
    usernick_receive = request.form['usernick_give']
    exists = bool(db.users.find_one({"usernick": usernick_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# 글쓰기 페이지 ###########################################
# 글쓰기 페이지
@app.route('/write')
def write():
    return render_template('write.html')


# html/CSS 페이지
@app.route('/html_CSS')
def html_CSS():
    QnA_list = list(db.boards.find({}, {'_id': False}))
    boards = list(db.boards.find())
    for board in boards:
        board["_id"] = str(board["_id"])
    boards.reverse()
    return render_template('html_CSS.html', QnA_list=QnA_list, boards=boards)


# Javascript 페이지
@app.route('/Javascript')
def Javascript():
    QnA_list = list(db.boards.find({}, {'_id': False}))
    boards = list(db.boards.find())
    for board in boards:
        board["_id"] = str(board["_id"])
    boards.reverse()
    return render_template('Javascript.html', QnA_list=QnA_list, boards=boards)


# Python 페이지
@app.route('/Python')
def Python():
    QnA_list = list(db.boards.find({}, {'_id': False}))
    boards = list(db.boards.find())
    for board in boards:
        board["_id"] = str(board["_id"])
    boards.reverse()
    return render_template('Python.html', QnA_list=QnA_list, boards=boards)


# 글쓰기 페이지 인풋값
@app.route("/api/write", methods=["POST"])
def write_post():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 포스팅하기
        user_info = db.users.find_one({"username": payload["id"]})
        title_receive = request.form['title_give']
        content_receive = request.form['content_give']
        category_receive = request.form['category_give']
        date_receive = request.form["date_give"]

        # QnA_list = list(db.boards.find({}, {'_id': False}))
        # count = len(QnA_list) + 1

        doc = {
            "title": title_receive,
            "content": content_receive,
            "category": category_receive,
            "usernick": user_info["usernick"],
            "username": user_info["username"]
        }
        db.boards.insert_one(doc)
        return jsonify({"result": "success", 'msg': '작성 완료'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({'result': 'fail', 'msg': '로그인 후 이용해주세요.'})


# 상세페이지 ###########################################
# 상세페이지
@app.route('/detail')
def detail():
    msg = request.args.get("msg")
    return render_template('write.html', msg=msg)


@app.route('/detail/<id>')
def detail_page(id):
    detail_board = db.boards.find_one({'_id': ObjectId(id)})

    comments = list(db.comments.find())
    boards = list(db.boards.find())

    # boards에서 _id를 하나씩 꺼내서, 문자열화 시킴(원래는 object형)
    for comment in comments:
        comment["_id"] = str(comment["_id"])

    for board in boards:
        board["_id"] = str(board["_id"])

    comment_id = db.comments.find_one({'_id': ObjectId(id)})

    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('detail.html', id=id, detail_board=detail_board, comments=comments,
                               comment_id=comment_id, boards=boards, user=user_info)

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({'result': 'fail', 'msg': '오류 발생.'})


# 답변 리스트 보여주기
@app.route("/comment_show", methods=["GET"])
def comment_show():
    comments = list(db.comments.find({}, {'_id': False}))
    return jsonify({'comments': comments})


# 게시글 보여주기
@app.route("/board_show", methods=["GET"])
def board_show():
    boards = list(db.boards.find({}, {'_id': False}))
    return jsonify({'boards': boards})


# 답변 작성
@app.route('/comment_post', methods=['POST'])
def comment_post():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 포스팅하기
        user_info = db.users.find_one({"username": payload["id"]})
        comment_receive = request.form["comment_give"]
        board_id_receive = request.form["board_id_give"]
        date_receive = request.form["date_give"]
        doc = {
            "username": user_info["username"],
            "usernick": user_info["usernick"],
            "comment": comment_receive,
            "board_id": board_id_receive,
            "date": date_receive
        }
        db.comments.insert_one(doc)
        return jsonify({"result": "success", 'msg': '답변이 등록되었습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({'result': 'fail', 'msg': '로그인 후 이용해주세요.'})


#  삭제 기능
@app.route("/delete_board", methods=["POST"])
def board_delete():
    # return jsonify({'msg': '삭제 되었습니다!'})
    # return render_template('index.html')
    ###############
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})

        # 현재 로그인 유저의 username(아이디)불러오기
        username = user_info["username"]
        board_id_receive = request.form['board_id_give']

        # 게시판 db지우기
        db.boards.delete_one({'_id': ObjectId(board_id_receive), 'username': username})
        # board_username = db.boards.find_one({'_id': f'ObjectId({board_id_receive})'})['username']

        # 답변목록db도 지우기
        comments = list(db.comments.find())
        for c in comments:
            db.comments.delete_one({'board_id': board_id_receive, 'username': username})

        return jsonify({"result": "success", "username": username})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({'result': 'fail', 'msg': '삭제 권한이 없습니다.'})


# # 숨김처리 기능
# @app.route("/get_posts", methods=['GET'])
# def get_posts():
#     token_receive = request.cookies.get('mytoken')
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         username_receive = request.args.get("username_give")
#         user_info = db.users.find_one({"username": payload["id"]})
#         username = user_info['username']
#         if username_receive == username:
#             return jsonify({"result": "success"})
#
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for("home"))

# 추천 기능
@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 좋아요 수 변경
        user = db.users.find_one({"username": payload["id"]})
        comment_id_receive = request.form["comment_id_give"]
        action_receive = request.form["action_give"]
        doc = {
            "comment_id": comment_id_receive,
            "username": user["username"]
        }
        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        count = db.likes.count_documents({"post_id": comment_id_receive})
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({'result': 'fail', 'msg': '로그인 후 이용해주세요.'})
        # return redirect(url_for("home"))


# @app.route("/get_time", methods=['GET'])
# def get_time():
#     # token_receive = request.cookies.get('mytoken')
#     # payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#     boards = list(db.boards.find({}).sort("date", -1).limit(20))
#
#     return jsonify ({'boards':boards})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
