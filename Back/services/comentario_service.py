from fastapi.responses import JSONResponse
from fastapi import status
from sqlalchemy.orm import Session

from database.models import ComentarioModel, EtapaModel, ProjetoModel, TarefaModel
from model.schemas import Comentario

class ComentarioService:
    def __init__(self, db_session:Session):
        self.db_session = db_session

     #COMENTARIOS  
    def listar_comentarios(self, projeto_id: int, etapa_id: int, tarefa_id: int):
        # Lógica para listar os comentários de uma tarefa específica
        projeto = self.db_session.query(ProjetoModel).filter_by(id_projeto = projeto_id).first()

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

        tarefa = self.db_session.query(TarefaModel).filter_by(id_tarefa = tarefa_id).first()

        if not tarefa:
            return None, JSONResponse(
                content={'error': 'Tarefa não encontrada'},
                status_code=status.HTTP_404_NOT_FOUND
            )

        comentarios = self.db_session.query(ComentarioModel).filter_by(id_tarefa = tarefa_id).all()

        comentarios_dict = []
        for comentario in comentarios:
            comentario_dict = {
                'id': comentario.id_comentario,
                'descricao': comentario.descricao
            }
            comentarios_dict.append(comentario_dict)
        
        return comentarios_dict, None
    
    def adicionar_comentario(self, tarefa_id: int, comentario: Comentario):
        # Lógica para adicionar um comentário a uma tarefa específica
        tarefa = self.db_session.query(TarefaModel).filter_by(id_tarefa=tarefa_id).first()

        if not tarefa:
            return None, JSONResponse(
                content={'error': 'Tarefa não encontrada'},
                status_code=status.HTTP_404_NOT_FOUND
            )

        novo_comentario = ComentarioModel(
            id_criador = comentario.id_criador,
            id_tarefa = tarefa_id,
            descricao = comentario.descricao
        )

        self.db_session.add(novo_comentario)
        self.db_session.commit()

        return JSONResponse(
            content={'msg': f"Comentário adicionado à tarefa {tarefa_id}"},
            status_code=status.HTTP_201_CREATED
        ), None
    
    def editar_comentario(self, comentario_id: int, comentario: str):
        # Lógica para modificar um comentário em uma tarefa específica
        comentario_modificado = self.db_session.query(ComentarioModel).filter_by(id_comentario=comentario_id).first()

        if not comentario_modificado:
            return None, JSONResponse(
                content={'error': 'Comentário não encontrado'},
                status_code=status.HTTP_404_NOT_FOUND
            )

        comentario_modificado.descricao = comentario
        self.db_session.commit()

        return JSONResponse(
            content={'msg': "Comentário modificado com sucesso."},
            status_code=status.HTTP_200_OK
        ), None
    
    def excluir_comentario(self, comentario_id: int):
        # Lógica para remover um comentário de uma tarefa específica
        
        comentario_removido = self.db_session.query(ComentarioModel).filter_by(id_comentario = comentario_id).first()

        if not comentario_removido:
            return None, JSONResponse(
                content={'error': 'Comentário não encontrado'},
                status_code=status.HTTP_404_NOT_FOUND
            )

        self.db_session.delete(comentario_removido)
        self.db_session.commit()

        return JSONResponse(
            content={'msg': "Comentário removido com sucesso."},
            status_code=status.HTTP_200_OK
        ), None
    
    
