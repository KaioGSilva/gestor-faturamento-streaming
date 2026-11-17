import streamlit as st
import pandas as pd
import calendar
from datetime import date
from streamlit_calendar import calendar as st_calendar
import database as db

# Configuração da página
st.set_page_config(page_title="StreamControl | Faturamento", page_icon="📺", layout="wide")
db.criar_tabela()

# --- DICIONÁRIO AMPLIADO DE DOMÍNIOS ---
DOMINIOS_STREAMING = {
    "netflix": "netflix.com",
    "spotify": "spotify.com",
    "prime video": "primevideo.com",
    "amazon prime": "primevideo.com",
    "disney": "disneyplus.com",
    "disney+": "disneyplus.com",
    "max": "max.com",
    "hbo": "max.com",
    "hbomax": "max.com",
    "youtube": "youtube.com",
    "youtube premium": "youtube.com",
    "apple tv": "tv.apple.com",
    "apple music": "music.apple.com",
    "deezer": "deezer.com",
    "globoplay": "globoplay.globo.com",
    "crunchyroll": "crunchyroll.com",
    "paramount": "paramountplus.com",
    "paramount+": "paramountplus.com",
    "game pass": "xbox.com",
    "xbox": "xbox.com",
    "playstation": "playstation.com",
    "ps plus": "playstation.com",
    "twitch": "twitch.tv",
    "steam": "store.steampowered.com",
    "telecine": "telecine.globo.com",
    "premiere": "globoplay.globo.com"
}

def resolver_dominio(nome_servico, site_customizado=""):
    # Se o usuário digitou um site manual no cadastro, usa ele
    if site_customizado and site_customizado.strip():
        dominio_limpo = site_customizado.strip().replace("https://", "").replace("http://", "").rstrip("/")
        return dominio_limpo

    # Senão, busca no dicionário inteligente
    nome_limpo = nome_servico.strip().lower()
    for chave, dominio in DOMINIOS_STREAMING.items():
        if chave in nome_limpo:
            return dominio
    
    # Fallback inteligente: transforma o nome em um domínio provável (ex: "Meu App" -> "meuapp.com")
    dominio_gerado = nome_limpo.replace(" ", "").replace("+", "plus") + ".com"
    return dominio_gerado

def obter_logo(dominio):
    return f"https://www.google.com/s2/favicons?domain={dominio}&sz=64"

def obter_site(dominio):
    return f"https://{dominio}"

def gerar_eventos_calendario(df):
    eventos = []
    ano_atual = date.today().year
    
    for mes in range(1, 13):
        ultimo_dia_mes = calendar.monthrange(ano_atual, mes)[1]
        for _, row in df.iterrows():
            dia_valido = min(int(row["Dia Cobrança"]), ultimo_dia_mes)
            data_str = f"{ano_atual}-{mes:02d}-{dia_valido:02d}"
            
            eventos.append({
                "title": f"💳 {row['Serviço']} (R$ {row['Valor (R$)']:.2f})",
                "start": data_str,
                "end": data_str,
                "backgroundColor": "#FF4B4B",
                "borderColor": "#FF4B4B",
                "allDay": True
            })
    return eventos

# --- BARRA LATERAL (CADASTRO) ---
st.sidebar.header("➕ Nova Assinatura")
with st.sidebar.form("form_assinatura", clear_on_submit=True):
    servico = st.text_input("Nome do Serviço", placeholder="Ex: Netflix, Max, Crunchyroll...")
    categoria = st.selectbox("Categoria", ["Vídeo", "Música", "Jogos", "Leitura", "Outros"])
    valor = st.number_input("Valor Mensal (R$)", min_value=0.01, format="%.2f", step=1.0)
    dia_cobranca = st.number_input("Dia da Cobrança", min_value=1, max_value=31, step=1)
    site_custom = st.text_input("Site Oficial (Opcional)", placeholder="Ex: netflix.com")
    
    enviado = st.form_submit_button("Salvar Assinatura", use_container_width=True)
    if enviado:
        if servico.strip():
            db.adicionar_assinatura(servico.strip(), categoria, valor, dia_cobranca, site_custom.strip())
            st.sidebar.success(f"{servico} adicionado!")
            st.rerun()
        else:
            st.sidebar.error("Digite o nome do serviço.")

# --- ÁREA PRINCIPAL ---
st.title("📺 Controle de Faturamento de Streaming")
st.markdown("Acompanhe seu gasto mensal com assinaturas de streaming.")
st.divider()

dados = db.listar_assinaturas()

if not dados:
    st.info("Você ainda não possui assinaturas cadastradas. Utilize o menu ao lado para adicionar a primeira!")
else:
    # Ajuste para lidar com a tupla vinda do banco (id, servico, categoria, valor, dia, site)
    df = pd.DataFrame(dados, columns=["ID", "Serviço", "Categoria", "Valor (R$)", "Dia Cobrança", "SiteCustom"])
    
    # Processa os domínios, logos e links dinamicamente
    df["Dominio"] = df.apply(lambda row: resolver_dominio(row["Serviço"], row["SiteCustom"]), axis=1)
    df["Logo"] = df["Dominio"].apply(obter_logo)
    df["Acessar"] = df["Dominio"].apply(obter_site)
    
    # Cálculos principais
    total_mensal = df["Valor (R$)"].sum()
    total_anual = total_mensal * 12
    qtd_servicos = len(df)
    mais_caro = df.loc[df["Valor (R$)"].idxmax()]

    # Cartões de Métricas (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Gasto Mensal", f"R$ {total_mensal:,.2f}")
    col2.metric("Projeção Anual", f"R$ {total_anual:,.2f}")
    col3.metric("Assinaturas Ativas", f"{qtd_servicos} serviços")
    col4.metric("Maior Gasto", mais_caro["Serviço"], f"R$ {mais_caro['Valor (R$)']:,.2f}")

    st.divider()

    # Tabela com Logos, Links e Gráfico lado a lado
    col_esq, col_dir = st.columns([1.7, 1])

    with col_esq:
        st.subheader("📋 Suas Assinaturas")
        df_exibicao = df[["Logo", "Serviço", "Categoria", "Valor (R$)", "Dia Cobrança", "Acessar"]].copy()
        
        st.dataframe(
            df_exibicao,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Logo": st.column_config.ImageColumn("Logo", width="small"),
                "Valor (R$)": st.column_config.NumberColumn("Valor Mensal", format="R$ %.2f"),
                "Dia Cobrança": st.column_config.NumberColumn("Dia Vencimento", format="Dia %d"),
                "Acessar": st.column_config.LinkColumn(
                    "Plataforma",
                    help="Clique para abrir o site oficial",
                    display_text="🔗 Abrir Site"
                )
            }
        )

        # Área para remover assinatura
        with st.expander("🗑️ Remover uma assinatura"):
            opcoes_exclusao = {f"{row['Serviço']} (R$ {row['Valor (R$)']:.2f})": row["ID"] for _, row in df.iterrows()}
            selecionado = st.selectbox("Selecione o serviço para excluir", list(opcoes_exclusao.keys()))
            if st.button("Confirmar Exclusão", type="primary"):
                db.deletar_assinatura(opcoes_exclusao[selecionado])
                st.rerun()

    with col_dir:
        st.subheader("📊 Gastos por Categoria")
        gastos_categoria = df.groupby("Categoria")["Valor (R$)"].sum()
        st.bar_chart(gastos_categoria, color="#FF4B4B")

    st.divider()

    # --- SEÇÃO DO CALENDÁRIO ---
    st.subheader("📅 Calendário Anual de Cobranças")
    st.caption("Navegue pelos meses para visualizar os dias de vencimento de cada assinatura.")
    
    eventos_calendario = gerar_eventos_calendario(df)
    opcoes_calendario = {
        "initialView": "dayGridMonth",
        "locale": "pt-br",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,listMonth"
        },
        "buttonText": {
            "today": "Hoje",
            "month": "Mês",
            "list": "Lista"
        },
        "height": 550
    }
    
    st_calendar(events=eventos_calendario, options=opcoes_calendario)