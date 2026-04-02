import streamlit as st
import google.generativeai as genai

# 1. COLOCANDO O SEU CRACHÁ VIP DO GOOGLE (PUXANDO DO COFRE DA NUVEM)
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

# 3. LIGANDO O CÉREBRO
modelo = genai.GenerativeModel("gemini-2.5-flash")

# --- INÍCIO DA TELA DO APLICATIVO ---
st.set_page_config(page_title="AJA - Super Easy Lean", page_icon="⚙️")

# --- A FOTO DA AJA ALINHADA COM O TÍTULO ---
col1, col2 = st.columns([1, 4]) 

with col1:
    # O SEGREDO: Criamos um espaço vazio de 15 pixels acima da foto para ela descer e alinhar com o texto
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    try:
        # Usamos o st.image normal que sabemos que funciona!
        st.image("aja.png", width=100)
    except Exception:
        st.write("🤖") 

with col2:
    st.title("AJA - Agente Super Easy Lean")
    
st.write("---") 

# O Caderninho de anotações
if 'usos_gratuitos' not in st.session_state:
    st.session_state.usos_gratuitos = 0

# A Regra do Pedágio
if st.session_state.usos_gratuitos >= 3:
    st.error("Seu teste grátis acabou! 🛑")
    st.write("Para continuar gerando análises profundas com a AJA, assine nosso plano.")
    st.link_button("💳 Pagar Assinatura", "https://buy.stripe.com/seu-link-aqui")

else:
    # A Tela Principal
    st.write(f"Você tem direito a 3 análises gratuitas. Usos até agora: **{st.session_state.usos_gratuitos}**")
    
    st.info("""
    **📝 Como preencher o seu relato para uma análise perfeita:**
    
    * 🛑 **Não proponha soluções:** Descreva apenas os fatos, os sintomas e o impacto.
    * 🗣️ **Traga a voz do Gemba:** Insira os relatos dos operadores e da engenharia.
    * 🔍 **Seja factual:** Inclua dados (turno, modelo, quantidade de refugo).
    """)
    
    # 1. A Caixa de Texto
    problema_do_usuario = st.text_area("Cole aqui o seu relato detalhado do desvio de processo:", height=250)
    
    # 2. O Botão de Upload Múltiplo
    st.write("📎 **Opcional:** Anexe POPs, fotos do defeito ou relatórios (PDF/Imagens):")
    arquivos_anexados = st.file_uploader(
        "Escolha os arquivos", 
        type=['pdf', 'png', 'jpg', 'jpeg'], 
        accept_multiple_files=True, 
        label_visibility="collapsed"
    )
    
    # 3. O Botão de Enviar
    if st.button("Analisar Causa Raiz"):
        if problema_do_usuario == "":
            st.warning("Por favor, descreva o problema antes de analisar.")
        else:
            with st.spinner("A AJA está investigando os fatos e analisando as evidências..."):
                
                # Preparamos a "caixa" base só com texto
                pacote_para_ia = [instrucoes_do_agente, problema_do_usuario]
                
                # Se o usuário escolheu arquivos, fazemos um loop para pegar TODOS eles
                if arquivos_anexados:
                    for arquivo in arquivos_anexados:
                        dados_do_arquivo = arquivo.getvalue()
                        tipo_mime = arquivo.type
                        
                        pacote_para_ia.append({
                            "mime_type": tipo_mime,
                            "data": dados_do_arquivo
                        })
                
                # Enviamos a caixa completa (Texto + Todos os Arquivos) para a IA
                resposta = modelo.generate_content(pacote_para_ia)
                
                # Mostramos o resultado
                st.success("Análise concluída com sucesso!")
                st.markdown(resposta.text)
                
                # Registramos o uso
                st.session_state.usos_gratuitos = st.session_state.usos_gratuitos + 1