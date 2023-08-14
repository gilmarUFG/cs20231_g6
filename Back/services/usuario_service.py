from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.models import UsuarioModel, UsuarioLoginModel
from model.schemas import Usuario, UsuarioLogin, UsuarioAlterarSenha
from passlib.context import CryptContext
from fastapi.exceptions import HTTPException
from fastapi import status
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from datetime import datetime, timedelta
from decouple import config
from email_validator import EmailNotValidError, validate_email

SECRET_KEY = config('SECRET_KEY')
ALGORITHM = config('ALGORITHM')

crypt_context = CryptContext(schemes=['sha256_crypt'])


class UsuarioLoginService:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def registrar_usuario_login(self, usuario: UsuarioLogin):
        email_valido = self.validar_email(usuario.email)

        if not email_valido:
            raise HTTPException(
                detail='Endereço de email invalido',
                status_code=status.HTTP_406_NOT_ACCEPTABLE
            )
        
        usuario_login_model = UsuarioLoginModel(
            username=usuario.username,
            senha=crypt_context.hash(usuario.senha),
            email=usuario.email
        )

        username_ja_cadastrado = self.db_session.query(UsuarioLoginModel).filter_by(username=usuario.username).first()
        email_ja_cadastrado = self.db_session.query(UsuarioLoginModel).filter_by(email=usuario.email).first()

        if username_ja_cadastrado is not None or email_ja_cadastrado is not None:
            raise HTTPException(
                detail="Username ou Email já cadastrados para outro LOGIN!",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        try:
            self.db_session.add(usuario_login_model)
            self.db_session.commit()
            return usuario_login_model.id_login
        except IntegrityError:
            raise HTTPException(
                detail="Erro ao inserir login do usuario",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    def validar_email(self, email:str):
        try:
            validate_email(email, check_deliverability=False)
            return True

        except EmailNotValidError as e:
            return False

    def registrar_usuario(self, usuario: Usuario, id_credencial: int):
        usuario_model = UsuarioModel(
            id_credencial=id_credencial,
            apelido=usuario.apelido,
            nome_completo=usuario.nome_completo,
            data_nasc=usuario.data_nasc,
            avatar=usuario.avatar,
        )

        try:
            self.db_session.add(usuario_model)
            self.db_session.commit()
            return usuario_model.id_usuario
        except IntegrityError:
            raise HTTPException(
                detail="Erro ao inserir dados do usuario",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    def listar_usuarios_login(self):
        try:
            usuario_lista = self.db_session.query(UsuarioLoginModel).all()
            user_dict = []

            for u in usuario_lista:
                infos_json = {
                    'id_login': u.id_login,
                    'email': u.email
                }
                user_dict.append(infos_json)

            return user_dict
        except:
            raise HTTPException(
                detail="Erro ao buscar usuarios",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    def login_usuario(self, usuario: UsuarioLogin, expires_in: int = 60):
        usuario_back = self.db_session.query(UsuarioLoginModel).filter_by(username=usuario.username).first()

        if usuario_back is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Usuário ou senha incorretos.'
            )

        if not crypt_context.verify(usuario.senha, usuario_back.senha):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Usuário ou senha incorretos.'
            )

        exp = datetime.utcnow() + timedelta(minutes=expires_in)

        payload = {
            'sub': usuario_back.username,
            'exp': exp,
        }

        access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        id_usuario = self.obtem_id_usuario_login(usuario_back.id_login)

        return {
            'access_token': access_token,
            'exp': exp.isoformat(),
            'id_login': usuario_back.id_login,
            'id_usuario': id_usuario
        }

    def obtem_id_usuario_login(self, id_login):
        usuario_back = self.db_session.query(UsuarioModel).filter_by(id_credencial=id_login).first()

        if usuario_back is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='O usuário não foi cadastrado!'
            )

        return usuario_back.id_usuario

    def logout_usuario(self, token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            payload = None

        if payload:
            payload['exp'] = datetime.utcnow()
            return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        else:
            return JSONResponse(
                content={"message": "Token inválido ou expirado"},
                status_code=status.HTTP_400_BAD_REQUEST
            )

    def verify_token(self, access_token):
        try:
            data = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token de acesso invalido.'
            )

        usuario_back = self.db_session.query(UsuarioLoginModel).filter_by(username=data['sub']).first()

        if usuario_back is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token de acesso invalido.'
            )

    def verifica_existencia_usuario(self, id_usuario: int):
        usuario = self.db_session.query(UsuarioModel).filter_by(id_usuario=id_usuario).first()
        if not usuario:
            return False, JSONResponse(
                content={'error': 'Usuário não encontrado'},
                status_code=status.HTTP_404_NOT_FOUND
            )

        return True, None

    def obtem_id_credencial(self, id_usuario: int):
        usuario_back = self.db_session.query(UsuarioModel).filter_by(id_usuario=id_usuario).first()
        return usuario_back.id_credencial

    def valida_senha_email(self, id_usuario: int, usuario_alterar_senha: UsuarioAlterarSenha):
        id_credencial = self.obtem_id_credencial(id_usuario=id_usuario)
        login_back = self.db_session.query(UsuarioLoginModel).filter_by(id_login=id_credencial).first()

        if not crypt_context.verify(usuario_alterar_senha.senha_atual, login_back.senha) or usuario_alterar_senha.email != login_back.email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Email ou senha incorretos.'
            )

        login_back.senha = crypt_context.hash(usuario_alterar_senha.nova_senha)
        self.db_session.commit()
        self.db_session.refresh(login_back)
        return login_back

    def obtem_id_usuario(self, email):
        login_back = self.db_session.query(UsuarioLoginModel).filter_by(email=email).first()

        if login_back is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Email do usuário não encontrado!'
            )

        usuario_back = self.db_session.query(UsuarioModel).filter_by(id_credencial=login_back.id_login).first()
        return usuario_back.id_usuario