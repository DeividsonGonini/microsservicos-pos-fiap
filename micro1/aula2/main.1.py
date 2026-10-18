from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

# Invoca o construtor do FastAPI
app = FastAPI()

# Herda a classe do BaseModel
class Produto(BaseModel):
    em_estoque: int
    reservado: int = 0

class OperacaoEstoque(BaseModel):
    sku: str
    quantidade: int

class OperacoesEstoque(BaseModel):
    operacoes: List[OperacaoEstoque]

# Simulação banco de dados em memória
#Criando um dicionário
estoque = {
    "123": Produto(em_estoque=10),
    "456": Produto(em_estoque=5),
    "789": Produto(em_estoque=2)
}

# Expondo endpoint Get com uma função Python
@app.get("/estoque/{sku}")
# função assincrona que recebe um SKU do tipo String
async def obter_estoque(sku: str):
    produto = estoque.get(sku)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto

@app.post("/estoque/reserva")
# Caso tivessem Path Parameters, eles entrariam em ordem nos parametros da função, o ultimo parametro seria o Body
async def reservar_estoque(operacoes: OperacoesEstoque):
    # no for o primeiro elemento(operações) vem da entrada do método / o Segundo elemento(operações) vem da estrutura do OperacoesEstoque (linha 18)
    for operacao in operacoes.operacoes:
        # o produto é igual ao estoque, o SKU de busca vem da OperaçãoEstoque
        produto = estoque.get(operacao.sku)
        if not produto:
            raise HTTPException(status_code=404, detail=f"Produto com SKU {operacao.sku} não encontrado")
        if operacao.quantidade > produto.em_estoque:
            raise HTTPException(status_code=400, detail=f"Estoque insuficiente para reserva do SKU {operacao.sku}")
        produto.em_estoque -= operacao.quantidade
        produto.reservado += operacao.quantidade
        # Por padrão o FastAPI devolve 200 OK
    return operacoes

@app.post("/estoque/debito")
async def debitar_estoque(operacoes: OperacoesEstoque):
    for operacao in operacoes.operacoes:
        produto = estoque.get(operacao.sku)
        if not produto:
            raise HTTPException(status_code=404, detail=f"Produto com SKU {operacao.sku} não encontrado")
            # Caso o debito seja maior que a quantidade reservada retorna erro (regra de negócios)
        if operacao.quantidade > produto.reservado:
            raise HTTPException(status_code=400, detail=f"Estoque reservado insuficiente para debitar do SKU {operacao.sku}")
        produto.reservado -= operacao.quantidade
    return operacoes
