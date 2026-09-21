import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO

from leitor_contratos import analisar_contrato


# ============================================================
# VARIÁVEIS
# ============================================================

arquivos_selecionados = []


# ============================================================
# SELECIONAR PDFs
# ============================================================

def selecionar_arquivos():
    global arquivos_selecionados

    arquivos = filedialog.askopenfilenames(
        title="Selecione os contratos",
        filetypes=[
            ("Arquivos PDF", "*.pdf")
        ]
    )

    if not arquivos:
        return

    arquivos_selecionados = list(arquivos)

    quantidade = len(arquivos_selecionados)

    if quantidade == 1:
        texto_status.config(
            text="1 contrato selecionado"
        )
    else:
        texto_status.config(
            text=f"{quantidade} contratos selecionados"
        )

    botao_analisar.config(state="normal")

    texto_resultado.delete("1.0", tk.END)

    texto_resultado.insert(
        tk.END,
        "Contratos selecionados:\n\n"
    )

    for arquivo in arquivos_selecionados:
        nome = Path(arquivo).name
        texto_resultado.insert(
            tk.END,
            f"• {nome}\n"
        )


# ============================================================
# ANALISAR PDFs
# ============================================================

def analisar_contratos():

    if not arquivos_selecionados:
        messagebox.showwarning(
            "Nenhum contrato",
            "Selecione pelo menos um contrato PDF."
        )
        return

    texto_resultado.delete("1.0", tk.END)

    quantidade = len(arquivos_selecionados)

    texto_resultado.insert(
        tk.END,
        "=" * 70 + "\n"
    )

    texto_resultado.insert(
        tk.END,
        "ANÁLISE DE CONTRATOS\n"
    )

    texto_resultado.insert(
        tk.END,
        "=" * 70 + "\n\n"
    )

    texto_resultado.insert(
        tk.END,
        f"{quantidade} contrato(s) selecionado(s).\n\n"
    )

    janela.update_idletasks()

    botao_analisar.config(
        state="disabled",
        text="ANALISANDO..."
    )

    botao_selecionar.config(
        state="disabled"
    )

    janela.update()

    erros = 0

    for numero, arquivo in enumerate(
        arquivos_selecionados,
        start=1
    ):

        caminho = Path(arquivo)

        texto_status.config(
            text=(
                f"Analisando {numero} de {quantidade}: "
                f"{caminho.name}"
            )
        )

        janela.update()

        saida = StringIO()

        try:

            with redirect_stdout(saida):
                analisar_contrato(caminho)

            resultado = saida.getvalue()

            texto_resultado.insert(
                tk.END,
                resultado
            )

            texto_resultado.insert(
                tk.END,
                "\n\n"
            )

        except Exception as erro:

            erros += 1

            texto_resultado.insert(
                tk.END,
                "\n" + "!" * 70 + "\n"
            )

            texto_resultado.insert(
                tk.END,
                f"ERRO AO ANALISAR: {caminho.name}\n"
            )

            texto_resultado.insert(
                tk.END,
                f"{erro}\n"
            )

            texto_resultado.insert(
                tk.END,
                "!" * 70 + "\n\n"
            )

        texto_resultado.see(tk.END)

        janela.update()

    # --------------------------------------------------------
    # FINALIZAÇÃO
    # --------------------------------------------------------

    texto_resultado.insert(
        tk.END,
        "\n" + "=" * 70 + "\n"
    )

    texto_resultado.insert(
        tk.END,
        "ANÁLISE FINALIZADA\n"
    )

    texto_resultado.insert(
        tk.END,
        "=" * 70 + "\n"
    )

    texto_resultado.insert(
        tk.END,
        f"\nContratos processados: {quantidade}\n"
    )

    if erros:
        texto_resultado.insert(
            tk.END,
            f"Erros encontrados: {erros}\n"
        )

    texto_resultado.see(tk.END)

    texto_status.config(
        text="Análise concluída"
    )

    botao_analisar.config(
        state="normal",
        text="ANALISAR CONTRATOS"
    )

    botao_selecionar.config(
        state="normal"
    )

    messagebox.showinfo(
        "Análise concluída",
        "A análise dos contratos foi concluída."
    )


# ============================================================
# LIMPAR
# ============================================================

def limpar_resultados():
    global arquivos_selecionados

    arquivos_selecionados = []

    texto_resultado.delete(
        "1.0",
        tk.END
    )

    texto_status.config(
        text="Nenhum contrato selecionado"
    )

    botao_analisar.config(
        state="disabled"
    )


# ============================================================
# JANELA PRINCIPAL
# ============================================================

janela = tk.Tk()

janela.title(
    "Leitor de Contratos"
)

janela.geometry(
    "950x700"
)

janela.minsize(
    800,
    600
)


# ============================================================
# TÍTULO
# ============================================================

titulo = tk.Label(
    janela,
    text="Leitor de Contratos",
    font=(
        "Segoe UI",
        22,
        "bold"
    )
)

titulo.pack(
    pady=(25, 5)
)


subtitulo = tk.Label(
    janela,
    text=(
        "Identificação automática de valores "
        "e formas de remuneração"
    ),
    font=(
        "Segoe UI",
        11
    )
)

subtitulo.pack(
    pady=(0, 20)
)


# ============================================================
# BOTÕES SUPERIORES
# ============================================================

frame_botoes = tk.Frame(
    janela
)

frame_botoes.pack(
    pady=10
)


botao_selecionar = tk.Button(
    frame_botoes,
    text="Selecionar contratos PDF",
    font=(
        "Segoe UI",
        11
    ),
    width=25,
    height=2,
    command=selecionar_arquivos
)

botao_selecionar.grid(
    row=0,
    column=0,
    padx=10
)


botao_analisar = tk.Button(
    frame_botoes,
    text="ANALISAR CONTRATOS",
    font=(
        "Segoe UI",
        11,
        "bold"
    ),
    width=25,
    height=2,
    state="disabled",
    command=analisar_contratos
)

botao_analisar.grid(
    row=0,
    column=1,
    padx=10
)


botao_limpar = tk.Button(
    frame_botoes,
    text="Limpar",
    font=(
        "Segoe UI",
        11
    ),
    width=12,
    height=2,
    command=limpar_resultados
)

botao_limpar.grid(
    row=0,
    column=2,
    padx=10
)


# ============================================================
# STATUS
# ============================================================

texto_status = tk.Label(
    janela,
    text="Nenhum contrato selecionado",
    font=(
        "Segoe UI",
        10
    )
)

texto_status.pack(
    pady=10
)


# ============================================================
# RESULTADOS
# ============================================================

frame_resultados = tk.Frame(
    janela
)

frame_resultados.pack(
    fill="both",
    expand=True,
    padx=30,
    pady=(5, 25)
)


titulo_resultado = tk.Label(
    frame_resultados,
    text="Resultados",
    font=(
        "Segoe UI",
        12,
        "bold"
    )
)

titulo_resultado.pack(
    anchor="w",
    pady=(0, 5)
)


frame_texto = tk.Frame(
    frame_resultados
)

frame_texto.pack(
    fill="both",
    expand=True
)


barra_rolagem = tk.Scrollbar(
    frame_texto
)

barra_rolagem.pack(
    side="right",
    fill="y"
)


texto_resultado = tk.Text(
    frame_texto,
    font=(
        "Consolas",
        10
    ),
    wrap="word",
    yscrollcommand=barra_rolagem.set
)

texto_resultado.pack(
    side="left",
    fill="both",
    expand=True
)


barra_rolagem.config(
    command=texto_resultado.yview
)


# ============================================================
# RODAPÉ
# ============================================================

rodape = tk.Label(
    janela,
    text=(
        "Resultados classificados como REVISAR "
        "devem passar por conferência manual."
    ),
    font=(
        "Segoe UI",
        9
    )
)

rodape.pack(
    pady=(0, 15)
)


# ============================================================
# INICIAR
# ============================================================

janela.mainloop()