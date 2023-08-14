from pydantic import BaseModel, validator, EmailStr, Field
import datetime


class Login(BaseModel):
    username: str
    senha: str


class Logout(BaseModel):
    token: str


class Usuario(BaseModel):
    apelido: str
    nome_completo: str
    data_nasc: datetime.date
    avatar: str


class UsuarioLogin(BaseModel):
    username: str
    senha: str
    email: str = Field(None)


class UsuarioAlterarSenha(BaseModel):
    username: str
    senha_atual: str
    nova_senha: str
    email: EmailStr = Field(None)


class Projeto(BaseModel):
    nome: str
    descricao: str


class ProjetoParticipantes(BaseModel):
    id_projeto: int
    id_participante: int


class BodyAdicionarParticipante(BaseModel):
    email_novo_participante: str


class Comentario(BaseModel):
    id_criador: int
    descricao: str


class Tarefa(BaseModel):
    id_criador: int
    id_responsavel: int
    descricao: str


class Etapa(BaseModel):
    titulo: str
