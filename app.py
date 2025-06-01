from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask_sqlalchemy import SQLAlchemy
from flask_simplelogin import SimpleLogin
from flask_simplelogin import login_required
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///padaria.db"
app.config["SECRET_KEY"] = "MinhaChave11:11"
app.config["SIMPLELOGIN_USERNAME"] = "joe"
app.config["SIMPLELOGIN_PASSWORD"] = "1105"
db=SQLAlchemy()
db.init_app(app)
SimpleLogin(app)

class Product (db.Model):
    __tablename__ = 'produto'
    id = db.Column (db.Integer, primary_key=True)
    nome = db.Column (db.String(100), nullable=False)
    descricao = db.Column(db.String(100))
    ingredientes = db.Column(db.String(500))
    origem = db.Column(db.String(100))
    imagem = db.Column(db.String(100))

    def __init__(self, nome:str,
                 descricao: str,
                 ingredientes: str,
                 origem: str,
                 imagem: str) -> None:
        self.nome = nome
        self.descricao = descricao
        self.ingredientes = ingredientes
        self.origem = origem
        self.imagem = imagem

@app.route("/")
@login_required
def home():
    return render_template("index.html")

@app.route("/catalogo_produtos", methods=["GET","POST"])
@login_required
def lista_prod():
    if request.method == "POST":
        termo = request.form["pesquisa"]
        resultado = db.session.execute(db.select(Product).filter(Product.nome.like(f'%{termo}%'))).scalars()
        return render_template('produtos.html', cad_prod=resultado)
    else:
        produtos = db.session.execute(db.select(Product)).scalars()
        return render_template('produtos.html', cad_prod=produtos)

@app.route("/cadadstro_produtos", methods=["GET", "POST"])
@login_required
def cadastra_prod():
    if request.method == "POST":
        status = {"type": "sucesso", "message": "Produto cadastrado com sucesso!"}
        dados_form = request.form
        imagem = request.files['imagem']
        try:
            produto_form = Product(dados_form['nome'], dados_form['descricao'], dados_form['ingredientes'], dados_form['origem'], imagem.filename)
            imagem.save(os.path.join('static/imagens', imagem.filename)) 
            db.session.add(produto_form)
            db.session.commit()
        except:
            status = {"type": "erro", "message": f"Ocorreram inconsistências ao cadastar o produto {dados_form['nome']} !"}
        return render_template("cadastro_prod.html", status=status)
    else:
        return render_template("cadastro_prod.html")
    
@app.route("/editar_produtos/<int:id>", methods=["GET", "POST"])
@login_required
def editar_prod(id):
    if request.method == "POST":
        dados_editados = request.form
        imagem = request.files['imagem']
        produto = db.session.execute(db.select(Product).filter(Product.id == id)).scalar()

        produto.nome = dados_editados['nome']
        produto.descricao = dados_editados['descricao']
        produto.ingredientes = dados_editados['ingredientes']
        produto.origem = dados_editados['origem']

        if imagem.filename:
            produto.imagem = imagem.filename

        db.session.commit()
        return redirect ("/catalogo_produtos")
    else:
        produto_editado=db.session.execute(db.select(Product).filter(Product.id == id)).scalar()
        return render_template("editar.html", produto=produto_editado)
    
@app.route("/deletar_produto/<int:id>")
@login_required
def deletar_produto(id):
    produto_deletado=db.session.execute(db.select(Product).filter(Product.id == id)).scalar()
    db.session.delete(produto_deletado)
    db.session.commit()
    return redirect("/catalogo_produtos")

@app.route("/fale_conosco")
def contato():
    return render_template('contato.html')

if __name__ == '__main__':
    with app.app_context(): 
        db.create_all() #Sempre antes do app.run(debug=True)
        app.run()        