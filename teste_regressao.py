from pathlib import Path

from leitor_contratos import (
    extrair_texto_pdf,
    procurar_valores,
    classificar_valor,
    detectar_cronograma_percentual,
    procurar_valor_base_cronograma,
)


PASTA_CONTRATOS = Path("contratos")


# ============================================================
# CASOS DE TESTE
# ============================================================

CASOS_TESTE = [

    # --------------------------------------------------------
    # CASOS POSITIVOS
    # O programa DEVE encontrar o valor correto.
    # --------------------------------------------------------

    {
        "nome": "PANIA CITO",
        "tipo_teste": "VALOR",
        "arquivo_contem": (
            "Barueri - PANIA_x_JT_-_Locação_Escritório_101_e_104_CITO 29"
        ),
        "valor_esperado": 13802.50,
        "cronograma_esperado": None,
    },

    {
        "nome": "PANIA 21.09.2021",
        "tipo_teste": "VALOR",
        "arquivo_contem": (
            "contrato assinado e rubricado - PANIA_x_JT 21.09.2021"
        ),
        "valor_esperado": 622556.75,
        "cronograma_esperado": None,
    },

    {
        "nome": "São José do Rio Preto",
        "tipo_teste": "VALOR",
        "arquivo_contem": "CONTRATO ASSINADO SJ RIO PRETO 5",
        "valor_esperado": 4000.00,
        "cronograma_esperado": None,
    },

    {
        "nome": "SBN",
        "tipo_teste": "VALOR",
        "arquivo_contem": "CONTRATO DE LOCACAO - SBN-SP",
        "valor_esperado": 16000.00,
        "cronograma_esperado": None,
    },

    {
        "nome": "FULAYN",
        "tipo_teste": "VALOR",
        "arquivo_contem": "CONTRATO FULAYN",
        "valor_esperado": 18000.00,
        "cronograma_esperado": None,
    },

    {
        "nome": "Caruaru",
        "tipo_teste": "VALOR",
        "arquivo_contem": "CONTRATO LOCACAO CARUARU PE",
        "valor_esperado": 8000.00,
        "cronograma_esperado": None,
    },

    {
        "nome": "Volvo",
        "tipo_teste": "VALOR",
        "arquivo_contem": "Contrato_Volvo_atualizado_18_05_2026",
        "valor_esperado": 25085000.00,
        "cronograma_esperado": None,
    },

    {
        "nome": "FW15",
        "tipo_teste": "VALOR",
        "arquivo_contem": "FW15 - GRU BP",
        "valor_esperado": 1041056.03,
        "cronograma_esperado": None,
    },

    {
        "nome": "Guarulhos",
        "tipo_teste": "VALOR",
        "arquivo_contem": "GUARULHOSBP JTEXPRESS",
        "valor_esperado": 13568.75,
        "cronograma_esperado": None,
    },

    {
        "nome": "Itupeva",
        "tipo_teste": "VALOR",
        "arquivo_contem": "ITUPEVA - CONTRATO",
        "valor_esperado": 3500.00,
        "cronograma_esperado": None,
    },

    {
        "nome": "FAZIX",
        "tipo_teste": "VALOR",
        "arquivo_contem": "CONTRATO_PROJETO_SIGATMS_FAZIX",
        "valor_esperado": 81000.00,
        "cronograma_esperado": [
            "20%",
            "30%",
            "30%",
            "20%",
        ],
    },

    {
        "nome": "Contagem RCI Business",
        "tipo_teste": "VALOR",
        "arquivo_contem": "2 CTT RC BUSINESS - JT_CDContagem",
        "valor_esperado": 309402.75,
        "cronograma_esperado": None,
    },

    {
        "nome": "CAPTA Mobilidade",
        "tipo_teste": "VALOR",
        "arquivo_contem": "CONTRATO_CAPTA MOBILIDADE",
        "valor_esperado": 19850.00,
        "cronograma_esperado": None,
    },

    # --------------------------------------------------------
    # CASO NEGATIVO
    #
    # O programa pode encontrar R$ 167,50 no TWO MOT,
    # mas NÃO deve tratá-lo automaticamente como
    # remuneração principal.
    # --------------------------------------------------------

    {
        "nome": "TWO MOT - preço variável",
        "tipo_teste": "REVISAR",
        "arquivo_contem": "CONTRATO TWO MOT",
    },

    # --------------------------------------------------------
    # NOVO TESTE - VAMOS
    #
    # Este teste pode FALHAR na V4.3.
    # Isso é proposital.
    #
    # A verdade validada manualmente é:
    # R$ 310.000,00
    # --------------------------------------------------------

    {
        "nome": "VAMOS - compra de veículo",
        "tipo_teste": "VALOR",
        "arquivo_contem": (
            "CONTRATO DE VENDA E COMPRA DE VEICULO - FINAL_VAMOS LOCACAO"
        ),
        "valor_esperado": 310000.00,
        "cronograma_esperado": None,
    },
]


# ============================================================
# FORMATAÇÃO
# ============================================================

def formatar_reais(valor):

    if valor is None:
        return "N/A"

    texto = f"{valor:,.2f}"

    texto = (
        texto
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"R$ {texto}"


# ============================================================
# LOCALIZAR PDF
# ============================================================

def encontrar_arquivo(texto_procurado):

    texto_procurado = texto_procurado.lower()

    for arquivo in PASTA_CONTRATOS.glob("*.pdf"):

        if texto_procurado in arquivo.name.lower():
            return arquivo

    return None


# ============================================================
# NORMALIZAR CRONOGRAMA
# ============================================================

def normalizar_cronograma(cronograma):

    if not cronograma:
        return []

    return [
        str(item).strip()
        for item in cronograma
    ]


# ============================================================
# ADAPTADOR DA V4.3
#
# Esta função transforma o resultado das funções atuais
# do leitor em uma estrutura simples para os testes.
# ============================================================

def obter_resultado_contrato(caminho_pdf):

    paginas = extrair_texto_pdf(
        caminho_pdf
    )

    valores = procurar_valores(
        paginas
    )

    classificacao, melhor_valor = classificar_valor(
        valores
    )

    cronograma = detectar_cronograma_percentual(
        paginas
    )

    valor_cronograma = None

    if cronograma:

        valor_cronograma = procurar_valor_base_cronograma(
            paginas
        )

    # --------------------------------------------------------
    # CASO COM CRONOGRAMA
    # Exemplo: FAZIX
    # --------------------------------------------------------

    if cronograma and valor_cronograma:

        return {
            "tipo": "VALOR_MONETARIO_CRONOGRAMA",
            "valor": valor_cronograma["valor_numerico"],
            "confianca": "ALTA",
            "cronograma": cronograma["percentuais"],
        }

    # --------------------------------------------------------
    # VALOR MONETÁRIO NORMAL
    # --------------------------------------------------------

    if melhor_valor:

        return {
            "tipo": "VALOR_MONETARIO",
            "valor": melhor_valor["valor_numerico"],
            "confianca": classificacao,
            "cronograma": (
                cronograma["percentuais"]
                if cronograma
                else None
            ),
        }

    # --------------------------------------------------------
    # NADA ENCONTRADO
    # --------------------------------------------------------

    return {
        "tipo": "NAO_ENCONTRADO",
        "valor": None,
        "confianca": "NAO_ENCONTRADO",
        "cronograma": None,
    }


# ============================================================
# TESTAR UM CASO
# ============================================================

def testar_caso(caso):

    print()
    print("=" * 70)
    print(f"TESTE: {caso['nome']}")
    print("=" * 70)

    arquivo = encontrar_arquivo(
        caso["arquivo_contem"]
    )

    if arquivo is None:

        print(
            "STATUS: ARQUIVO NÃO ENCONTRADO"
        )

        print(
            f"Procurado por: {caso['arquivo_contem']}"
        )

        return {
            "nome": caso["nome"],
            "status": "ARQUIVO_NAO_ENCONTRADO",
        }

    print(
        f"Arquivo: {arquivo.name}"
    )

    try:

        resultado = obter_resultado_contrato(
            arquivo
        )

    except Exception as erro:

        print()
        print("STATUS: ERRO")

        print(
            f"Erro ao analisar contrato: {erro}"
        )

        return {
            "nome": caso["nome"],
            "status": "ERRO",
        }

    tipo_teste = caso["tipo_teste"]


    # ========================================================
    # TESTE POSITIVO
    # ========================================================

    if tipo_teste == "VALOR":

        esperado = caso["valor_esperado"]

        obtido = resultado.get(
            "valor"
        )

        confianca = resultado.get(
            "confianca"
        )

        print(
            f"Esperado: {formatar_reais(esperado)}"
        )

        print(
            f"Obtido:   {formatar_reais(obtido)}"
        )

        print(
            f"Confiança: {confianca}"
        )

        # ----------------------------------------------------
        # VALOR
        # ----------------------------------------------------

        valor_ok = False

        if obtido is not None:

            valor_ok = (
                abs(obtido - esperado)
                < 0.01
            )

        # ----------------------------------------------------
        # CRONOGRAMA
        # ----------------------------------------------------

        cronograma_esperado = caso.get(
            "cronograma_esperado"
        )

        cronograma_ok = True

        if cronograma_esperado is not None:

            cronograma_obtido = normalizar_cronograma(
                resultado.get("cronograma")
            )

            cronograma_esperado = normalizar_cronograma(
                cronograma_esperado
            )

            print(
                f"Cronograma esperado: "
                f"{cronograma_esperado}"
            )

            print(
                f"Cronograma obtido:   "
                f"{cronograma_obtido}"
            )

            cronograma_ok = (
                cronograma_obtido
                == cronograma_esperado
            )

        # ----------------------------------------------------
        # RESULTADO
        #
        # Para um teste positivo:
        #
        # 1. valor precisa estar correto
        # 2. cronograma precisa estar correto
        # 3. confiança NÃO pode ser REVISAR
        # ----------------------------------------------------

        confianca_normalizada = (
            str(confianca).strip().upper()
            if confianca is not None
            else ""
        )

        confianca_ok = (
            confianca_normalizada
            in {"ALTA", "MEDIA"}
        )

        if (
            valor_ok
            and cronograma_ok
            and confianca_ok
        ):

            print()
            print("STATUS: PASSOU")

            return {
                "nome": caso["nome"],
                "status": "PASSOU",
            }

        else:

            print()
            print("STATUS: FALHOU")

            if not valor_ok:

                print(
                    "Motivo: valor diferente "
                    "do esperado."
                )

            elif not cronograma_ok:

                print(
                    "Motivo: cronograma diferente "
                    "do esperado."
                )

            elif not confianca_ok:

                print(
                    "Motivo: valor encontrado, "
                    "mas ainda exige revisão manual."
                )

            return {
                "nome": caso["nome"],
                "status": "FALHOU",
            }


    # ========================================================
    # TESTE NEGATIVO
    #
    # O programa NÃO DEVE promover esse caso
    # automaticamente para ALTA ou MEDIA.
    # ========================================================

    elif tipo_teste == "REVISAR":

        valor = resultado.get(
            "valor"
        )

        confianca = resultado.get(
            "confianca"
        )

        tipo_resultado = resultado.get(
            "tipo"
        )

        print(
            "Esperado: REVISÃO MANUAL"
        )

        print(
            f"Tipo obtido: {tipo_resultado}"
        )

        print(
            f"Candidato: {formatar_reais(valor)}"
        )

        print(
            f"Confiança: {confianca}"
        )

        confianca_normalizada = (
            str(confianca).strip().upper()
            if confianca is not None
            else ""
        )

        # ----------------------------------------------------
        # PASSA se NÃO for ALTA/MEDIA
        # ----------------------------------------------------

        if confianca_normalizada not in {
            "ALTA",
            "MEDIA",
        }:

            print()
            print("STATUS: PASSOU")

            print(
                "O sistema corretamente evitou "
                "afirmar um valor principal."
            )

            return {
                "nome": caso["nome"],
                "status": "PASSOU",
            }

        else:

            print()
            print("STATUS: FALHOU")

            print(
                "ATENÇÃO: o sistema promoveu "
                "este caso para confiança automática."
            )

            return {
                "nome": caso["nome"],
                "status": "FALHOU",
            }


    # ========================================================
    # TIPO DESCONHECIDO
    # ========================================================

    else:

        print()

        print(
            "STATUS: TIPO DE TESTE "
            f"DESCONHECIDO ({tipo_teste})"
        )

        return {
            "nome": caso["nome"],
            "status": "ERRO",
        }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)

    print(
        "        TESTE DE REGRESSÃO - "
        "LEITOR DE CONTRATOS"
    )

    print("=" * 70)

    print()

    print(
        f"{len(CASOS_TESTE)} casos cadastrados."
    )

    resultados = []

    for caso in CASOS_TESTE:

        resultado = testar_caso(
            caso
        )

        resultados.append(
            resultado
        )

    # --------------------------------------------------------
    # CONTADORES
    # --------------------------------------------------------

    passou = sum(
        1
        for resultado in resultados
        if resultado["status"] == "PASSOU"
    )

    falhou = sum(
        1
        for resultado in resultados
        if resultado["status"] == "FALHOU"
    )

    nao_achado = sum(
        1
        for resultado in resultados
        if resultado["status"]
        == "ARQUIVO_NAO_ENCONTRADO"
    )

    erros = sum(
        1
        for resultado in resultados
        if resultado["status"] == "ERRO"
    )

    # --------------------------------------------------------
    # RESUMO
    # --------------------------------------------------------

    print()
    print()

    print("=" * 70)
    print("RESUMO DOS TESTES")
    print("=" * 70)

    for resultado in resultados:

        status = resultado["status"]

        if status == "PASSOU":

            simbolo = "[OK]"

        elif status == "FALHOU":

            simbolo = "[FALHA]"

        elif status == "ARQUIVO_NAO_ENCONTRADO":

            simbolo = "[SEM ARQUIVO]"

        else:

            simbolo = "[ERRO]"

        print(
            f"{simbolo:<14} "
            f"{resultado['nome']}"
        )

    print()

    print("-" * 70)

    print(
        f"PASSOU:              {passou}"
    )

    print(
        f"FALHOU:              {falhou}"
    )

    print(
        f"ARQUIVO NÃO ACHADO:  {nao_achado}"
    )

    print(
        f"ERROS:               {erros}"
    )

    print(
        f"TOTAL:                {len(resultados)}"
    )

    print("-" * 70)

    # --------------------------------------------------------
    # RESULTADO FINAL
    # --------------------------------------------------------

    if (
        falhou == 0
        and nao_achado == 0
        and erros == 0
    ):

        print()
        print(
            "TODOS OS TESTES PASSARAM."
        )

        print(
            "Nenhuma regressão foi detectada."
        )

    else:

        print()
        print(
            "ATENÇÃO: existem testes "
            "que ainda não passaram."
        )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    main()