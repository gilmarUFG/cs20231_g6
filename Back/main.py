from fastapi import FastAPI
from controller.routes import usuario_router, projeto_router, tarefas_router, comentario_router, etapa_router, test_router

app = FastAPI(
    title="Construção de Software: Rotas backend NoteSync",
    description="Esta é a documentação de todas as rotas do backend do nosso projeto de API Rest",
    version="1.0.0"
)

@app.get("/")
def home():
    return "Salve"

app.include_router(router=usuario_router)
app.include_router(router=projeto_router) 
app.include_router(router=etapa_router)
app.include_router(router=tarefas_router)
app.include_router(router=comentario_router)

app.include_router(router=test_router)