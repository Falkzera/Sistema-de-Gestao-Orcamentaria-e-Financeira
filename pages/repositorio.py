import base64
import streamlit as st
from utils.ui.display import padrao_importacao_pagina, titulos_pagina, rodape_desenvolvedor, img_pag_icon
from utils.repositorio.funcoes_repositorio import restringir_usuario_externo_base
from utils.repositorio.funcoes_repositorio import processar_download

st.set_page_config(page_title="SIGOF", page_icon=img_pag_icon(), layout="wide")

padrao_importacao_pagina()

titulos_pagina("Repositório de Dados", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-folder"></i>')

# CSS e HTML para os cards
cards_html = f"""
<style>
.cards-container {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    padding: 20px 0;
}}

.card {{
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border: 1px solid #e1e5e9;
    transition: all 0.3s ease;
    position: relative;
}}

.card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}}

.card-icon {{
    font-size: 2.5rem;
    margin-bottom: 16px;
    display: block;
}}

.card-title {{
    font-size: 1.25rem;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 8px;
    line-height: 1.3;
}}

.card-description {{
    color: #6b7280;
    font-size: 0.9rem;
    line-height: 1.5;
    margin-bottom: 16px;
}}

.card-tags {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 20px;
}}

.tag {{
    background: #f3f4f6;
    color: #374151;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 500;
}}

.tag.primary {{ background: #dbeafe; color: #1d4ed8; }}
.tag.success {{ background: #dcfce7; color: #166534; }}
.tag.warning {{ background: #fef3c7; color: #92400e; }}

.card-footer {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: auto;
}}

.card-size {{
    color: #9ca3af;
    font-size: 0.8rem;
}}

.download-btn {{
    background: #3b82f6;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 6px;
}}

.download-btn:hover {{
    background: #2563eb;
    transform: translateY(-1px);
}}

.download-btn:active {{
    transform: translateY(0);
}}

.search-container {{
    margin-bottom: 30px;
}}

.search-input {{
    width: 100%;
    padding: 12px 16px;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.2s ease;
}}

.search-input:focus {{
    outline: none;
    border-color: #3b82f6;
}}
</style>

<div class="search-container">
    <input type="text" class="search-input" placeholder="🔍 Buscar bases de dados..." onkeyup="filterCards(this.value)">
</div>

<div class="cards-container" id="cardsContainer">
"""

usuario = st.session_state.get("username", "")
bases_filtradas = restringir_usuario_externo_base(usuario)

for base in bases_filtradas:
    tag_colors = ["primary", "success", "warning"]
    tags_html = ""
    for i, tag in enumerate(base["tags"]):
        color_class = tag_colors[i % len(tag_colors)]
        tags_html += f'<span class="tag {color_class}">{tag}</span>'

    cards_html += f"""
    <div class="card" data-name="{base['nome'].lower()}" data-tags="{' '.join(base['tags']).lower()}">
        <span class="card-icon">{base['icone']}</span>
        <h3 class="card-title">{base['nome']}</h3>
        <p class="card-description">{base['descricao']}</p>
        <div class="card-tags">
            {tags_html}
        </div>
        <div class="card-footer">
            <span class="card-size">{base['tamanho']}</span>
            <button class="download-btn" onclick="downloadBase('{base['id']}')">
                <span>⬇️</span>
                Download
            </button>
        </div>
    </div>
    """

cards_html += """
</div>

<script>
function filterCards(searchTerm) {
    const cards = document.querySelectorAll('.card');
    const term = searchTerm.toLowerCase();

    cards.forEach(card => {
        const name = card.getAttribute('data-name');
        const tags = card.getAttribute('data-tags');

        if (name.includes(term) || tags.includes(term)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

function downloadBase(baseId) {
    // Redireciona para a mesma página com o parâmetro 'download_base'
    const url = new URL(window.location);
    url.searchParams.set('download_base', baseId);
    window.location.href = url.toString();
}
</script>
"""

search_term = st.text_input("🔍 Buscar bases de dados...", "", help="Pesquise pelo nome da base desejada ou por palavras chaves.")

st.caption("Ao clicar em Download, você receberá os dados mais recentes. O tempo de download pode variar conforme o tamanho da base selecionada.")

cols = st.columns(3)
for idx, base in enumerate(bases_filtradas):

    if search_term.strip():
        termo = search_term.strip().lower()
        if termo not in base['nome'].lower() and not any(termo in tag.lower() for tag in base['tags']):
            continue

    with cols[idx % 3]:
        st.markdown(f"""
        <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border: 1px solid #e1e5e9; margin-bottom: 18px;">
            <span style="font-size:2.5rem;">{base['icone']}</span>
            <span style="font-size:1.25rem;font-weight:600;color:#1f2937;margin-left:10px;">{base['nome']}</span>
            <div style="color:#6b7280;font-size:0.9rem;margin:8px 0 12px 0;">{base['descricao']}</div>
            <div style="margin-bottom:10px;">
                {" ".join([f'<span style=\"background:#dbeafe;color:#1d4ed8;padding:4px 8px;border-radius:6px;font-size:0.75rem;font-weight:500;margin-right:4px;\">{tag}</span>' for tag in base['tags']])}
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="color:#9ca3af;font-size:0.8rem;">{base['tamanho']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        excel_data, shape = None, None
        download_btn = st.button(
            f"{base['nome']} ⬇️",
            key=f"download_btn_{base['id']}",
            use_container_width=True,
            type="primary"
        )
        if download_btn:
            excel_data, shape = processar_download(base['arquivo'])
            if excel_data:
                nome_arquivo = base['arquivo'].replace('.parquet', '.xlsx')
                b64 = base64.b64encode(excel_data).decode()
                mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                download_script = f"""
                <html>
                <body>
                <a id="download_link" href="data:{mime};base64,{b64}" download="{nome_arquivo}" style="display:none"></a>
                <script>
                    document.getElementById('download_link').click();
                </script>
                </body>
                </html>
                """
                st.components.v1.html(download_script, height=0)


rodape_desenvolvedor()