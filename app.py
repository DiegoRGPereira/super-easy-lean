import streamlit as st
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection

# 1. CRACHÁ VIP DO GOOGLE (PUXANDO DO COFRE)
chave_secreta = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=chave_secreta)

# 2. O SYSTEM PROMPT (A alma da AJA)
instrucoes_do_agente = """
O seu nome é AJA. Você é a Agente Virtual da Super Easy Lean, uma Engenheira de Produção e especialista Sênior em Melhoria Contínua. 
Analise o problema abaixo e gere a saída EXATAMENTE nesta ordem e com este rigor técnico:

Regras de Ouro Analíticas:
- Hierarquia de Causas: Esgote todas as variáveis técnicas e físicas (parâmetros de máquina, variações de matéria-prima, tolerâncias dimensionais, falhas no método, desgaste de gabaritos e ausência de Poka-Yoke) ANTES de considerar o fator humano. O "erro operacional", "falta de atenção" ou "falta de treinamento" só devem ser citados como última alternativa. O processo deve proteger o operador.
- Foco na Origem: Identifique se as soluções atuais são apenas paliativas (contenção) e force a análise para o ponto de origem do defeito.

Etapas da Análise:
1. 5W2H: Compreensão clara do problema.
2. Ishikawa (Espinha de Peixe): Categorize causas nos 6Ms.
3. 5 Porquês: Investigação profunda focada na quebra do processo/método.
4. Diagnóstico da Causa Raiz: Declaração concisa e técnica.
5. PDCA: Plano de Ação estruturado (Plan, Do, Check, Act).

Aqui está o relato e os documentos anexos para você analisar:
"""

modelo = genai.GenerativeModel("gemini-2.5-flash")

# --- INÍCIO DA TELA DO APLICATIVO ---
st.set_page_config(page_title="AJA - Super Easy Lean", page_icon="⚙️")

# 3. LENDO A PLANILHA DO GOOGLE SHEETS
# O ttl=0 garante que a AJA sempre leia a planilha em tempo real (sem atrasos)
conn = st.connection("gsheets", type=GSheetsConnection)
planilha = conn.read(ttl=0) 

# --- A FOTO E O TÍTULO ---
col1, col2 = st.columns([1, 4]) 

with col1:
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    try:
        st.image("aja.png", width=100)
    except Exception:
        st.write("🤖") 

with col2:
    st.title("AJA - Agente Super Easy Lean")
    # --- NOVIDADE: A DESCRIÇÃO DA AJA ---
    st.markdown("**🤖 Assistente Especialista em Análise de Causa Raiz**")
    st.caption(
        "Transforme relatos do Gemba e evidências visuais em diagnósticos precisos. "
        "A AJA aplica o rigor do Lean Manufacturing para identificar a verdadeira origem de desvios de processo, "
        "estruturar diagramas de Ishikawa, 5 Porquês e entregar um Plano de Ação (PDCA) pronto para execução."
    )
    
st.write("---")

# --- A PORTA DE ENTRADA (LOGIN) ---
email_usuario = st.text_input("🔑 Digite seu e-mail para acessar a AJA:")

if email_usuario: # Só mostra o resto se o usuário digitar algo
    eh_vip = False
    
    # A AJA olha a coluna 'Email' da planilha para ver se acha o e-mail digitado
    if email_usuario in planilha['Email'].values:
        # Se achou, ela olha na mesma linha para ver se o Status é VIP
        status_do_usuario = planilha.loc[planilha['Email'] == email_usuario, 'Status'].values[0]
        if status_do_usuario == "VIP":
            eh_vip = True

    # --- REGRAS DE CATRACA ---
    pode_usar = False
    
    if eh_vip:
        st.success("✅ Acesso VIP Reconhecido! Pode utilizar a AJA à vontade.")
        pode_usar = True
    else:
        # Lógica de quem não é VIP (Visitantes / Teste Grátis)
        if 'usos_gratuitos' not in st.session_state:
            st.session_state.usos_gratuitos = 0
            
        if st.session_state.usos_gratuitos >= 3:
            st.error("🛑 Seu teste grátis (3 usos) acabou!")
            st.write("Para continuar gerando análises profundas, assine nosso plano.")
            st.link_button("💳 Assinar Super Easy Lean", "https://buy.stripe.com/seu-link-aqui")
        else:
            st.info(f"Você está no modo Teste. Usos restantes hoje: **{3 - st.session_state.usos_gratuitos}**")
            pode_usar = True

    # --- A ÁREA DE TRABALHO (Só aparece se o usuário tiver permissão) ---
    if pode_usar:
        problema_do_usuario = st.text_area("Cole aqui o relato do problema:", height=200)
        
        arquivos_anexados = st.file_uploader(
            "📎 Opcional: Anexe fotos ou PDFs:", 
            type=['pdf', 'png', 'jpg', 'jpeg'], 
            accept_multiple_files=True, 
            label_visibility="collapsed"
        )
        
        if st.button("Analisar Causa Raiz"):
            if problema_do_usuario == "":
                st.warning("Por favor, descreva o problema antes de analisar.")
            else:
                with st.spinner("AJA está investigando os fatos..."):
                    
                    pacote_para_ia = [instrucoes_do_agente, problema_do_usuario]
                    
                    if arquivos_anexados:
                        for arquivo in arquivos_anexados:
                            pacote_para_ia.append({
                                "mime_type": arquivo.type,
                                "data": arquivo.getvalue()
                            })
                    
                    resposta = modelo.generate_content(pacote_para_ia)
                    
                    st.success("Análise concluída!")
                    st.markdown(resposta.text)
                    
                    # Se não for VIP, ela "fura o cartão" e gasta 1 uso
                    if not eh_vip:
                        st.session_state.usos_gratuitos += 1
                        st.rerun() # Atualiza a tela para mostrar a contagem caindo