from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
# Biblioteca para chamadas Http
from requests import get

app = FastAPI()

class Produto(BaseModel):
    sku: str
    nome: str
    descr: str
    urlImagem: str
    qtd:  Optional[int] = None
    preco: Optional[float] = None

@app.get("/produto/{sku}")
async def obter_produto(sku: str):
    # Integração com serviço catalogo
    catalogo = get(f"http://catalogo:8080/produto/{sku}").json()
    #detail só aparece quando tem uma exceção do lado da API, é padrão do FastAPI / igual ao detail do raise HTTPException() abaixo
    if catalogo.get("detail") is not None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    produto = {
        "sku": sku,
        "nome": catalogo["nome"],
        "descr": catalogo["descr"],
        "urlImagem": catalogo["urlImagem"],
        "qtd": None,
        "preco": None
    }

    # Integração com serviço Precificação para popular o preço
    preco = get(f"http://precificacao:8080/preco/{sku}").json()
    # Verifica se o atributo preco é vazio
    if preco.get("preco") is not None:
        produto["preco"] = preco["preco"]

    # Integração com serviço Estoque para popular a quantidade
    estoque = get(f"http://estoque:8080/estoque/{sku}").json()
    # Verifica se o atributo em_estoque é vazio
    if estoque.get("em_estoque") is not None:
        produto["qtd"] = estoque["em_estoque"]

    return Produto(**produto)
