from database.connection import SessaoBD
from fastapi.security import OAuth2PasswordBearer
from services.usuario_service import UsuarioLoginService
from sqlalchemy.orm import Session
from fastapi import Depends


oauth_scheme = OAuth2PasswordBearer(tokenUrl='usuario/login')

def get_db_session():
    try:
        session = SessaoBD()
        yield session
    finally:
        session.close()
        
def token_verifier(db_session: Session = Depends(get_db_session), token = Depends(oauth_scheme)):
    uc = UsuarioLoginService(db_session=db_session)
    uc.verify_token(access_token=token)
