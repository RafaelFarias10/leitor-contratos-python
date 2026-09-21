import re
from pathlib import Path
import pymupdf


PASTA_CONTRATOS = Path("contratos")


# ============================================================
# TERMOS MONETÁRIOS
# ============================================================

TERMOS_POSITIVOS = {
    "valor do aluguel": 30,
    "aluguel mensal": 30,
    "valor total mensal": 30,
    "remuneração mensal": 30,
    "remuneracao mensal": 30,
    "valor mensal": 25,
    "valor adicional mensal": 25,
    "valor adicional mensal de aluguel": 35,
    "valor global do contrato": 35,
    "valor total do contrato": 35,
    "valor total da contratação": 35,
    "valor total da contratacao": 35,
    "preço total": 30,
    "preco total": 30,
    "pelos serviços prestados": 25,
    "pelos servicos prestados": 25,
    "pagará à contratada": 25,
    "pagara a contratada": 25,
    "pagará à locadora": 20,
    "pagara a locadora": 20,
    "remuneração e pagamento": 25,
    "remuneracao e pagamento": 25,
}


TERMOS_NEGATIVOS = {
    "caução": -40,
    "caucao": -40,
    "carta fiança": -45,
    "carta fianca": -45,
    "fiança bancária": -45,
    "fianca bancaria": -45,
    "garantia": -40,
    "título de capitalização": -40,
    "titulo de capitalizacao": -40,
    "capital social": -40,
    "multa": -35,
    "cancelamento": -30,
    "juros": -30,
    "seguro": -25,
    "indenização": -25,
    "indenizacao": -25,
    "desconto": -40,
    "bônus": -35,
    "bonus": -35,
    "retenção": -20,
    "retencao": -20,
    "sinal": -15,
    "entrada": -10,
}


TERMOS_FORTES = [
    "valor do aluguel",
    "aluguel mensal",
    "valor total mensal",
    "remuneração mensal",
    "remuneracao mensal",
    "valor adicional mensal de aluguel",
    "valor global do contrato",
    "valor total do contrato",
    "valor total da contratação",
    "valor total da contratacao",
    "preço total",
    "preco total",
    "pelos serviços prestados",
    "pelos servicos prestados",
    "remuneração e pagamento",
    "remuneracao e pagamento",
]


# ============================================================
# PERCENTUAIS
# ============================================================

PERCENTUAL_POSITIVO = {
    "comissão por intermediação": 35,
    "comissao por intermediacao": 35,
    "comissão da contratada": 30,
    "comissao da contratada": 30,
    "remuneração da contratada": 30,
    "remuneracao da contratada": 30,
    "a título de comissão": 25,
    "a titulo de comissao": 25,
    "comissão": 10,
    "comissao": 10,
}


PERCENTUAL_NEGATIVO = {
    "multa": -45,
    "juros": -45,
    "honorários advocatícios": -50,
    "honorarios advocaticios": -50,
    "medidas judiciais": -45,
    "leiloeiro": -30,
    "arrematantes": -25,
    "reajuste": -30,
    "tributo": -25,
    "imposto": -25,
    "desconto": -30,
    "retenção": -25,
    "retencao": -25,
    "bônus": -30,
    "bonus": -30,
}


# ============================================================
# TABELAS
# ============================================================

EXPRESSOES_TABELA = [
    "tabela de preços",
    "tabela de precos",
    "tabelas de preços",
    "tabelas de precos",
    "tabela de valores",
    "tabela comercial",
]


EXPRESSOES_TABELA_EXTERNA = [
    "termo de condições comerciais",
    "termo de condicoes comerciais",
    "conforme tabela vigente",
    "conforme tabelas vigentes",
    "tabelas de preços e tarifas vigentes",
    "tabelas de precos e tarifas vigentes",
    "tarifas vigentes",
]


# ============================================================
# FUNÇÕES BÁSICAS
# ============================================================

def limpar_texto(texto):
    texto = texto.replace("\xa0", " ")
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def converter_valor(valor):
    texto = (
        valor.upper()
        .replace("R$", "")
        .replace(" ", "")
        .strip()
    )

    try:
        if "," in texto and "." in texto:
            ultima_virgula = texto.rfind(",")
            ultimo_ponto = texto.rfind(".")

            if ultima_virgula > ultimo_ponto:
                texto = texto.replace(".", "")
                texto = texto.replace(",", ".")
            else:
                texto = texto.replace(",", "")

        elif "," in texto:
            texto = texto.replace(".", "")
            texto = texto.replace(",", ".")

        elif "." in texto:
            partes = texto.split(".")

            if len(partes[-1]) == 2:
                texto = texto.replace(",", "")
            else:
                texto = texto.replace(".", "")

        return float(texto)

    except ValueError:
        return 0


def extrair_texto_pdf(caminho_pdf):
    paginas = []

    with pymupdf.open(caminho_pdf) as pdf:
        for numero, pagina in enumerate(pdf, start=1):
            paginas.append({
                "pagina": numero,
                "texto": pagina.get_text("text")
            })

    return paginas


def diagnosticar_pdf(paginas):
    total = sum(
        len(p["texto"].strip())
        for p in paginas
    )

    if total == 0:
        return "SEM_TEXTO"

    if total < 30:
        return "POUCO_TEXTO"

    return "TEXTO_OK"


# ============================================================
# DISTÂNCIA
# ============================================================

def distancia_termo(texto_lower, termo, posicao_valor):
    posicoes = [
        m.start()
        for m in re.finditer(
            re.escape(termo),
            texto_lower
        )
    ]

    if not posicoes:
        return None

    return min(
        abs(pos - posicao_valor)
        for pos in posicoes
    )


def aplicar_termo_por_distancia(
    texto_lower,
    termo,
    pontos,
    posicao_valor,
    motivos
):
    distancia = distancia_termo(
        texto_lower,
        termo,
        posicao_valor
    )

    if distancia is None:
        return 0

    if distancia <= 80:
        motivos.append(
            f"{pontos:+}: {termo} (muito próximo)"
        )
        return pontos

    if distancia <= 150:
        reduzido = int(pontos / 2)

        motivos.append(
            f"{reduzido:+}: {termo} (próximo)"
        )

        return reduzido

    return 0


# ============================================================
# NEGATIVOS COM DIREÇÃO
# ============================================================

def aplicar_termo_negativo_com_direcao(
    texto_lower,
    termo,
    pontos,
    posicao_valor,
    motivos
):
    posicoes = [
        m.start()
        for m in re.finditer(
            re.escape(termo),
            texto_lower
        )
    ]

    if not posicoes:
        return 0

    pos_termo = min(
        posicoes,
        key=lambda p: abs(p - posicao_valor)
    )

    distancia = abs(
        pos_termo - posicao_valor
    )

    if pos_termo < posicao_valor:

        if distancia <= 80:
            motivos.append(
                f"{pontos:+}: {termo} "
                f"(antes do valor)"
            )

            return pontos

        if distancia <= 150:
            reduzido = int(pontos / 2)

            motivos.append(
                f"{reduzido:+}: {termo} "
                f"(antes, próximo)"
            )

            return reduzido

    else:

        if distancia <= 35:
            reduzido = int(pontos / 3)

            motivos.append(
                f"{reduzido:+}: {termo} "
                f"(depois do valor)"
            )

            return reduzido

    return 0


# ============================================================
# GARANTIA
# ============================================================

def contexto_de_garantia(texto, encontrado):
    inicio = max(
        0,
        encontrado.start() - 180
    )

    fim = min(
        len(texto),
        encontrado.end() + 180
    )

    contexto = texto[inicio:fim].lower()

    termos = [
        "carta fiança",
        "carta fianca",
        "fiança bancária",
        "fianca bancaria",
        "caução",
        "caucao",
        "garantia locatícia",
        "garantia locaticia",
        "título de capitalização",
        "titulo de capitalizacao",
    ]

    return any(
        termo in contexto
        for termo in termos
    )


# ============================================================
# SEGURO
# ============================================================

def contexto_de_seguro(texto, encontrado):
    inicio = max(
        0,
        encontrado.start() - 180
    )

    fim = min(
        len(texto),
        encontrado.end() + 80
    )

    contexto = texto[inicio:fim].lower()

    termos_seguro = [
        "valor da cobertura",
        "valor de cobertura",
        "apólice de seguro",
        "apolice de seguro",
        "seguro patrimonial",
        "cobertura securitária",
        "cobertura securitaria",
        "seguradora",
    ]

    return any(
        termo in contexto
        for termo in termos_seguro
    )


# ============================================================
# VALORES MONETÁRIOS
# ============================================================

def procurar_valores(paginas):
    candidatos = []

    padrao = re.compile(
        r"R\$\s*(?:"
        r"\d{1,3}(?:\.\d{3})+,\d{2}"
        r"|"
        r"\d{1,3}(?:,\d{3})+\.\d{2}"
        r"|"
        r"\d+,\d{2}"
        r"|"
        r"\d+\.\d{2}"
        r")",
        re.IGNORECASE
    )

    for pagina in paginas:
        texto = limpar_texto(
            pagina["texto"]
        )

        texto_lower = texto.lower()

        for encontrado in padrao.finditer(texto):
            valor = encontrado.group()

            inicio = max(
                0,
                encontrado.start() - 220
            )

            fim = min(
                len(texto),
                encontrado.end() + 220
            )

            contexto = texto[inicio:fim]

            antes_80 = texto[
                max(0, encontrado.start() - 80):
                encontrado.start()
            ].lower()

            antes_150 = texto[
                max(0, encontrado.start() - 150):
                encontrado.start()
            ].lower()

            antes_180 = texto[
                max(0, encontrado.start() - 180):
                encontrado.start()
            ].lower()

            depois_80 = texto[
                encontrado.end():
                min(
                    len(texto),
                    encontrado.end() + 80
                )
            ].lower()

            depois_150 = texto[
                encontrado.end():
                min(
                    len(texto),
                    encontrado.end() + 150
                )
            ].lower()

            pontuacao = 0
            motivos = []
            termo_forte = False

            # =================================================
            # TERMOS POSITIVOS
            # =================================================

            for termo, pontos in TERMOS_POSITIVOS.items():
                ganho = aplicar_termo_por_distancia(
                    texto_lower,
                    termo,
                    pontos,
                    encontrado.start(),
                    motivos
                )

                pontuacao += ganho

            # =================================================
            # TERMOS NEGATIVOS
            # =================================================

            for termo, pontos in TERMOS_NEGATIVOS.items():
                perda = aplicar_termo_negativo_com_direcao(
                    texto_lower,
                    termo,
                    pontos,
                    encontrado.start(),
                    motivos
                )

                pontuacao += perda

            # =================================================
            # TERMO FORTE
            # =================================================

            for termo in TERMOS_FORTES:
                distancia = distancia_termo(
                    texto_lower,
                    termo,
                    encontrado.start()
                )

                if (
                    distancia is not None
                    and distancia <= 100
                ):
                    termo_forte = True
                    break

            # =================================================
            # LIGAÇÕES CONTRATUAIS
            # =================================================

            padroes_ligacao = [
                (
                    r"aluguel\s+mensal.{0,140}"
                    r"(?:será|sera)\s+de\s*$",
                    "aluguel mensal ... será de",
                    35
                ),
                (
                    r"remunera[cç][aã]o\s+mensal.{0,140}"
                    r"(?:será|sera)\s+de\s*$",
                    "remuneração mensal ... será de",
                    35
                ),
                (
                    r"valor\s+mensal.{0,140}"
                    r"(?:será|sera)\s+de\s*$",
                    "valor mensal ... será de",
                    30
                ),
                (
                    r"aluguel.{0,140}"
                    r"(?:será|sera)\s+de\s*$",
                    "aluguel ... será de",
                    30
                ),
            ]

            for (
                padrao_ligacao,
                descricao,
                pontos
            ) in padroes_ligacao:

                if re.search(
                    padrao_ligacao,
                    antes_180
                ):
                    pontuacao += pontos

                    motivos.append(
                        f"+{pontos}: ligação direta "
                        f"'{descricao}'"
                    )

                    termo_forte = True
                    break

            # =================================================
            # V4.3 - ALUGUEL TOTAL / CONSOLIDADO
            # =================================================
            #
            # Exemplo:
            #
            # "25,00 por m² ... totalizando o aluguel
            # na quantia consolidada de R$ 309.402,75
            # mensais"
            #
            # A regra exige "totalizando" + "aluguel"
            # antes do valor.
            # =================================================

            padrao_aluguel_total = re.search(
                r"totalizando.{0,100}"
                r"aluguel.{0,100}"
                r"(?:quantia|valor|montante)?"
                r".{0,80}$",
                antes_180
            )

            if padrao_aluguel_total:
                pontuacao += 45

                motivos.append(
                    "+45: totalizando o aluguel "
                    "ligado diretamente ao valor"
                )

                termo_forte = True

            # Segunda ordem possível:
            #
            # "aluguel ... totalizando ... R$"

            padrao_aluguel_total_2 = re.search(
                r"aluguel.{0,100}"
                r"totalizando.{0,100}$",
                antes_180
            )

            if (
                padrao_aluguel_total_2
                and not padrao_aluguel_total
            ):
                pontuacao += 40

                motivos.append(
                    "+40: aluguel ... totalizando "
                    "ligado ao valor"
                )

                termo_forte = True

            # =================================================
            # V4.3 - COBRANÇA POR PACOTE MENSAL
            # =================================================
            #
            # Exemplo:
            #
            # "será cobrado o valor de R$ 19.850,00
            # pelo pacote mensal de 2500 consultas"
            #
            # Exigimos informação dos dois lados:
            #
            # ANTES: será cobrado o valor de
            # DEPOIS: pacote mensal
            #
            # Isso é muito mais seguro do que apenas
            # procurar a palavra "mensal".
            # =================================================

            cobranca_antes = re.search(
                r"(?:será|sera)\s+cobrado"
                r".{0,70}"
                r"(?:o\s+)?valor"
                r"(?:\s+de)?\s*$",
                antes_150
            )

            pacote_depois = re.search(
                r"(?:pelo|por|referente\s+ao)?"
                r".{0,50}"
                r"pacote\s+mensal",
                depois_150
            )

            if (
                cobranca_antes
                and pacote_depois
            ):
                pontuacao += 45

                motivos.append(
                    "+45: valor cobrado por "
                    "pacote mensal"
                )

                termo_forte = True

            # =================================================
            # RELAÇÕES DIRETAS
            # =================================================

            if re.search(
                r"totalizando(?:,?\s+portanto)?"
                r"(?:\s+o)?(?:\s+valor)?"
                r"(?:\s+mensal)?(?:\s+de)?\s*$",
                antes_80
            ):
                pontuacao += 30

                motivos.append(
                    "+30: totalizando ligado "
                    "diretamente ao valor"
                )

            if re.search(
                r"valor\s+total(?:\s+de)?\s*$",
                antes_80
            ):
                pontuacao += 30

                motivos.append(
                    "+30: valor total ligado "
                    "diretamente ao R$"
                )

                termo_forte = True

            if re.search(
                r"valor\s+global(?:\s+de)?\s*$",
                antes_80
            ):
                pontuacao += 30

                motivos.append(
                    "+30: valor global ligado "
                    "diretamente ao R$"
                )

                termo_forte = True

            if re.search(
                r"valor\s+mensal(?:\s+de)?\s*$",
                antes_80
            ):
                pontuacao += 25

                motivos.append(
                    "+25: valor mensal ligado "
                    "diretamente ao R$"
                )

                termo_forte = True

            # =================================================
            # FINAL - COMPRA/VENDA: ANEXO COM ITEM ÚNICO
            # =================================================
            #
            # Regra conservadora:
            # 1) o PDF inteiro precisa ter contexto de compra/venda;
            # 2) a página do candidato precisa conter "VALOR UNITÁRIO";
            # 3) essa página precisa ter exatamente um valor em R$;
            # 4) só então o valor unitário pode ser tratado como preço
            #    principal.
            #
            # Isso resolve anexos de venda com um único bem (como VAMOS)
            # sem transformar qualquer valor unitário em valor principal.
            # =================================================

            texto_documento_lower = " ".join(
                limpar_texto(p["texto"]).lower()
                for p in paginas
            )

            contexto_compra_venda_documento = any(
                termo in texto_documento_lower
                for termo in [
                    "venda e compra",
                    "compra e venda",
                    "pedido de venda",
                    "comprador",
                    "vendedor",
                    "aquisição do veículo",
                    "aquisicao do veiculo",
                    "aquisição dos veículos",
                    "aquisicao dos veiculos",
                ]
            )

            pagina_tem_cabecalho_unitario = (
                "valor unitário" in texto_lower
                or "valor unitario" in texto_lower
            )

            valores_na_pagina = re.findall(
                r"R\$\s*(?:"
                r"\d{1,3}(?:\.\d{3})+,\d{2}"
                r"|"
                r"\d{1,3}(?:,\d{3})+\.\d{2}"
                r"|"
                r"\d+,\d{2}"
                r"|"
                r"\d+\.\d{2}"
                r")",
                texto,
                re.IGNORECASE
            )

            compra_item_unico = (
                contexto_compra_venda_documento
                and pagina_tem_cabecalho_unitario
                and len(valores_na_pagina) == 1
            )

            if compra_item_unico:
                pontuacao += 60

                motivos.append(
                    "+60: compra/venda com anexo de item único "
                    "e um único valor monetário na página"
                )

                termo_forte = True

            # =================================================
            # VALORES UNITÁRIOS
            # =================================================

            if (
                not compra_item_unico
                and (
                    "por unidade" in depois_80
                    or "unitário" in antes_80
                    or "unitario" in antes_80
                )
            ):
                pontuacao -= 30

                motivos.append(
                    "-30: valor unitário"
                )

            if (
                "por metro quadrado" in depois_80
                or "/m2" in depois_80
                or "/m²" in depois_80
            ):
                pontuacao -= 30

                motivos.append(
                    "-30: valor por área"
                )

            # =================================================
            # DESCONTO
            # =================================================

            if (
                "desconto de" in antes_80
                or "desconto no valor" in antes_150
            ):
                pontuacao -= 60

                motivos.append(
                    "-60: valor é desconto"
                )

                termo_forte = False

            # =================================================
            # MULTA
            # =================================================

            if re.search(
                r"multa.{0,45}"
                r"(?:no\s+valor\s+de)?\s*$",
                antes_80
            ):
                pontuacao -= 50

                motivos.append(
                    "-50: valor diretamente "
                    "ligado a multa"
                )

                termo_forte = False

            # =================================================
            # BÔNUS
            # =================================================

            if (
                "bônus" in antes_80
                or "bonus" in antes_80
            ):
                pontuacao -= 50

                motivos.append(
                    "-50: valor diretamente "
                    "ligado a bônus"
                )

                termo_forte = False

            if (
                "limitado à" in antes_80
                or "limitado a" in antes_80
            ):
                pontuacao -= 35

                motivos.append(
                    "-35: valor representa limite"
                )

            # =================================================
            # SEGURO
            # =================================================

            seguro_detectado = contexto_de_seguro(
                texto,
                encontrado
            )

            if seguro_detectado:
                pontuacao -= 90

                motivos.append(
                    "-90: valor relacionado a "
                    "seguro/cobertura"
                )

                termo_forte = False

            # =================================================
            # GARANTIA
            # =================================================

            garantia = contexto_de_garantia(
                texto,
                encontrado
            )

            if garantia:
                pontuacao -= 80

                motivos.append(
                    "-80: contexto de "
                    "garantia/carta-fiança"
                )

                termo_forte = False

            candidatos.append({
                "valor": valor,
                "valor_numerico": converter_valor(
                    valor
                ),
                "pagina": pagina["pagina"],
                "contexto": contexto,
                "pontuacao": pontuacao,
                "motivos": motivos,
                "termo_forte": termo_forte,
                "garantia": garantia,
                "seguro": seguro_detectado,
            })

    return candidatos


# ============================================================
# PERCENTUAIS
# ============================================================

def procurar_percentuais(paginas):
    candidatos = []

    padrao = re.compile(
        r"\b\d{1,3}(?:[.,]\d+)?\s*%",
        re.IGNORECASE
    )

    for pagina in paginas:
        texto = limpar_texto(
            pagina["texto"]
        )

        texto_lower = texto.lower()

        for encontrado in padrao.finditer(texto):
            percentual = encontrado.group()

            inicio = max(
                0,
                encontrado.start() - 180
            )

            fim = min(
                len(texto),
                encontrado.end() + 220
            )

            contexto = texto[inicio:fim]

            pontuacao = 0
            motivos = []

            for termo, pontos in PERCENTUAL_POSITIVO.items():
                ganho = aplicar_termo_por_distancia(
                    texto_lower,
                    termo,
                    pontos,
                    encontrado.start(),
                    motivos
                )

                pontuacao += ganho

            for termo, pontos in PERCENTUAL_NEGATIVO.items():
                perda = aplicar_termo_negativo_com_direcao(
                    texto_lower,
                    termo,
                    pontos,
                    encontrado.start(),
                    motivos
                )

                pontuacao += perda

            candidatos.append({
                "percentual": percentual,
                "pagina": pagina["pagina"],
                "contexto": contexto,
                "pontuacao": pontuacao,
                "motivos": motivos
            })

    candidatos.sort(
        key=lambda x: x["pontuacao"],
        reverse=True
    )

    return candidatos


# ============================================================
# CRONOGRAMA
# ============================================================

def detectar_cronograma_percentual(paginas):
    padrao = re.compile(
        r"\b\d{1,3}(?:[.,]\d+)?\s*%"
    )

    termos_etapa = [
        "no início",
        "no inicio",
        "na conclusão",
        "na conclusao",
        "após homologação",
        "apos homologacao",
        "após o go-live",
        "apos o go-live",
        "go-live",
        "go live",
        "parcela",
        "forma de pagamento",
        "fluxo de",
    ]

    for pagina in paginas:
        texto = limpar_texto(
            pagina["texto"]
        )

        lower = texto.lower()

        percentuais = padrao.findall(
            texto
        )

        sinais = sum(
            1
            for termo in termos_etapa
            if termo in lower
        )

        if (
            len(percentuais) >= 3
            and sinais >= 2
        ):
            return {
                "pagina": pagina["pagina"],
                "percentuais": percentuais
            }

    return None


# ============================================================
# VALOR BASE DO CRONOGRAMA
# ============================================================

def procurar_valor_base_cronograma(paginas):
    padroes = [
        re.compile(
            r"calculad[oa]\s+sobre\s+o\s+total\s+de\s+"
            r"(R\$\s*(?:"
            r"\d{1,3}(?:\.\d{3})+,\d{2}"
            r"|"
            r"\d{1,3}(?:,\d{3})+\.\d{2}"
            r"|"
            r"\d+,\d{2}"
            r"|"
            r"\d+\.\d{2}"
            r"))",
            re.IGNORECASE
        ),

        re.compile(
            r"total\s+de\s+"
            r"(R\$\s*(?:"
            r"\d{1,3}(?:\.\d{3})+,\d{2}"
            r"|"
            r"\d{1,3}(?:,\d{3})+\.\d{2}"
            r"|"
            r"\d+,\d{2}"
            r"|"
            r"\d+\.\d{2}"
            r"))",
            re.IGNORECASE
        ),
    ]

    for pagina in paginas:
        texto = limpar_texto(
            pagina["texto"]
        )

        for padrao in padroes:
            resultado = padrao.search(
                texto
            )

            if resultado:
                valor = resultado.group(1)

                inicio = max(
                    0,
                    resultado.start() - 180
                )

                fim = min(
                    len(texto),
                    resultado.end() + 180
                )

                return {
                    "valor": valor,
                    "valor_numerico": converter_valor(
                        valor
                    ),
                    "pagina": pagina["pagina"],
                    "contexto": texto[inicio:fim]
                }

    return None


# ============================================================
# TABELAS
# ============================================================

def detectar_tabela(paginas):
    for pagina in paginas:
        texto = limpar_texto(
            pagina["texto"]
        )

        lower = texto.lower()

        for expressao in EXPRESSOES_TABELA:
            pos = lower.find(
                expressao
            )

            if pos != -1:
                trecho = texto[
                    max(0, pos - 150):
                    min(len(texto), pos + 650)
                ]

                quantidade = len(
                    re.findall(
                        r"R\$\s*\d",
                        trecho,
                        re.IGNORECASE
                    )
                )

                if quantidade >= 2:
                    return {
                        "tipo": "TABELA_INTERNA",
                        "pagina": pagina["pagina"],
                        "contexto": trecho
                    }

        for expressao in EXPRESSOES_TABELA_EXTERNA:
            pos = lower.find(
                expressao
            )

            if pos != -1:
                trecho = texto[
                    max(0, pos - 180):
                    min(len(texto), pos + 500)
                ]

                return {
                    "tipo": "TABELA_EXTERNA",
                    "pagina": pagina["pagina"],
                    "contexto": trecho
                }

    return None


# ============================================================
# CLASSIFICAÇÃO
# ============================================================

def classificar_valor(candidatos):
    if not candidatos:
        return "NAO_ENCONTRADO", None

    candidatos_validos = [
        c
        for c in candidatos
        if (
            not c["garantia"]
            and not c["seguro"]
        )
    ]

    if not candidatos_validos:
        candidatos_validos = candidatos

    ordenados = sorted(
        candidatos_validos,
        key=lambda x: (
            x["pontuacao"],
            x["termo_forte"],
            x["valor_numerico"]
        ),
        reverse=True
    )

    melhor = ordenados[0]

    if (
        melhor["termo_forte"]
        and melhor["pontuacao"] >= 20
    ):
        return "ALTA", melhor

    if melhor["pontuacao"] >= 25:
        return "MEDIA", melhor

    return "REVISAR", melhor


# ============================================================
# EXIBIÇÃO
# ============================================================

def mostrar_valor(candidato):
    print(
        f"Valor: {candidato['valor']}"
    )

    print(
        f"Página: {candidato['pagina']}"
    )

    print("\nTrecho:")
    print(
        candidato["contexto"]
    )

    print(
        "\nPontuação:",
        candidato["pontuacao"]
    )

    if candidato["motivos"]:
        print("Motivos:")

        for motivo in candidato["motivos"]:
            print(
                "  ",
                motivo
            )


def mostrar_percentual(candidato):
    print(
        f"Percentual: "
        f"{candidato['percentual']}"
    )

    print(
        f"Página: "
        f"{candidato['pagina']}"
    )

    print("\nTrecho:")
    print(
        candidato["contexto"]
    )

    print(
        "\nPontuação:",
        candidato["pontuacao"]
    )

    if candidato["motivos"]:
        print("Motivos:")

        for motivo in candidato["motivos"]:
            print(
                "  ",
                motivo
            )


# ============================================================
# ANÁLISE
# ============================================================

def analisar_contrato(caminho):
    print(
        "\n" + "=" * 70
    )

    print(
        f"ANALISANDO: {caminho.name}"
    )

    print(
        "=" * 70
    )

    paginas = extrair_texto_pdf(
        caminho
    )

    diagnostico = diagnosticar_pdf(
        paginas
    )

    if diagnostico == "SEM_TEXTO":
        print(
            "\nPDF SEM TEXTO EXTRAÍVEL."
        )

        print(
            "Provavelmente é um documento "
            "escaneado."
        )

        print(
            "Necessário OCR ou "
            "conferência manual."
        )

        return

    valores = procurar_valores(
        paginas
    )

    percentuais = procurar_percentuais(
        paginas
    )

    cronograma = detectar_cronograma_percentual(
        paginas
    )

    valor_cronograma = None

    if cronograma:
        valor_cronograma = (
            procurar_valor_base_cronograma(
                paginas
            )
        )

    tabela = detectar_tabela(
        paginas
    )

    classificacao, melhor_valor = (
        classificar_valor(
            valores
        )
    )

    melhor_percentual = (
        percentuais[0]
        if percentuais
        else None
    )

    # ========================================================
    # CRONOGRAMA + VALOR
    # ========================================================

    if (
        cronograma
        and valor_cronograma
    ):
        print(
            "\nVALOR PRINCIPAL IDENTIFICADO"
        )

        print("-" * 70)

        print(
            "Tipo: VALOR MONETÁRIO "
            "+ CRONOGRAMA DE PAGAMENTO"
        )

        print(
            f"Valor: "
            f"{valor_cronograma['valor']}"
        )

        print(
            f"Página: "
            f"{valor_cronograma['pagina']}"
        )

        print("\nTrecho:")

        print(
            valor_cronograma["contexto"]
        )

        print(
            "\nForma de pagamento:"
        )

        print(
            ", ".join(
                cronograma["percentuais"]
            )
        )

        print(
            "\nConfiança: ALTA"
        )

        return

    # ========================================================
    # VALOR MONETÁRIO
    # ========================================================

    if classificacao in [
        "ALTA",
        "MEDIA"
    ]:
        print(
            "\nVALOR PRINCIPAL IDENTIFICADO"
        )

        print("-" * 70)

        print(
            "Tipo: VALOR MONETÁRIO"
        )

        mostrar_valor(
            melhor_valor
        )

        print(
            f"\nConfiança: "
            f"{classificacao}"
        )

        if cronograma:
            print(
                "\nForma de pagamento:"
            )

            print(
                ", ".join(
                    cronograma["percentuais"]
                )
            )

        return

    # ========================================================
    # PERCENTUAL
    # ========================================================

    if (
        melhor_percentual
        and melhor_percentual["pontuacao"] >= 25
        and cronograma is None
    ):
        print(
            "\nREMUNERAÇÃO PRINCIPAL "
            "IDENTIFICADA"
        )

        print("-" * 70)

        print(
            "Tipo: PERCENTUAL"
        )

        mostrar_percentual(
            melhor_percentual
        )

        print(
            "\nConfiança: ALTA"
        )

        return

    # ========================================================
    # TABELA INTERNA
    # ========================================================

    if (
        tabela
        and tabela["tipo"]
        == "TABELA_INTERNA"
    ):
        print(
            "\nFORMA DE COBRANÇA IDENTIFICADA"
        )

        print("-" * 70)

        print(
            "Tipo: TABELA DE PREÇOS"
        )

        print(
            f"Página: "
            f"{tabela['pagina']}"
        )

        print(
            "\nO próprio PDF contém "
            "múltiplos preços."
        )

        print("\nTrecho:")

        print(
            tabela["contexto"]
        )

        return

    # ========================================================
    # TABELA EXTERNA
    # ========================================================

    if (
        tabela
        and tabela["tipo"]
        == "TABELA_EXTERNA"
    ):
        print(
            "\nVALOR NÃO DEFINIDO "
            "DIRETAMENTE NO CONTRATO"
        )

        print("-" * 70)

        print(
            "Tipo: TABELA / TARIFA EXTERNA"
        )

        print(
            f"Página: "
            f"{tabela['pagina']}"
        )

        print(
            "\nO valor depende de tabela, "
            "tarifa ou documento complementar."
        )

        print("\nTrecho:")

        print(
            tabela["contexto"]
        )

        return

    # ========================================================
    # CRONOGRAMA SEM TOTAL
    # ========================================================

    if cronograma:
        print(
            "\nCRONOGRAMA DE PAGAMENTO "
            "IDENTIFICADO"
        )

        print("-" * 70)

        print(
            "Percentuais:"
        )

        print(
            ", ".join(
                cronograma["percentuais"]
            )
        )

        print(
            "\nOs percentuais parecem "
            "representar etapas de pagamento."
        )

        print(
            "\n>>> REVISAR VALOR TOTAL <<<"
        )

        return

    # ========================================================
    # CANDIDATO INCERTO
    # ========================================================

    if melhor_valor:
        print(
            "\n" + "!" * 70
        )

        print(
            "NÃO FOI POSSÍVEL IDENTIFICAR "
            "O VALOR PRINCIPAL COM SEGURANÇA."
        )

        print(
            "!" * 70
        )

        print(
            "\nPossível candidato:"
        )

        mostrar_valor(
            melhor_valor
        )

        print(
            "\n>>> RECOMENDA-SE "
            "CONFERÊNCIA MANUAL <<<"
        )

        return

    print(
        "\nNÃO FOI POSSÍVEL IDENTIFICAR "
        "A FORMA DE REMUNERAÇÃO."
    )

    print(
        "\nNenhuma evidência suficientemente "
        "segura foi encontrada."
    )

    print(
        "\n>>> RECOMENDA-SE "
        "CONFERÊNCIA MANUAL <<<"
    )


# ============================================================
# MAIN
# ============================================================

def main():
    print(
        "=" * 70
    )

    print(
        "             LEITOR DE CONTRATOS - VERSÃO FINAL 1.0"
    )

    print(
        "=" * 70
    )

    if not PASTA_CONTRATOS.exists():
        PASTA_CONTRATOS.mkdir()

        print(
            "\nPasta 'contratos' criada."
        )

        print(
            "Coloque os PDFs nela "
            "e execute novamente."
        )

        return

    arquivos = sorted(
        PASTA_CONTRATOS.glob(
            "*.pdf"
        )
    )

    if not arquivos:
        print(
            "\nNenhum PDF encontrado."
        )

        return

    print(
        f"\n{len(arquivos)} contrato(s) "
        "encontrado(s)."
    )

    for arquivo in arquivos:
        try:
            analisar_contrato(
                arquivo
            )

        except Exception as erro:
            print(
                f"\nERRO ao analisar "
                f"{arquivo.name}:"
            )

            print(
                erro
            )

    print(
        "\n" + "=" * 70
    )

    print(
        "ANÁLISE FINALIZADA"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()