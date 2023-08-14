from fastapi.responses import JSONResponse
from fastapi import status
from sqlalchemy.orm import Session

from database.models import ComentarioModel, EtapaModel, ProjetoModel, TarefaModel, UsuarioModel
from model.schemas import Tarefa


class TarefaService:
    def __init__(self, db_session:Session):
        self.db_session = db_session

    
    def listar_tarefas(self, projeto_id: int, etapa_id: int):
        # Lógica para listar as tarefas de uma etapa específica de um projeto
        projeto = self.db_session.query(ProjetoModel).filter_by(id_projeto=projeto_id).first()

        if not projeto:
            return None, JSONResponse(
                content={'error': 'Projeto não encontrado'},
                status_code=status.HTTP_404_NOT_FOUND
            )

        etapa = self.db_session.query(EtapaModel).filter_by(id_etapa = etapa_id).first()

        if not etapa:
            return None, JSONResponse(
                content={'error': 'Etapa não encontrada'},
                status_code=status.HTTP_404_NOT_FOUND
            )

        tarefas = self.db_session.query(TarefaModel).filter_by(id_etapa = etapa_id).all()

        tarefas_dict = []
        for tarefa in tarefas:
            tarefa_dict = {
                'id': tarefa.id_tarefa,
                'descricao': tarefa.descricao,
            }
            tarefas_dict.append(tarefa_dict)
        
        return JSONResponse(
            content=tarefas_dict,
            status_code=status.HTTP_200_OK
        ), None
    
    def adicionar_tarefa(self, projeto_id: int, etapa_id: int, tarefa: Tarefa):
        projeto = self.db_session.query(ProjetoModel).filter_by(id_projeto=projeto_id).first()
        
        if not projeto:
            return None, JSONResponse(
                content={'error': 'Projeto não encontrado'},
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        etapa = self.db_session.query(EtapaModel).filter_by(id_etapa = etapa_id).first()

        if not etapa:
            return None, JSONResponse(
                content={'error': 'Etapa não encontrada'},
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        nova_tarefa = TarefaModel(
            id_criador = tarefa.id_criador,
            id_responsavel = tarefa.id_responsavel,
            id_etapa = etapa_id,
            descricao = tarefa.descricao
        )

        self.db_session.add(nova_tarefa)
        self.db_session.commit()

        return JSONResponse(
            content={'msg': f"Nova tarefa adicionada à etapa {etapa_id}"},
            status_code=status.HTTP_201_CREATED
        ), None
    
    def editar_tarefa_descricao(self, tarefa_id:int, descricao:str):
        tarefa = self.db_session.query(TarefaModel).filter_by(id_tarefa=tarefa_id).first()

        if not tarefa:
            return None, JSONResponse(
                content={'error': 'Tarefa não encontrada'},
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        tarefa.descricao = descricao
        self.db_session.commit()
        
        return JSONResponse(
            content={'msg': "A descricao da tarefa foi modificada com sucesso"},
            status_code=status.HTTP_200_OK
        ), None

    def editar_tarefa_responsavel(self, tarefa_id:int, id_responsavel:int):
        tarefa = self.db_session.query(TarefaModel).filter_by(id_tarefa=tarefa_id).first()

        if not tarefa:
            return None, JSONResponse(
                content={'error': 'Tarefa não encontrada'},
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        responsavel = self.db_session.query(UsuarioModel).filter_by(id_usuario=id_responsavel).first()

        if not responsavel:
            return None, JSONResponse(
                content={'error': 'Usuário não encontrado'},
                status_code=status.HTTP_404_NOT_FOUND
            )

        tarefa.id_responsavel = id_responsavel
        self.db_session.commit()
        
        return JSONResponse(
            content={'msg': "O usuário responsavel pela tarefa foi alterado."},
            status_code=status.HTTP_200_OK
        ), None

    def excluir_tarefa(self, tarefa_id:int):
        tarefa = self.db_session.query(TarefaModel).filter_by(id_tarefa=tarefa_id).first()

        if not tarefa:
            return None, JSONResponse(
                content={'error': 'Tarefa não encontrada'},
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        comentarios = self.db_session.query(ComentarioModel).filter_by(id_tarefa = tarefa_id).all()

        for comentario in comentarios:
            try:
                self.db_session.delete(comentario)
            except(Exception):
                self.db_session.rollback()
                return None, JSONResponse(
                    content={'error': 'Erro ao excluir tarefa'},
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
        
        self.db_session.delete(tarefa)
        self.db_session.commit()

        return JSONResponse(
            content={'msg': "A tarefa foi excluída com sucesso."},
            status_code=status.HTTP_200_OK
        ), None

    def mudar_etapa(self, tarefa_id:int, nova_etapa_id:int):
        tarefa = self.db_session.query(TarefaModel).filter_by(id_tarefa=tarefa_id).first()

        if not tarefa:
            return None, JSONResponse(
                content={'error': 'Tarefa não encontrada'},
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        tarefa.id_etapa = nova_etapa_id
        self.db_session.commit()

        return JSONResponse(
            content={'msg': "A tarefa trocou de etapa com sucesso."},
            status_code=status.HTTP_200_OK
        ), None