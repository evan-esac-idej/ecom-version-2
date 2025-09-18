import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from time import sleep
import os
import google.generativeai as genai
import os


st.set_page_config(page_title='ecom_events', layout='wide', page_icon='bar_chart')

a, e, i = st.columns([2, 3, 2])
with e:
    st.markdown(
        """
        <h1 style="font-family:sans-serif; color:#1f77b4; text-align:center;">
            <span class="animated-title">Bem vindo a Ecom-Web Eventos</span>
        </h1>

        <style>
        .animated-title {
            display: inline-block;
            overflow: hidden;
            border-right: .15em solid #1f77b4;
            white-space: nowrap;
            animation: typing 3s steps(40, end), blink-caret .75s step-end infinite;
            font-size: 20px;
        }

        @keyframes typing {
            from { width: 0 }
            to { width: 100% }
        }

        @keyframes blink-caret {
            from, to { border-color: transparent }
            50% { border-color: #1f77b4; }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

#with st.sidebar:
    #op = st.selectbox('Catálogo', options=['👥 Clientes', '📈Financeiro', '🗄️Bancos de Dados'], placeholder='Home')

dados = {
    'Mobiliário': {
        'Mesas': 1000,
        'Cadeiras': 100,
        'Kit Utensilios por Mesas': 300,
        'Piscina': 2000,
        'Decorativos': 8000,
        'Jardim': 3000 },
    'alimentação': {
        'Bolo': 1000,
        'Sobremesa': 100,
        'Salgados': 300,
        'Bifé': 2000,
        'Saladas': 8000,
        'Churrasco': 3000
    },
    'entretenimento': {
        'Som': 1000,
        'DJ': 100,
        'Artista ou Banda': 300,
        'Animação em Led': 2000,
        'Fogo de Artifício': 8000,
        'After Party': 3000

    }
}


with st.sidebar.expander(':blue[*Fazer o upload da folha de dados*]', expanded=True):
    # Componente para carregar o arquivo
    arquivo = st.file_uploader(
        'Clique aqui para carregar o arquivo',
        type=['csv', 'xlsx']  # Restringe os tipos de arquivo diretamente no uploader
    )

    st.caption('O arquivo deve conter as colunas obrigatórias para ser processado.')
    # Lista de colunas obrigatórias
    colunas_obrigatorias = ['Data', 'Categorias', 'Qtd', 'Preço', 'Valor']

    # --- LÓGICA DE VALIDAÇÃO ---
    # Só executa se um arquivo foi efetivamente carregado
    if arquivo is not None:
        df = None  # Inicializa o dataframe como None

        try:
            # Tenta ler o arquivo com base na sua extensão
            if arquivo.name.endswith('.csv'):
                df = pd.read_csv(arquivo)
            elif arquivo.name.endswith('.xlsx'):
                df = pd.read_excel(arquivo)
        except Exception as e:
            st.error(f"Ocorreu um erro ao ler o arquivo: {e}")

        # Se a leitura foi bem-sucedida, prossegue com a validação das colunas
        if df is not None:
            # Converte as colunas do dataframe para um conjunto (set) para uma verificação eficiente
            colunas_arquivo = set(df.columns)

            # Verifica se o conjunto de colunas obrigatórias é um subconjunto das colunas do arquivo
            if set(colunas_obrigatorias).issubset(colunas_arquivo):
                st.success('Arquivo válido e carregado com sucesso!')
                st.info(f'{len(df)} linhas foram lidas do arquivo.')

                # Armazena o dataframe no estado da sessão para uso posterior no aplicativo
                st.session_state['df_carregado'] = df[colunas_obrigatorias]

            else:
                # Calcula quais colunas estão em falta para dar um feedback útil
                colunas_em_falta = set(colunas_obrigatorias) - colunas_arquivo
                st.error(f'O arquivo carregado é inválido. As seguintes colunas obrigatórias não foram encontradas:')
                # Usa st.markdown para criar uma lista formatada
                st.markdown(f"**Colunas em Falta:** `{'`, `'.join(colunas_em_falta)}`")

                # Limpa qualquer dataframe antigo do estado da sessão
                if 'df_carregado' in st.session_state:
                    del st.session_state['df_carregado']


# Verifica se o dataframe existe no estado da sessão antes de tentar exibi-lo
if 'df_carregado' in st.session_state:
    st.sidebar.markdown("### Pré-visualização dos Dados")
    st.sidebar.dataframe(st.session_state['df_carregado'])
else:
    st.sidebar.info("Nenhum arquivo válido foi carregado ainda. Por favor, use o painel acima.")
# Inicializa session_state
for key in ['max', 'mean', 'aval', 'carrinho', 'len']:
    if key not in st.session_state:
        st.session_state[key] = [0] if key != 'carrinho' else []
if 'banco_dados' not in st.session_state:
    st.session_state.banco_dados = []


# Função para adicionar item ao carrinho
def adicionar_ao_carrinho(nome, preco, pr):
    df_item = {
        'Data': pd.to_datetime(datetime.now()),
        'Categorias': nome,
        'Qtd': pr,
        'Preço': preco,
        'Valor': pr * preco
    }
    st.session_state.carrinho.append(df_item)
    st.toast(f"{pr}x{nome} no carrinho ✅!", icon="🎉")

# Função para exibir itens (mob, alim, entr)
def exibir_itens(dicionario, especiais=[], coluna=None):
    with coluna:
        for nome, preco in dicionario.items():
            caminho_pasta = os.path.join(os.path.dirname(__file__), 'images')
            caminho_imagem = os.path.join(caminho_pasta, f"{nome}.jpg")
            if os.path.exists(caminho_imagem):
                st.image(caminho_imagem)
            else:
                st.warning(f"Imagem não encontrada: {caminho_imagem}")

            if nome in especiais:
                pr = st.slider(f'Para adicionar **{nome}** arraste para 1', 0, 1, 0)
            else:
                pr = st.number_input(f'Número de {nome}', 0, 100, 0)

            a, i = st.columns(2)
            with a:
                button = st.button(f'Adicionar', key=f'{nome}')
                if button:
                    placeholder = st.empty()
                    if pr == 0:
                        placeholder.warning(f"⚠️ O número de **{nome}** deve ser igual ou maior que 1.")
                        sleep(1.5)
                        placeholder.empty()
                    else:
                        adicionar_ao_carrinho(nome, preco, pr)
            with i:
                st.write(f':green[Preço: **{preco}** Mts/unit]')


# Exemplo de uso no bloco de clientes
taba, tabe, tabi, tabo, tabu = st.tabs(['👥 Cliente', '📈 Financeiro', '🗄️Banco de Dados', '🤖 Assistente', 'ℹ️ Sobre'])
try:
    with taba:
        col_a, col_e, col_i = st.columns(3)
        exibir_itens(dados['Mobiliário'], especiais=['Jardim', 'Piscina', 'Decorativos'], coluna=col_a)
        exibir_itens(dados['alimentação'], especiais=['Bolo'], coluna=col_e)
        exibir_itens(dados['entretenimento'], especiais=['Som', 'DJ', 'Artista ou Banda', 'Fogo de Artifício', 'After Party'], coluna=col_i)

        with st.sidebar:
            try:
                if not pd.DataFrame(st.session_state['df_carregado']).empty:
                    if st.button('Carregar'):
                        st.session_state.carrinho.extend(
                            st.session_state['df_carregado'].to_dict(orient='records')
                        )
                select = st.selectbox('Selecione o número da linha ou index',
                                      options=pd.DataFrame(st.session_state.carrinho).index)
                a, b = st.columns(2)
            except:
                st.empty()
            with a:
                if st.button('Eliminar Item'):
                    st.session_state.carrinho.pop(select)

            with b:
                if st.button('Limpar Dados'):
                    st.session_state.carrinho.clear()
            new_data = pd.DataFrame(st.session_state.carrinho)

            st.dataframe(new_data, hide_index=True)
            st.metric("O Pagamento total", f"{new_data['Valor'].sum():.2f} Mts")

            if st.button("✅ Confirmar e Guardar no Banco de Dados"):
                # Acumula no banco de dados
                st.session_state.banco_dados.extend(st.session_state.carrinho)
                st.success("Itens guardados no banco de dados!")

                data_base = pd.DataFrame(st.session_state.banco_dados)

                st.session_state.aval.append(data_base['Valor'].sum())
                st.session_state.mean.append(data_base['Valor'].mean())
                st.session_state.max.append(data_base['Valor'].max())
                st.session_state.len.append(len(data_base))

            else:
                st.info("Carrinho vazio")

except:
    st.empty()

data_base = pd.DataFrame(st.session_state.banco_dados)
try:
    with tabe:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            try:
                preview = st.session_state.aval[::-1][1]
                st.metric(":grey[*Total de vendas anterior*]", f"{preview:,} Mts")
                st.divider()
                total = data_base['Valor'].sum()
                growth = ((total - preview) / preview) * 100
            except (IndexError, ZeroDivisionError):
                preview = 0
                total = data_base['Valor'].sum()
                growth = 0
            st.metric("Total de Vendas", f"{total:,.2f} Mts", f"{growth:.2f}%")
        with col2:
            try:
                preview = st.session_state.mean[::-1][1]
                st.metric(":grey[*Média anterior*]", f"{preview:,.2f} Mts")
                st.divider()
                total = data_base['Valor'].mean()
                growth = ((total - preview) / preview) * 100
            except (IndexError, ZeroDivisionError):
                preview = 0
                total = data_base['Valor'].mean()
                growth = 0
            st.metric("Média de Venda", f"{total:,.2f} Mts", f"{growth:,.2f}%")

        with col3:
            try:
                preview = st.session_state.max[::-1][1]
                st.metric(":grey[*O Máximo de Vendas anterior*]", f"{preview:,} Mts")
                st.divider()
                total = data_base['Valor'].max()
                growth = ((total - preview) / preview) * 100
            except (IndexError, ZeroDivisionError):
                preview = 0
                total = data_base['Valor'].max()
                growth = 0
            st.metric("Máximo das Vendas", f"{total:,.2f} Mts",  f"{growth:,.2f}%")
        with col4:

            try:
                preview = st.session_state.len[::-1][1]
                st.metric(":grey[*Total do Pedidos anterior*]", f"{preview:,}")
                st.divider()
                total = len(data_base)
                growth = ((total - preview) / preview) * 100
            except (IndexError, ZeroDivisionError):
                preview = 0
                total = len(data_base)
                growth = 0
            st.metric(" Total de Pedidos", f"{total:,}",  f"{growth:,.2f}%")
        st.markdown('---')
        col1, col2 = st.columns(2)
        with col1:
            fig_bar = px.bar(data_base.groupby("Categorias")["Qtd"].sum().sort_values(ascending=False).reset_index()
                             , x="Categorias", y="Qtd",
                             title="Produtos mais vendidos", text='Qtd', color='Qtd')
            fig_bar.update_traces(textposition='outside')
            st.plotly_chart(fig_bar, use_container_width=True)
        with col2:
            import plotly.graph_objects as go

            cores = [
                # Tons de Azul
                "#e3f2fd",  # Azul muito claro
                "#bbdefb",  # Azul claro
                "#90caf9",  # Azul suave
                "#64b5f6",  # Azul médio
                "#2196f3",  # Azul padrão
                "#1565c0",  # Azul escuro
                "#0d47a1",  # Azul profundo

                # Tons de Vermelho
                "#ffebee",  # Vermelho muito claro
                "#ffcdd2",  # Vermelho claro
                "#ef9a9a",  # Vermelho suave
                "#e57373",  # Vermelho médio
                "#f44336",  # Vermelho padrão
                "#c62828",  # Vermelho escuro
                "#8b0000",  # Vermelho profundo
                "#4a0000"  # Vermelho quase vinho
            ]

            fig = go.Figure(data=[go.Pie(title='Percentagem de cada categoria',
                labels=data_base['Categorias'],
                values=data_base['Valor'],
                hole=0.5,
                marker=dict(colors=cores),  # aplica cores fixas
                pull=[0, 0.1, 0, 0.3]
            )])
            fig.update_traces(textposition='inside', textinfo='percent')
            st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            fig_line = px.line(data_base, x="Data", y="Valor", color="Categorias",
                               markers=True, title="Evolução Diária")
            st.plotly_chart(fig_line, use_container_width=True)
        with col2:

            receita = data_base.groupby("Categorias")["Valor"].sum().sort_values(ascending=False).reset_index()
            figh = px.bar(receita, x="Valor", y="Categorias", orientation="h",
                          title="Produtos por Receita", text="Valor")
            figh.update_traces(textposition='inside')
            st.plotly_chart(figh, use_container_width=True)
        st.markdown('---')
        group_lis = st.multiselect('Verificar o Valor Total em:', options=data_base.columns, default='Data')
        grouped = data_base.groupby(group_lis)['Valor'].sum()
        df_grouped = pd.DataFrame(grouped)
        df_ = df_grouped.rename(columns={'Valor': 'Valor total'})
        with st.expander(''):
            st.dataframe(df_)

        st.markdown('---')

        cat = st.multiselect('Selecione a(s) Categoria(s) para análise', options=data_base['Categorias'].unique(),)


        df_filt = data_base.query('Categorias == @cat')
        col1, col2, col3 = st.columns(3)
        with col1:
            sum_cat = df_filt['Valor'].sum()
            total = data_base['Valor'].sum()
            per_cat = (sum_cat / total) * 100
            st.metric(f"Total de Vendas de "+", ".join(cat), f"{df_filt['Valor'].sum():,.2f} Mts",
                      f"{per_cat:.2f}% dos produtos")

        with col2:
            qtd_total = df_filt['Qtd'].sum()
            total = data_base['Qtd'].sum()
            per_cat = (qtd_total / total) * 100
            st.metric("Qtd Vendidas", f"{qtd_total:,.2f} Unidades", f"{per_cat:,.2f}% das unidades")

        with col3:
            total = df_filt['Valor'].max()
            st.metric("Máximo de venda em Dia", f"{total:,.2f} Mts", f"{growth:,.2f}%")
        st.dataframe(df_filt)
except:
    st.warning('Adicione produtos a carrinha e no banco de dados...')
    st.empty()

try:
    with tabi:
        data_base = pd.DataFrame(st.session_state.banco_dados)
        st.dataframe(data_base)
        button = st.button('Exportar dados em Excel')
        if button:
            placeholder = st.empty()
            placeholder.success(f"Novo Banco de Dados arquivado com sucesso ✅")
            sleep(1.5)
            placeholder.empty()
except:
    st.empty()

try:
    with tabo:
            import streamlit as st
            import google.generativeai as genai
            import os
    
            st.subheader(" Chatbot com e-com web eventos")
            st.caption("Um assistente convencional para o aplicativo e-com web eventos")
    
            # --- Configuração da API Key do Gemini ---
    
            # A forma mais segura de gerenciar a chave é através do st.secrets (para deploy)
            # Para uso local, você pode usar o sidebar para inseri-la.
    
            # Tenta obter a chave a partir do st.secrets
            try:
                api_key = st.secrets["GEMINI_API_KEY"]
            except (FileNotFoundError, KeyError):
                # Se não encontrar, solicita ao usuário na barra lateral
                st.sidebar.header("Configuração")
                api_key = st.sidebar.text_input(
                    "Cole sua API Key do Google Gemini aqui:",
                    type="password",
                    help="Obtenha sua chave em https://aistudio.google.com/"
                )

            # Se a chave não for fornecida, exibe um aviso e interrompe a execução
            if not api_key:
                st.info("Por favor, insira sua API Key do Google Gemini na barra lateral para começar.")
                st.stop()

            # Configura a biblioteca do Gemini com a chave fornecida
            try:
                genai.configure(api_key=api_key)
            except Exception as e:
                st.error(f"Erro ao configurar a API do Gemini: {e}")
                st.stop()
    
    
            # --- NOVO: Instrução Inicial (Contexto) atualizada ---
            system_instruction = f"""
            Você é o "Assistente EventsBot", um chatbot especialista no aplicativo web "e-com web  Eventos".
            Sua função é responder a perguntas sobre as funcionalidades do aplicativo e sobre os resultados financeiros da empresa, com base ESTRITAMENTE nas informações fornecidas.
        
            REGRAS:
            1.  **Persona:** Seja profissional, preciso e direto.
            2.  **Base de Conhecimento:** NUNCA invente informações. Se a resposta não estiver no contexto que eu fornecer, diga "Não tenho essa informação na minha base de dados."
            3.  **Segurança:** Nunca partilhe informações financeiras a menos que a pergunta seja explicitamente sobre finanças.
            4.  **Foco:** Recuse educadamente responder a perguntas que não sejam sobre o e-com web eventos. Sugira que entre em contacto com a agência GHT.
        
            Aqui está a base de conhecimento sobre dos Dados:
            Catálogo: {dados}
            Mobiliário(Data,	Categorias,	Qtd,	Preço,	Valor): {dados['Mobiliário']}
            Entretenimento(Data,	Categorias,	Qtd,	Preço,	Valor): {dados['entretenimento']}
            alimentação(Data,	Categorias,	Qtd,	Preço,	Valor): {dados['alimentação']}
            Banco de dados: {st.session_state.banco_dados}
            carrinho: {st.session_state.carrinho}
            Total de Vendas: {data_base['Valor'].sum()} Mts
            ---
        
            ---
        
            Aqui está a base de conhecimento sobre os RESULTADOS FINANCEIROS:
            ---
        
            ---
            """
            # --- Inicialização do Modelo e do Histórico da Conversa ---
    
            MODEL_NAME = "gemini-1.5-flash-latest"
    
            # MODIFICAÇÃO: Inicia o histórico com a instrução e uma primeira mensagem
            if "messages" not in st.session_state:
                st.session_state.messages = [
                    {"role": "assistant",
                     "content": "Olá! Eu sou o Event, o seu assistente virtual para explorar o ecom-web. Como posso ajudar?"}
                ]
    
            # MODIFICAÇÃO: Passa o histórico inicial para o modelo
            if "chat" not in st.session_state:
                model = genai.GenerativeModel(MODEL_NAME)
                # O Gemini usa o histórico para entender o contexto.
                # Nós simulamos que o "user" deu a instrução e o "model" entendeu.
                initial_history = [
                    {'role': 'user', 'parts': [system_instruction]},
                    {'role': 'model', 'parts': [
                        "Entendido. Olá! Eu sou o Event, o seu assistente virtual para explorar o ecom-web. Como posso ajudar?"]}
                ]
                st.session_state.chat = model.start_chat(history=initial_history)
    
            # ... (o resto do código, como a interface do chat e a função `send_message_to_gemini`, permanece exatamente o mesmo) ...
    
            # Exibe as mensagens do histórico na interface
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
    
            # ... (resto do código igual)
    
    
            # --- Função para Enviar Mensagem e Obter Resposta ---
            def send_message_to_gemini(prompt):
                """Envia a mensagem para a API do Gemini e retorna a resposta."""
                try:
                    # O histórico é gerenciado automaticamente pelo objeto `chat`
                    response = st.session_state.chat.send_message(prompt)
                    return response.text
                except Exception as e:
                    # Trata possíveis erros na chamada da API
                    st.error(f"Ocorreu um erro ao comunicar com a API: {e}")
                    return None
    
            try:
                # Captura a entrada do usuário através do st.chat_input
                if prompt := st.chat_input("Digite sua mensagem..."):
                    # 1. Adiciona e exibe a mensagem do usuário
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.markdown(prompt)
    
                    # 2. Envia a mensagem para o Gemini e obtém a resposta
                    with st.chat_message("assistant"):
                        with st.spinner("Pensando..."):
                            response_text = send_message_to_gemini(prompt)
                            if response_text:
                                st.markdown(response_text)
                                # 3. Adiciona a resposta do assistente ao histórico
                                st.session_state.messages.append({"role": "assistant", "content": response_text})
            except:
                st.empty()
except:
    st.empty()    
with tabu:
    st.header("📌 Sobre o e-com web eventos")
    st.write(
        """
        O **e-com web eventos** é uma plataforma desenvolvida por Ginélio HT para facilitar a organização, 
        gestão e personalização de **eventos sociais e corporativos**.  
        
        ### 🎯 Objectivo
        Tornar a experiência de planejar eventos **mais simples, rápida e interativa**, 
        conectando clientes e fornecedores em um só ambiente digital.

        ### ⚙️ Funcionalidades Principais
        - 📦 **Catálogo Interativo**: escolha de mobiliário, decoração e serviços com imagens e preços.  
        - 🛒 **Carrinho de Compras**: seleção rápida de itens com resumo fixo de valores.  
        - 📊 **Dashboard Financeiro**: acompanhamento das vendas e métricas de crescimento.  
        - 🤖 **Assistente Virtual (EventBot)**: chatbot inteligente integrado com Gemini para tirar dúvidas.  
        - 🎨 **Experiência Personalizada**: filtros, busca rápida e categorias colapsáveis.  

        ### 🌟 Diferenciais
        - Plataforma **intuitiva** e fácil de usar.  
        - Informações em **tempo real** sobre o evento e finanças.  
        - Suporte interativo com **IA generativa**.  
        - Design moderno com animações e efeitos visuais.  

        ---
        💡 O e-com web eventos foi criado para **revolucionar a forma como os eventos são planejados**, 
        trazendo tecnologia e praticidade para quem organiza e para quem participa.
        """
    )
    st.success("✅ Explore as outras abas para conhecer todas as funcionalidades!")

   
























