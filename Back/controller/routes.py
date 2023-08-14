import traceback

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database.depends import get_db_session, token_verifier
from services.comentario_service import ComentarioService

from services.projeto_service import ProjetoService
from services.etapa_service import EtapaService, ProjetoNaoEncontradoException, ErroAoInserirEtapaException, EtapaNaoEncontradaException
from services.tarefa_service import TarefaService
from services.usuario_service import UsuarioLoginService
from model.schemas import Login, Logout, Usuario, UsuarioLogin, Projeto, Etapa, Tarefa, Comentario, UsuarioAlterarSenha, BodyAdicionarParticipante
from database.models import UsuarioModel, ProjetoModel, ViewInfosParticipantesProjetoModel

db_session: Session = Depends(get_db_session)

usuario_router = APIRouter(prefix='/usuario', tags=['Usuario'])
test_router = APIRouter(prefix='/teste', dependencies=[Depends(token_verifier)], tags=['Teste Rota Segura'])
projeto_router = APIRouter(prefix='/projeto', tags=['Projeto'], dependencies=[Depends(token_verifier)])
etapa_router = APIRouter(prefix='/etapa', tags=['Etapa'], dependencies=[Depends(token_verifier)])
tarefas_router = APIRouter(prefix='/tarefas', tags=['Tarefa'], dependencies=[Depends(token_verifier)])
comentario_router = APIRouter(prefix='/comentario', tags=['Comentario'], dependencies=[Depends(token_verifier)])


# -------- ROTAS PARA USUÁRIO -------- #

@usuario_router.post('/cadastrar-login', summary="Cadastro de credenciais: login, senha, email")
def registrar_login(usuario_login: UsuarioLogin, db_session: Session = Depends(get_db_session)):
    uc = UsuarioLoginService(db_session=db_session)
    id_usuario_login = uc.registrar_usuario_login(usuario=usuario_login)

    return JSONResponse(
        content={
            'msg': "Usuário registrado com sucesso!",
            'id_login': id_usuario_login
        },
        status_code=status.HTTP_201_CREATED
    )

@usuario_router.post('/{id_login}/cadastrar-usuario', summary="Cadastro de informaçoes do usuario: nome, apelido, data nascimento")
def registrar_usuario(id_login: int, usuario: Usuario, db_session: Session = Depends(get_db_session)):
    uc = UsuarioLoginService(db_session=db_session)
    id_usuario = uc.registrar_usuario(usuario=usuario, id_credencial=id_login)

    return JSONResponse(
        content={
            'msg': "Informacoes do usuario registrado com sucesso.",
            'id_usuario': id_usuario
        },
        status_code=status.HTTP_200_OK
    )

@usuario_router.get('/listar', summary="Listar todos os usuários cadastrados no banco")
def listar_usuarios(db_session: Session = Depends(get_db_session)):
    uc = UsuarioLoginService(db_session=db_session)
    user_dict = uc.listar_usuarios_login()

    return JSONResponse(
        content=user_dict,
        status_code=status.HTTP_200_OK
    )

@usuario_router.post('/login', summary='Rota para o usuario realizar login')
def login_usuario(request_form_usuario: Login, db_session: Session = Depends(get_db_session)):
    uc = UsuarioLoginService(db_session=db_session)
    usuario = UsuarioLogin(
        username=request_form_usuario.username,
        senha=request_form_usuario.senha
    )
    auth_data = uc.login_usuario(usuario=usuario)
    return JSONResponse(
        content=auth_data,
        status_code=status.HTTP_200_OK
    )

@usuario_router.post('/logout', summary='Rota para o usuario realizar logout')
def logout_usuario(token: Logout, db_session: Session = Depends(get_db_session)):
    uc = UsuarioLoginService(db_session=db_session)
    new_token = uc.logout_usuario(token.token)
    return JSONResponse(
        content={"message": "Logout realizado com sucesso", "new_token": new_token},
        status_code=status.HTTP_200_OK
    )

@usuario_router.post('/{id_usuario}/alterar-senha', summary="Alterar senha validando: senha atual, username e login")
def alterar_senha_usuario(id_usuario: int, usuario_alterar_senha: UsuarioAlterarSenha, db_session: Session = Depends(get_db_session)):
    uc = UsuarioLoginService(db_session=db_session)
    usuario_atualizado = uc.valida_senha_email(id_usuario=id_usuario, usuario_alterar_senha=usuario_alterar_senha)

    return JSONResponse(
        content=f'Senha do usuario {usuario_atualizado.username} foi atualizada!',
        status_code=status.HTTP_200_OK
    )


# -------- ROTAS PARA TESTE LOGIN -------- #

@test_router.get('/check')
def teste_login():
    return "Logado"


# -------- ROTAS PARA PROJETO -------- #

@projeto_router.get('/{id_usuario}/listar', summary="Listar projetos que o usuário participa")
def listar_projetos(id_usuario: int, db_session: Session = Depends(get_db_session)):
    us = UsuarioLoginService(db_session=db_session)
    usuario_existe, resposta = us.verifica_existencia_usuario(id_usuario=id_usuario)
    if not usuario_existe:
        return resposta

    ps=ProjetoService(db_session=db_session)
    infos_projetos = ps.listar_projetos_usuario(id_usuario=id_usuario)

    return JSONResponse(
        content=infos_projetos,
        status_code=status.HTTP_200_OK
    )

@projeto_router.get('/{id_usuario}/listar-criados', summary="Listar os projetos que o usuário criou")
def listar_projetos_criados(id_usuario: int, db_session: Session = Depends(get_db_session)):
    us = UsuarioLoginService(db_session=db_session)
    usuario_existe, resposta = us.verifica_existencia_usuario(id_usuario=id_usuario)
    if not usuario_existe:
        return resposta

    ps = ProjetoService(db_session=db_session)
    infos_projetos = ps.listar_projetos_criados_usuario(id_usuario=id_usuario)

    return JSONResponse(
        content=infos_projetos,
        status_code=status.HTTP_200_OK
    )

@projeto_router.post('/{id_usuario}/criar', summary="Criar um projeto para um usuário passando seu ID")
def criar_projeto(id_usuario: int, projeto: Projeto, db_session: Session = Depends(get_db_session)):
    us = UsuarioLoginService(db_session=db_session)
    usuario_existe, resposta = us.verifica_existencia_usuario(id_usuario=id_usuario)
    
    if not usuario_existe:
        return resposta

    ps = ProjetoService(db_session=db_session)
    sucesso, falha = ps.criar_relacionar_novo_projeto(id_usuario=id_usuario, projeto=projeto)

    if sucesso is None:
        return falha
    
    else:
        return sucesso

@projeto_router.put('/{id_projeto}/editar', summary="Editar projeto")
def editar_projeto(projeto_id: int, projeto: Projeto, db_session: Session = Depends(get_db_session)):
    ps = ProjetoService(db_session=db_session)
    try:
        ps.editar_projeto(id_projeto=projeto_id, projeto_alteracao=projeto)
    
        return JSONResponse(
            content={
                'msg': "Projeto alterado com sucesso"
            },
            status_code=status.HTTP_200_OK
        )
    except ProjetoNaoEncontradoException as e:
        return JSONResponse(
            content={
                'msg': f"{e.getMensagem()}"
            },
            status_code=status.HTTP_404_NOT_FOUND
        )
    except ErroAoInserirEtapaException as e:
        return JSONResponse(
            content={
                'msg': f"{e.getMensagem()}"
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@projeto_router.delete('/{projeto_id}', summary="Excluir um projeto")
def excluir_projeto(projeto_id: int, db_session: Session = Depends(get_db_session)):
    ps = ProjetoService(db_session=db_session)
    ps.deletar_projeto(id_projeto=projeto_id)

    return JSONResponse(
        content='Projeto excluído com sucesso!',
        status_code=status.HTTP_200_OK
    )

@projeto_router.get('/{projeto_id}', summary="Traz todas as etapas, tarefas e comentarios associados a um projeto")
def listar_projeto_completo(projeto_id: int, db_session: Session = Depends(get_db_session)):
    ps = ProjetoService(db_session=db_session)
    sucesso, falha = ps.listar_projeto_completo(id_projeto=projeto_id)

    if sucesso is None:
        return falha
    
    else:
        return JSONResponse(
            content=sucesso,
            status_code=status.HTTP_200_OK
        )

@projeto_router.post('/{projeto_id}/adicionar-participante', summary="Adiciona um participante no projeto pelo seu email")
def adicionar_participante(bodyAdicionarParticipante: BodyAdicionarParticipante, projeto_id: int, db_session: Session = Depends(get_db_session)):
    ps = ProjetoService(db_session=db_session)
    ps.add_participante(id_projeto=projeto_id, email=bodyAdicionarParticipante.email_novo_participante)

    return JSONResponse(
        content=f'Participante com email {bodyAdicionarParticipante.email_novo_participante} adicionado com sucesso!',
        status_code=status.HTTP_200_OK
    )

# -------- ROTAS PARA ETAPAS -------- #

# Endpoint para pegar no front-end os dados das etapas de um projeto específico para fornecer aos cards de projetos na página inicial
@etapa_router.get('/{projeto_id}/etapa', summary="Listar as etapas de um projeto")
def listar_etapas(projeto_id: int, db_session: Session = Depends(get_db_session)):
    es = EtapaService(db_session=db_session)
    etapas_dict = es.listar_etapas(projeto_id=projeto_id)

    if etapas_dict is None:
        return JSONResponse(
                content={'error': 'Projeto não encontrado'},
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    else:
        return etapas_dict
    
@etapa_router.post('/{projeto_id}/etapa', summary="Adiciona uma nova etapa")
def adicionar_etapas(projeto_id: int, etapa: Etapa, db_session: Session = Depends(get_db_session)):
    etapa_service = EtapaService(db_session=db_session)
    
    try:
        id_etapa = etapa_service.criar_etapa(projeto_id=projeto_id, etapa=etapa)
        
        return JSONResponse(
            content={
                'msg': f"Etapa '{etapa.titulo}' criada com sucesso no projeto '{projeto_id}'",
                'id_etapa':  f"'{id_etapa}"
            },
            status_code=status.HTTP_201_CREATED
        )
    except ProjetoNaoEncontradoException as e:
        return JSONResponse(
            content={
                'msg': f"{e.getMensagem()}"
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )
        
    except ErroAoInserirEtapaException as e:
       return JSONResponse(
            content={
                'msg': f"{e.getMensagem()}"
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@etapa_router.put('/etapa/{etapa_id}', summary="Editar uma etapa existente")
def editar_etapa(etapa_id: int, etapa: Etapa, db_session: Session = Depends(get_db_session)):
    etapa_service = EtapaService(db_session=db_session)
    
    try:
        etapa_service.editar_etapa(etapa_id=etapa_id, etapa_alteracao=etapa)
        
        return JSONResponse(
            content={
                'msg': f"Nome da etapa alterado com sucesso para '{etapa.titulo}",
                'id_etapa':  f"'{etapa_id}"
            },
            status_code=status.HTTP_200_OK
        )
    except EtapaNaoEncontradaException as e:
        return JSONResponse(
            content={
                'msg': f"{e.getMensagem()}"
            },
            status_code=status.HTTP_404_NOT_FOUND
        )
    except ErroAoInserirEtapaException as e:
        return JSONResponse(
            content={
                'msg': f"{e.getMensagem()}"
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@etapa_router.delete('/etapa/{etapa_id}', summary="Exclui uma etapa")
def excluir_etapa(etapa_id: int, db_session: Session = Depends(get_db_session)):
    etapa_service = EtapaService(db_session=db_session)
    
    try:
        etapa_service.deletar_etapa(etapa_id=etapa_id)
        
        return JSONResponse(
            content={
                'msg': "Etapa deletada com sucesso!",
                'id_etapa':  f"'{etapa_id}"
            },
            status_code=status.HTTP_200_OK
        )
        
    except EtapaNaoEncontradaException as e:
        return JSONResponse(
            content={
                'msg': f"{e.getMensagem()}"
            },
            status_code=status.HTTP_404_NOT_FOUND
        )
    except ErroAoInserirEtapaException as e:
        return JSONResponse(
            content={
                'msg': f"{e.getMensagem()}"
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )    

# -------- ROTAS PARA TAREFAS -------- #

@tarefas_router.get('/{projeto_id}/{etapa_id}', summary='Listar as tarefas de uma determindada etapa e projeto ')
def listar_tarefas(projeto_id: int, etapa_id: int, db_session: Session = Depends(get_db_session)):
    ts = TarefaService(db_session=db_session)
    tarefas_dict, respostaJSON = ts.listar_tarefas(projeto_id=projeto_id, etapa_id=etapa_id)

    if tarefas_dict is None:
        return respostaJSON

    else:
        return tarefas_dict

@tarefas_router.post('/{projeto_id}/{etapa_id}', summary="Adicionar uma nova tarefa à uma etapa ")
def adicinar_tarefa(projeto_id: int, etapa_id: int, tarefa: Tarefa, db_session: Session = Depends(get_db_session)):
    ts = TarefaService(db_session=db_session)
    sucesso, falha = ts.adicionar_tarefa(projeto_id=projeto_id, etapa_id=etapa_id, tarefa=tarefa)

    if sucesso is None:
        return falha
    
    else: 
        return sucesso

@tarefas_router.put('/{tarefa_id}/descricao', summary="Editar descrição de uma tarefa existente ")
def editar_tarefa_descricao(tarefa_id:int, descricao:str, db_session: Session = Depends(get_db_session)):
    ts = TarefaService(db_session=db_session)
    sucesso, falha = ts.editar_tarefa_descricao(tarefa_id=tarefa_id, descricao=descricao)

    if sucesso is None:
        return falha
    
    else: 
        return sucesso
    
@tarefas_router.put('/{tarefa_id}/responsavel', summary='Altera o responsavel pela tarefa existente ')
def editar_tarefa_responsavel(tarefa_id:int, id_responsavel:int, db_session: Session = Depends(get_db_session)):
    ts = TarefaService(db_session=db_session)
    sucesso, falha = ts.editar_tarefa_responsavel(tarefa_id=tarefa_id, id_responsavel=id_responsavel)

    if sucesso is None:
        return falha
    
    else: 
        return sucesso

@tarefas_router.delete('/{tarefa_id}', summary="Exclui uma tarefa existente")
def excluir_tarefa(tarefa_id:int, db_session: Session = Depends(get_db_session)):
    ts = TarefaService(db_session=db_session)
    sucesso, falha = ts.excluir_tarefa(tarefa_id=tarefa_id)

    if sucesso is None:
        return falha
    
    else:
        return sucesso

@tarefas_router.put('/{tarefa_id}/mudar_etapa', summary="Muda a etapa de uma tarefa")
def mudar_etapa(tarefa_id:int, nova_etapa_id:int, db_session: Session = Depends(get_db_session)):
    ts = TarefaService(db_session=db_session)
    sucesso, falha = ts.mudar_etapa(tarefa_id=tarefa_id, nova_etapa_id=nova_etapa_id)

    if sucesso is None:
        return falha
    
    else: 
        return sucesso

# -------- ROTAS PARA COMENTARIOS -------- #

@comentario_router.get('/{projeto_id}/etapas/{etapa_id}/tarefas/{tarefa_id}/comentarios', summary='Lista todos os comentarios')
def listar_comentarios(projeto_id: int, etapa_id: int, tarefa_id: int, db_session: Session = Depends(get_db_session)):
    cs = ComentarioService(db_session=db_session)
    comentarios_dict, respostaJSON = cs.listar_comentarios(projeto_id=projeto_id, etapa_id=etapa_id, tarefa_id=tarefa_id)

    if comentarios_dict is None:
        return respostaJSON

    else:
        return JSONResponse(
            content=comentarios_dict,
            status_code=status.HTTP_200_OK
        )

@comentario_router.post('/tarefa/{tarefa_id}', summary='Adiciona um comentario a uma tarefa específica')
def adicionar_comentario(tarefa_id: int, comentario: Comentario, db_session: Session = Depends(get_db_session)):
    cs = ComentarioService(db_session=db_session)
    sucesso, falha = cs.adicionar_comentario(tarefa_id=tarefa_id, comentario=comentario)
    
    if sucesso is None:
        return falha
    
    else:
        return sucesso

@comentario_router.put('/{comentario_id}', summary='Atualiza um comentario existente')
def modificar_comentario(comentario_id: int, comentario: str, db_session: Session = Depends(get_db_session)):
    cs = ComentarioService(db_session=db_session)
    sucesso, falha = cs.editar_comentario(comentario_id=comentario_id, comentario=comentario)

    if sucesso is None:
        return falha
    
    else:
        return sucesso

@comentario_router.delete('/{comentario_id}', summary='Excluir um comentario ')
def remover_comentario(comentario_id: int, db_session: Session = Depends(get_db_session)):
    cs = ComentarioService(db_session=db_session)
    sucesso, falha = cs.excluir_comentario(comentario_id=comentario_id)

    if sucesso is None:
        return falha
    
    else:
        return sucesso
