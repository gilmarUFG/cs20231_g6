import traceback

from sqlalchemy.orm import Session
from model.schemas import Etapa
from database.models import ProjetoModel, EtapaModel



class EtapaService:
    def __init__(self, db_session:Session):
        self.db_session = db_session
    
    def listar_etapas(self, projeto_id:int):
        # Lógica para listar as etapas de um projeto específico
        projeto = self.db_session.query(ProjetoModel).filter_by(id_projeto = projeto_id).first()

        if not projeto:
            return None

        etapas = self.db_session.query(EtapaModel).filter_by(id_projeto = projeto_id).all()

        etapas_dict = []
        for etapa in etapas:
            etapa_dict = {
                'id_etapa': etapa.id_etapa,
                'nome': etapa.nome
            }
            etapas_dict.append(etapa_dict)
        
        return etapas_dict
    
    def criar_etapa(self, projeto_id: int, etapa: Etapa):
        projeto = self.db_session.query(ProjetoModel).filter_by(id_projeto = projeto_id).first()
        
        if not projeto:
            raise ProjetoNaoEncontradoException(f"Projeto com id='{projeto_id}' não encontrado")
        
        etapa_model = EtapaModel(
            id_projeto = projeto_id,
            nome = etapa.titulo
        )
        
        try:
            self.db_session.add(etapa_model)
            self.db_session.flush()
            self.db_session.commit()
            return etapa_model.id_etapa
        except Exception:
            traceback.print_exc()
            self.db_session.rollback()
            raise ErroAoInserirEtapaException(f"Não foi possível inserir a etapa '{etapa.titulo}' no projeto '{projeto_id}'")

    def recupera_etapa(self, etapa_id: int):
        etapa = self.db_session.query(EtapaModel).filter_by(id_etapa = etapa_id).first()
        if not etapa:
            raise EtapaNaoEncontradaException(f"Etapa com id='{etapa_id}' não encontrada")
        
        return etapa
    

    def editar_etapa(self, etapa_id: int, etapa_alteracao: Etapa):
        try:
            etapa = self.recupera_etapa(etapa_id=etapa_id)
        except EtapaNaoEncontradaException as excecao:
            raise excecao
        
        etapa.nome = etapa_alteracao.titulo
        
        try:
            self.db_session.commit()
        except Exception:
            traceback.print_exc()
            self.db_session.rollback()
            raise ErroAoInserirEtapaException(f"Não foi possível editar a etapa '{etapa.titulo}'")
        

    def deletar_etapa(self, etapa_id: int):
        try:
            etapa = self.recupera_etapa(etapa_id=etapa_id)
        except EtapaNaoEncontradaException as excecao:
            raise excecao
        
        try:
            self.db_session.delete(etapa)
            self.db_session.commit()
        except Exception:
            traceback.print_exc()
            self.db_session.rollback()
            raise ErroAoInserirEtapaException(f"Falha em tentar deletar a etapa '{etapa_id}'")

class EtapaNaoEncontradaException(Exception):
    def __init__ (self, mensagem):
        self.mensagem = mensagem
        
    def getMensagem(self):
        return self.mensagem    

class ErroAoInserirEtapaException(Exception):
    def __init__ (self, mensagem):
        self.mensagem = mensagem
        
    def getMensagem(self):
        return self.mensagem
    
class ProjetoNaoEncontradoException(Exception):
    def __init__ (self, mensagem):
        self.mensagem = mensagem
        
    def getMensagem(self):
        return self.mensagem